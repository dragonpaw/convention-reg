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

    # Name(s)
    if membership.type.code == 'D': # Dealer.
        name1 = membership.person.con_name
        name2 = membership.person.name
    elif membership.person.con_name:
        name1 = membership.person.con_name
        name2 = None
    else:
        name1 = membership.person.name
        name2 = None

    elements.append(
        Text(
            x=2.0*inch,
            y=0.6*inch,
            font='Times-Bold',
            size=24,
            alignment='center',
            text=name1,
        )
    )
    if name2:
        elements.append(
            Text(
                x=2.0*inch,
                y=0.35*inch,
                font='Times',
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
                font='Times-Bold',
                size=20,
                alignment='left',
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
                x=2.0*inch,
                y=0.2*inch,
                font='Times',
                size=10,
                alignment='center',
                text=city_state
            )
        )

    # Badge #
    elements.append(
        Text(
            x=3.7*inch,
            y=0.15*inch,
            font='Times-Bold',
            size=20,
            alignment='right',
            text=membership.badge_number,
        )
    )

    # Done.
    return elements

per_page = 1
page_width = 4*inch
page_height = 1*inch

# Controls positions of each badge on the page
start = {
    1:  (0, 0),
}
