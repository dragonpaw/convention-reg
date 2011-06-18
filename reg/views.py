from datetime import datetime
from collections import defaultdict
from decimal import Decimal
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required


#from convention.lib.jinja import render, render_to_response
from convention.decorators import render_template
from convention.reg import forms
from convention.reg.models import Event, Person, MembershipSold, MembershipType, PaymentMethod, Payment
from convention.reg.pdf import pos, start
from convention.reg.cart import Cart

try:
    selfserve_gateway = settings.LOCAL_SETTINGS.get('selfserve','payment_method')
    SELFSERVE_PAYMENT = PaymentMethod.objects.get(name=selfserve_gateway)
except:
    raise RuntimeError('Self Service payment type in config points to non-existant method: {0}'.format(
        selfserve_gateway
    ))

def _process_member_form(request, person=None):
    if request.method == 'POST':
        if person:
            form = forms.MemberForm(request.POST, instance=person)
        else:
            form = forms.MemberForm(request.POST)
        if form.is_valid():
            form.person = form.save() # Save it into the form so it can be found.
            messages.success(request,'{0} updated.'.format(form.person))
    else:
        if person:
            return forms.MemberForm(instance=person)
        else:
            return forms.MemberForm()

    return form

def _available_types(member, cart):
    available = list()
    for type in MembershipType.objects.available().select_related('event'):
    # For types we are going to buy, or did buy, only show those that
    # can come in multiples. (Assumes dependencies were met already.)
        if cart.has(member, type) or member.memberships.filter(type=type).count():
            if type.in_quantity:
                available.append(type)
            else:
                pass # Don't re-add a non-in_quantity type.
        # Otherwise, check for dependencies.
        else:
            if type.requires.count() == 0:
                available.append(type)
            else:
                for r in type.requires.all():
                    if cart.has(member, r) or member.memberships.filter(type=r).count():
                        available.append(type)
                        break
    return available

def _get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = Cart()
    return request.session['cart']

@permission_required('reg.add_person')
@render_template
def member_add(request):
    form = _process_member_form(request)

    if request.method == 'POST':
        print "POST"
    if form.is_valid():
        print "Valid"
    else:
        print form.errors

    if request.method == 'POST' and form.is_valid():
        return redirect(member_view, form.person.pk)
    else:
        return { 'form': form }


@permission_required('reg.change_person')
@render_template
def member_list(request):
    if 'payment_form' in request.session and request.session['payment_form']:
        payment_form = request.session['payment_form']
    else:
        payment_form = forms.PaymentForm()
    return {
        'people': Person.objects.all(),
        'payment_form': payment_form,
        'cart': _get_cart(request),
    }


@permission_required('reg.change_person')
@render_template
def member_view(request, id):
    person = get_object_or_404(Person, pk=id)
    current = list()
    cart = _get_cart(request)

    memberships = person.memberships.all()
    for m in memberships:
        current.append(m.type)

    form = _process_member_form(request, person)

    if 'payment_form' in request.session and request.session['payment_form']:
        payment_form = request.session['payment_form']
    else:
        payment_form = forms.PaymentForm()

    return {
        'person': person,
        'form': form,
        'payment_form': payment_form,
        'memberships': memberships,
        'current_events': current,
        'cart': cart,
        'available_types': _available_types(person, cart),
        'is_selfserve': False, # used to show a different cart view for self serve.
    }


@permission_required('reg.add_membership')
def cart_remove(request, person_id, type_id):
    person = Person.objects.get(pk=person_id)
    type = MembershipType.objects.get(pk=type_id)

    cart = _get_cart(request)
    cart.remove(person, type)
    request.session['cart'] = cart # Force a save.

    return redirect(request.META['HTTP_REFERER'])


@permission_required('reg.add_membership')
def cart_add(request, person_id=None, type_id=None, qty=1):
    person = Person.objects.get(pk=person_id)
    type = MembershipType.objects.get(pk=type_id)
    qty = int(qty) # If passed in from URL, will be unicode.

    cart = _get_cart(request)
    cart.add(person, type, qty)
    request.session['cart'] = cart # Force a save.

    if 'next' in request.POST:
        return redirect(request.POST['next'])
    else:
        return redirect(request.META['HTTP_REFERER'])


