from reportlab.lib.units import inch
from reg.printing_modules import Text, Box

# w = width, h = height, fonts come from PDF spec.
# alignments can be 'left', 'right' or 'center'.
# X and Y are based on the BOTTOM left corner of the label!

def elements(membership, quantity):
    """Returns the various elements for this badge.

    Elements must be Text or Box elements from reg.printing_modules.

    """
    elements = list()

    # Colored affiliation bar
    if membership.person.affiliation:
        elements.extend([
            Box(
                x=0.03*inch, y=1.66*inch, w=3.45*inch, h=0.3*inch,
                color=membership.person.affiliation.color
            ),
            Text(
                x=1.75*inch,
                y=1.75*inch,
                font='Helvetica-Bold',
                size=14,
                alignment='center',
                color=membership.person.affiliation.text_color,
                text=membership.person.affiliation.tag,
            ),
        ])

    # Age stripe
    age = membership.person.age_code()
    if age in ('minor', '18'):
        if age == 'minor':
            color = 'red'
        elif age == '18':
            color = 'black'
        elements.append(
            Box(
                x=0.03*inch,
                y=0.03*inch,
                w=0.2*inch,
                h=1.93*inch,
                color=color,
            )
        )
    elif age == 'unknown':
        elements.append(
            Text(
                x=0.35/2.0*inch,
                y=1.75*inch,
                font='Helvetica-Bold',
                size=20,
                alignment='center',
                text='O',
            )
        )

    # Name(s)
    if membership.person.con_name:
        name1 = membership.person.con_name
        name2 = membership.person.name
    else:
        name1 = membership.person.name
        name2 = None

    elements.append(
        Text(
            x=1.75*inch,
            y=.81*inch,
            font='Helvetica-Bold',
            size=18,
            alignment='center',
            text=name1,
        )
    )
    if name2:
        elements.append(
            Text(
                x=1.75*inch,
                y=0.5*inch,
                font='Helvetica',
                size=8,
                alignment='center',
                text=name2
            )
        )

    # Code for type of badge
    if membership.type.code:
        elements.append(
            Text(
                x=0.3*inch,
                y=0.15*inch,
                font='Helvetica-Bold',
                size=20,
                alignment='center',
                text=membership.type.code,
        )
    )

    # City, State
    if membership.person.city:
        if membership.person.country == 'USA':
            city_state = "{0}, {1}".format(membership.person.city, membership.person.state)
        else:
            city_state = "{0}, {1}".format(membership.person.city, membership.person.country)
        elements.append(
            Text(
                x=1.75*inch,
                y=0.37*inch,
                font='Helvetica',
                size=10,
                alignment='center',
                text=city_state
            )
        )

    # Badge #
    elements.append(
        Text(
            x=3.4*inch,
            y=1.75*inch,
            font='Helvetica-Bold',
            size=12,
            alignment='right',
            text=membership.badge_number,
        )
    )

    # Done.
    return elements

per_page = 10
page_width = 8.5*inch
page_height = 11*inch

# Controls positions of each badge on the page
start = {
    1:  (0.75*inch, 8.51*inch),
    2:  (4.25*inch, 8.51*inch),
    3:  (0.75*inch, 6.51*inch),
    4:  (4.25*inch, 6.51*inch),
    5:  (0.75*inch, 4.51*inch),
    6:  (4.25*inch, 4.51*inch),
    7:  (0.75*inch, 2.51*inch),
    8:  (4.25*inch, 2.51*inch),
    9:  (0.75*inch, 0.51*inch),
    10: (4.25*inch, 0.51*inch),
}
