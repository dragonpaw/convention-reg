from datetime import datetime
from collections import defaultdict
from decimal import Decimal
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from convention.lib.jinja import render, render_to_response
from convention.reg.models import Event, Person, MembershipSold, MembershipType, PaymentMethod, Payment
from convention.reg.forms import PaymentForm, MemberForm
from convention.reg.pdf import pos, start

def _process_member_form(request, person=None):
    if request.method == 'POST':
        if person:
            form = MemberForm(request.POST, instance=person)
        else:
            form = MemberForm(request.POST)
        if form.is_valid():
            form.person = form.save() # Save it into the form so it can be found.
    else:
        if person:
            return MemberForm(instance=person)
        else:
            return MemberForm()

    return form


@permission_required('reg.add_person')
@render('reg_member_add.html')
def person_add(request):
    form = _process_member_form(request)

    if request.method == 'POST':
        print "POST"
    if form.is_valid():
        print "Valid"
    else:
        print form.errors

    if request.method == 'POST' and form.is_valid():
        return redirect(person_view, form.person.pk)
    else:
        return { 'form': form }


@permission_required('reg.change_person')
@render('reg_member_list.html')
def people_list(request):
    return { 'members': Person.objects.all() }


@permission_required('reg.change_person')
@render('reg_member_view.html')
def person_view(request, id):
    person = get_object_or_404(Person, pk=id)
    current = list()

    memberships = person.memberships.all()
    for m in memberships:
        current.append(m.type)

    form = _process_member_form(request, person)

    return {
        'person': person,
        'form': form,
        'payment_form': PaymentForm(),
        'memberships': memberships,
        'current_events': current,
    }


def _cart_struct():
    return defaultdict(int)


def _get_cart(request):
    if 'memberships' not in request.session:
        request.session['memberships'] = defaultdict(_cart_struct)
    return request.session['memberships']


def _cart(request, person, type, qty=1):
    """Cart manipulation helper.

    Requires: Person and MembershipType.
    Optional: quantity. Defaults to 1. Pass 0 to delete from cart.

    Quantity over 1 for types that don't accept a quantity is ignored silently.
    """
    cart = _get_cart(request)

    if qty:
        if type.in_quantity:
            cart[person][type] += qty
        else:
            cart[person][type] = 1
    else:
        try:
            del cart[person][type]
        except KeyError:
            pass

    total = Decimal(0)
    for p in cart:
        for t in cart[p]:
            total += (t.price * cart[p][t])
    request.session['total'] = total


def _cart_empty(request):
    del request.session['memberships']
    del request.session['total']


@permission_required('reg.add_membership')
def cart_remove(request, person_id, type_id):
    person = Person.objects.get(pk=person_id)
    type = MembershipType.objects.get(pk=type_id)

    _cart(request, person, type, 0)
    return redirect(person_view, person.pk)


@permission_required('reg.add_membership')
def cart_add(request, person_id, type_id, qty=1):
    person = Person.objects.get(pk=person_id)
    type = MembershipType.objects.get(pk=type_id)
    qty = int(qty) # If passed in from URL, will be unicode.

    _cart(request, person, type, qty)
    return redirect(person_view, person.pk)


@permission_required('reg.add_membership')
#@transaction.commit_manually
def checkout(request):
    """Perform a checkout opertion.

    For types that can be in-quantity, if there's already some sold, a new sale
    record will be created, showing the additional quantity. (This is
    intentional so that there will be proper logging.) """

    form = PaymentForm(request.POST)

    if not form.is_valid():
        transaction.rollback()
        messages.error(request, form.errors)
        return redirect(request.META['HTTP_REFERER'])

    cart = _get_cart(request)

    # First, some sanity checks.
    error = False
    for person in cart:
        for type in cart[person]:
            if cart[person][type] and person.memberships.filter(type=type).count() and not type.in_quantity:
                messages.error(request, 'That membership has already been sold.')
                error = True
    if error:
        transaction.rollback()
        return redirect(request.META['HTTP_REFERER'])

    # OK, now safe to commit.
    total = Decimal(0)
    payment = Payment()
    payment.user = request.user
    payment.method = form.cleaned_data['method']
    payment.comment = form.cleaned_data['comment']
    payment.ui_used = 'event'
    payment.amount = 0 # Will be changed below, but we need to save to link to the memberships.
    payment.save()
    
    for person in cart:
        for type in cart[person]:
            # Comes from the use of defaultdicts.
            if cart[person][type] == 0:
                continue

            membership = MembershipSold()
            membership.person = person
            membership.type = type
            membership.price = type.price * cart[person][type]
            membership.quantity = cart[person][type]
            membership.payment = payment
            membership.save()
            
            total += membership.price
    
    # Update the total.
    payment.amount = total
    payment.save()
    
    if payment.process():
        _cart_empty(request)
        messages.success(request, "Payment accepted")
        transaction.commit()
        return redirect(print_pending)
    else:
        if payment.error_message:
            messages.error(request, "Payment failed: %s" % payment.error_message)
        else:
            messages.error(request, "Payment failed. (Unknown reason.)")
        transaction.rollback()
        return redirect(person_view, person.pk)