#@permission_required('reg.add_membership')
@transaction.commit_on_success
def checkout(request,is_selfserve=False):
    """Perform a checkout opertion.

    For types that can be in-quantity, if there's already some sold, a new sale
    record will be created, showing the additional quantity. (This is
    intentional so that there will be proper logging.) """

    if is_selfserve:
        form = forms.SelfServePaymentForm(request.POST)
    else:
        form = forms.PaymentForm(request.POST)

    if not form.is_valid():
        transaction.rollback()
        messages.error(request, form.errors)
        request.session['payment_form'] = form
        return redirect(request.META['HTTP_REFERER'])

    cart = _get_cart(request)

    # First, some sanity checks.
    error = False
    for item in cart:
        if item.person.memberships.filter(type=item.type).count() and not item.type.in_quantity:
            messages.error(request, 'That membership has already been sold.')
            error = True
    if error:
        transaction.rollback()
        request.session['payment_form'] = form
        return redirect(request.META['HTTP_REFERER'])

    payment = Payment()
    if not request.user.is_anonymous():
        payment.user = request.user
    if is_selfserve:
        payment.method = SELFSERVE_PAYMENT
        payment.ui_used = 'self'
    else:
        payment.method = form.cleaned_data['method']
        payment.comment = form.cleaned_data['comment']
        payment.ui_used = 'event'
    payment.amount = cart.total
    payment.save()

    if not payment.process(form=form, request=request):
        if payment.error_message:
            messages.error(request, "Payment failed: %s" % payment.error_message)
        else:
            messages.error(request, "Payment failed. (Unknown reason.)")
        payment.delete() # Not all backends can rollback. So delete it too.
        transaction.rollback()
        request.session['payment_form'] = form
        if is_selfserve:
            return redirect(selfserve_index)
        else:
            return redirect(person_view, person.pk)

    for item in cart:
        membership = MembershipSold()
        membership.person = item.person
        membership.type = item.type
        membership.price = item.type.price
        membership.quantity = item.quantity
        membership.payment = payment
        membership.save()

    request.session['cart'] = Cart()
    messages.success(request, "Payment accepted")
    transaction.commit()
    if is_selfserve:
        return redirect(selfserve_index)
    else:
        return redirect(print_pending)


@permission_required('reg.print_badges')
#@render('reg_pending.html')
@render_template
def print_pending(request):
    q = MembershipSold.objects.to_print()
    return { 'objects': q }


#@render('reg_index.html')
@render_template
def index(request):
    return {}


#@render('reg_member_list.html')
@render_template
def report_member(request, slug=None, public_only=False):
    if slug:
        event = Event.objects.get(slug=slug)
    else:
        event = None

    if event:
        q = Person.objects.filter(memberships__type__event=event).distinct()
    else:
        q = Person.objects.all()

    if public_only:
        q = q.filter(public=True)
    else:
        if not request.user.has_perm('reg.change_member'):
            raise Http404

    return {
        'event': event,
        'people': q,
        'is_public': public_only,
    }


#@render('reg_approval_report.html')
@render_template
def approvals_report(request, slug):
    event = Event.objects.get(slug=slug)
    title = event.name

    q = MembershipSold.objects.filter(
        type__event=event,
        type__approval_needed=True,
    )

    return {
        'event': event,
        'objects': q,
    }


#@render('reg_selfserve_index.html')
@render_template
def selfserve_index(request):
    form = forms.SelfServePaymentForm()
    return {
        'cart': _get_cart(request),
        'payment_form': form,
        'is_selfserve': True,
    }


#@render('reg_selfserve_add_email.html')
@render_template
def selfserve_add_email(request):
    if request.method == 'GET':
        return {}
    else:
        email = request.POST['email']
        if not email or '@' not in email:
            messages.error(request, "Please type in an email address.")
            return redirect(selfserve_index)
        try:
            person = Person.objects.get(email=email)
            request.session['selfserve_person'] = person.pk
            return redirect(selfserve_add_membership)
        except Person.DoesNotExist:
            request.session['selfserve_email'] = email
            return redirect(selfserve_add_person)
        except Person.MultipleObjectsReturned:
            messages.error(request, "Unfortunately, multiple accounts have that address, unable to add to cart.")
            return redirect(selfserve_index)


#@render('reg_selfserve_add_person.html')
@render_template
def selfserve_add_person(request):
    if request.method == 'GET':
        form = forms.SelfServeAddMemberForm(
            initial={
                'email': request.session['selfserve_email'],
            }
        )
        return { 'form': form }
    else:
        form = forms.SelfServeAddMemberForm(request.POST)
        if not form.is_valid():
            return { 'form': form }
        else:
            email = form.cleaned_data['email']
            if Person.objects.filter(email=email).count():
                messages.error(request, 'That email is already registered. You may not edit it.')
                return { 'form': form }
            else:
                person = form.save()
                request.session['selfserve_person'] = person.pk
                return redirect(selfserve_add_membership)


