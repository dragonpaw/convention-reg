from datetime import datetime
from collections import defaultdict
from django.shortcuts import redirect
from django.http import HttpResponse
from math import ceil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


from convention.lib.jinja import render, render_to_response
from convention.reg.models import Event, Member, Membership, MembershipType
from convention.reg.forms import MemberForm, MembershipForm
from convention.reg.pdf import pos, start

def _process_member_form(request, member=None):
    if request.method != 'POST':
        if member:
            return MemberForm(instance=member)
        else:
            return MemberForm()
    else:
        if not member:
            member = Member()

    form = MemberForm(request.POST)
    if not form.is_valid():
        return form

    member.name = form.cleaned_data['name']
    member.con_name = form.cleaned_data['con_name']
    member.address = form.cleaned_data['address']
    member.city = form.cleaned_data['city']
    member.state = form.cleaned_data['state']
    member.zip = form.cleaned_data['zip']
    member.phone = form.cleaned_data['phone']
    member.country = form.cleaned_data['country']
    member.affiliation = form.cleaned_data['affiliation']
    member.birth_date = form.cleaned_data['birth_date']
    member.save()
    form.member = member

    return form

def member_add(request):
    form = _process_member_form(request)

    if request.method == 'POST':
        print "POST"
    if form.is_valid():
        print "Valid"
    else:
        print form.errors

    if request.method == 'POST' and form.is_valid():
        return redirect(member_view, form.member.pk)
    else:
        return render_to_response('reg_member_add.html',
                                  { 'form': form },
                                  request)

@render('reg_member_list.html')
def member_list(request):
    return { 'members': Member.objects.all() }

@render('reg_member_view.html')
def member_view(request, id):
    member = Member.objects.get(pk=id)
    current = list()

    memberships = member.memberships.all()
    for m in memberships:
        current.append(m.type)

    form = _process_member_form(request, member)

    return {
        'member': member,
        'form': form,
        'reg_form': MembershipForm(initial={'member':member.pk}),
        'memberships': memberships,
        'current_events': current,
    }

def membership_add(request):
    form = MembershipForm(request.POST)

    if not form.is_valid():
        return render_to_response('error.html',
                                  {'error':  form.errors},
                                  request )

    member = Member.objects.get(pk=request.POST['member_id'])
    type = form.cleaned_data['type']
    if member.memberships.filter(type=type).count():
        return render_to_response('error.html',
                                  { 'error': 'That membership has already been sold.'},
                                  request)

    membership = Membership()
    membership.member = member
    membership.type = type
    membership.price = membership.type.price
    membership.payment_method = form.cleaned_data['payment_method']
    membership.print_timestamp = datetime.now()
    membership.save()

    return redirect(member_view, member.pk)

@render('reg_pending.html')
def print_pending(request):
    q = Membership.objects.to_print()
    return { 'objects': q }

@render('reg_index.html')
def index(request):
    return {}

def print_pdf(request, pages=None):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=badges.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    w, h = letter

    pending = Membership.objects.to_print()

    x = 1
    page = 1
    for m in pending:

        # If it's blank, assign the next badge number to it.
        if not m.badge_number:
            e = m.type.event
            e.badge_number += 1
            m.badge_number = e.badge_number
            e.save()
            m.save()

        # Render the individual badge.
        p.saveState()
        p.translate(*start[x])

        # Colored affiliation bar
        tc = colors.toColor('black')
        if m.member.affiliation:
            c = colors.toColor(str(m.member.affiliation.color))
            tc = colors.toColor(str(m.member.affiliation.text_color))
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
                                m.member.affiliation.tag)

        # Age stripe
        age = m.member.age_code()
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
        if m.member.con_name:
            name1 = m.member.con_name
            name2 = m.member.name
        else:
            name1 = m.member.name
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
        if m.member.country == 'USA':
            city_state = "{0}, {1}".format(m.member.city, m.member.state)
        else:
            city_state = "{0}, {1}".format(m.member.city, m.member.country)
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