@permission_required('reg.print_badges')
@render('reg_pending.html')
def print_pending(request):
    q = MembershipSold.objects.to_print()
    return { 'objects': q }


@render('reg_index.html')
def index(request):
    return {}


@render('reg_member_report.html')
def report_member(request, slug=None, public_only=False):
    if slug:
        event = Event.objects.get(slug=slug)
        title = event.name
    else:
        event = None
        title = "Members"

    if event:
        q = Person.objects.filter(memberships__type__event=event)
    else:
        q = Person.objects.all()

    if public_only:
        q = q.filter(public=True)
        title += "(Public)"
    else:
        if not request.user.has_perm('reg.change_member'):
            raise Http404

    return {
        'title': title,
        'objects': q,
    }


@render('reg_approval_report.html')
def approvals(request, slug):
    event = Event.objects.get(slug=slug)
    title = event.name

    q = MembershipSold.objects.filter(
        type__event=event,
        type__approval_needed=True,
    )
    return {
        'title': title,
        'objects': q,
    }


@permission_required('reg.print_badges')
def print_pdf(request, pages=None):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=badges.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    w, h = letter

    pending = MembershipSold.objects.to_print()

    x = 1
    page = 1
    for m in pending:

        # Render the individual badge.
        p.saveState()
        p.translate(*start[x])

        # Colored affiliation bar
        tc = colors.toColor('black')
        if m.person.affiliation:
            c = colors.toColor(str(m.person.affiliation.color))
            tc = colors.toColor(str(m.person.affiliation.text_color))
            p.setFillColor( c )
            p.rect(
                pos['affiliation']['x'],
                pos['affiliation']['y'],
                pos['affiliation']['w'],
                pos['affiliation']['h'],
                fill=True, stroke=False)
            p.setFillColor( tc )
            p.setFont(pos['affiliation']['font'], pos['affiliation']['font_size'])
            p.drawCentredString(pos['affiliation']['text_x'],
                                pos['affiliation']['text_y'],
                                m.person.affiliation.tag)

        # Age stripe
        age = m.person.age_code()
        if age in ('minor', '18'):
            if age == 'minor':
                p.setFillColor(colors.red)
            elif age == '18':
                p.setFillColor(colors.black)
            p.rect(pos['age']['x'], pos['age']['y'],
                   pos['age']['w'], pos['age']['h'],
                   stroke=False, fill=True)
        elif age == 'unknown':
            p.setFillColor(colors.black)
            p.setFont(pos['age']['font'], pos['age']['font_size'])
            p.drawCentredString(pos['age']['text_x'], pos['age']['text_y'], 'O')

        # Name(s)
        if m.person.con_name:
            name1 = m.person.con_name
            name2 = m.person.name
        else:
            name1 = m.person.name
            name2 = None
        p.setFillColor(colors.black)
        p.setFont(pos['name1']['font'], pos['name1']['font_size'])
        p.drawCentredString(pos['name1']['x'], pos['name1']['y'], name1 )
        if name2:
            p.setFont(pos['name2']['font'], pos['name2']['font_size'])
            p.drawCentredString(pos['name2']['x'], pos['name2']['y'], name2 )

        # Code for type of badge
        if m.type.code:
            p.setFillColor(colors.black)
            p.setFont(pos['type_code']['font'], pos['type_code']['font_size'])
            p.drawString(pos['type_code']['x'], pos['type_code']['y'], m.type.code)

        # City, State
        if m.person.country == 'USA':
            city_state = "{0}, {1}".format(m.person.city, m.person.state)
        else:
            city_state = "{0}, {1}".format(m.person.city, m.person.country)
        p.setFillColor(colors.black)
        p.setFont(pos['city_state']['font'], pos['city_state']['font_size'])
        p.drawCentredString(pos['city_state']['x'], pos['city_state']['y'], city_state)

        # Badge #
        p.setFillColor( tc )
        p.setFont(pos['number']['font'], pos['number']['font_size'])
        p.drawRightString(pos['number']['x'], pos['number']['y'], str(m.badge_number))
        p.setFillColor(colors.black)

        p.restoreState()
        m.needs_printed = False
        m.print_timestamp = None
        m.save()

        if x == 10:
            # Have we hit max pages?
            if pages and page == int(pages):
                break

            p.showPage()
            x = 1
            page += 1
        else:
            x += 1
    p.showPage()
    p.save()

    return response