#@render('reg_selfserve_add_membership.html')
@render_template
def selfserve_add_membership(request):
    person = Person.objects.get(pk=request.session['selfserve_person'])

    if request.method == 'GET':
        form = forms.SelfServeAddMembershipForm(initial={'person':person.pk})
    else:
        form = forms.SelfServeAddMembershipForm(request.POST)

    if request.method == 'GET' or not form.is_valid():
        return {
            'person': person,
            'form': form,
        }
    else:
        type = MembershipType.objects.get(pk=form.cleaned_data['type'])
        quantity = form.cleaned_data['quantity']

        # Validation
        fail = False
        if not type.in_quantity:
            if MembershipSold.objects.filter(person=person, type=type).count():
                messages.error(request, 'That person already has that membership')
                fail = True
            if quantity > 1:
                messages.error(request, 'Sorry, but you can only buy one of that type per person. If you want to buy multiple memebrships, add them one per email address so we know who everyone is.')
                form.quantity = 1
                fail = True

        if fail:
            return {
                'person': person,
                'form': form,
            }
        else:
            cart = _get_cart(request)
            cart.add(person, type, quantity)
            request.session['cart'] = cart
            messages.success(request,'Membership added to cart.')
            return redirect(selfserve_index)


def selfserve_remove(request,email,type_id):
    person = Person.objects.get(email=email)
    type = MembershipType.objects.get(pk=type_id)

    _cart(request, person, type, 0)
    return redirect(selfserve_index)

def _draw_string(pdf, alignment, x, y, text):
    if alignment == 'left':
        pdf.drawString(x, y, text)
    elif alignment == 'center':
        pdf.drawCentredString(x, y, text)
    elif alignment == 'right':
        pdf.drawRightString(x, y, text)
    else:
        raise ValueError("Alignment not one of 'left', 'right' or 'center': {0}".format(alignment))

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
            _draw_string(
                p,
                pos['affiliation']['alignment'],
                pos['affiliation']['text_x'],
                pos['affiliation']['text_y'],
                m.person.affiliation.tag,
            )

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
            _draw_string(
                p,
                pos['age']['alignment'],
                pos['age']['text_x'],
                pos['age']['text_y'],
               'O'
            )
            #p.drawCentredString(pos['age']['text_x'], pos['age']['text_y'], 'O')

        # Name(s)
        if m.person.con_name:
            name1 = m.person.con_name
            name2 = m.person.name
        else:
            name1 = m.person.name
            name2 = None
        p.setFillColor(colors.black)
        p.setFont(pos['name1']['font'], pos['name1']['font_size'])
        _draw_string(
            p,
            pos['name1']['alignment'],
            pos['name1']['x'],
            pos['name1']['y'],
            name1,
        )
        #p.drawCentredString(pos['name1']['x'], pos['name1']['y'], name1 )
        if name2:
            p.setFont(pos['name2']['font'], pos['name2']['font_size'])
            _draw_string(
                p,
                pos['name2']['alignment'],
                pos['name2']['x'],
                pos['name2']['y'],
                name2,
            )
            #p.drawCentredString(pos['name2']['x'], pos['name2']['y'], name2 )

        # Code for type of badge
        if m.type.code:
            p.setFillColor(colors.black)
            p.setFont(pos['type_code']['font'], pos['type_code']['font_size'])
            _draw_string(
                p,
                pos['type_code']['alignment'],
                pos['type_code']['x'],
                pos['type_code']['y'],
                m.type.code,
            )
            #p.drawString(pos['type_code']['x'], pos['type_code']['y'], m.type.code)

        # City, State
        if m.person.country == 'USA':
            city_state = "{0}, {1}".format(m.person.city, m.person.state)
        else:
            city_state = "{0}, {1}".format(m.person.city, m.person.country)
        p.setFillColor(colors.black)
        p.setFont(pos['city_state']['font'], pos['city_state']['font_size'])
        _draw_string(
            p,
            pos['city_state']['alignment'],
            pos['city_state']['x'],
            pos['city_state']['y'],
            city_state,
        )
        #p.drawCentredString(pos['city_state']['x'], pos['city_state']['y'], city_state)

        # Badge #
        p.setFillColor( tc )
        p.setFont(pos['number']['font'], pos['number']['font_size'])
        _draw_string(
            p,
            pos['number']['alignment'],
            pos['number']['x'],
            pos['number']['y'],
            str(m.badge_number),
        )
        #p.drawRightString(pos['number']['x'], pos['number']['y'], str(m.badge_number))
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
