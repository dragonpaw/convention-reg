from datetime import datetime
from collections import defaultdict
from decimal import Decimal
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required


#from convention.lib.jinja import render, render_to_response
from .decorators import render_template
import forms
from .models import Event, Person, MembershipSold, MembershipType, PaymentMethod, Payment
from .cart import Cart

try:
    selfserve_gateway = settings.LOCAL_SETTINGS.get('selfserve','payment_method')
    SELFSERVE_PAYMENT = PaymentMethod.objects.get(name=selfserve_gateway)
except:
    raise RuntimeError('Self Service payment type in config points to non-existant method: {0}'.format(
        selfserve_gateway
    ))

# Load the appropriate printing module
printing_module_name = settings.LOCAL_SETTINGS.get('printing', 'module')
printing_module_name = 'reg.printing_modules.{0}'.format(printing_module_name)
try:
    __import__(printing_module_name)
    printing = sys.modules[printing_module_name]
except Exception, e:
    raise RuntimeError(
        'Unable to load the specified printing module: {0}: {1}'.format(
            printing_module_name, str(e)
        )
    )

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
def member_report(request, slug=None, public_only=False):
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

@permission_required('reg.print_badges')
def print_pdf(request, pages=None):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=badges.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    w, h = letter

    pending = MembershipSold.objects.to_print()

    current_badge = 1
    page = 1
    for membership in pending:
        for num in range(1, membership.quantity+1):
            # Render the individual badge.
            p.saveState()
            p.translate(*printing.start[current_badge])

            for element in printing.elements(membership, quantity):
                element.render_to_canvas(p)

            p.restoreState()
            membership.needs_printed = False
            membership.print_timestamp = None
            membership.save()

            if current_badge == 10:
                # Have we hit max pages?
                if pages and page == int(pages):
                    break

                p.showPage()
                current_badge = 1
                page += 1
            else:
                current_badge += 1
    p.showPage()
    p.save()

    return response
