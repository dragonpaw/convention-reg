#!/usr/bin/env python
from coffin import template
from jinja2 import contextfilter
register = template.Library()

@contextfilter
def not_in_cart(context, types):
    """Filter a list of types to only those that should be able to be added
    for the current member. This includes checking dependencies, as well as seeing
    if it's already in the cart and not a type that accepts multiples.
    """

    # Has to runtime import, as views calls the parent module that loads this module.
    from reg.views import _get_cart
    cart = _get_cart(context['request'])

    new = list()

    # This is the current member being viewed.
    member = context['person']

    for type in types:
        # For types we are going to buy, or did buy, only show those that
        # can come in multiples. (Assumes dependencies were met already.)
        if cart[member][type] or member.memberships.filter(type=type).count():
            if type.in_quantity:
                new.append(type)
            else:
                pass # Don't re-add a non-in_quantity type.
        # Otherwise, check for dependencies.
        else:
            if type.requires.count() == 0:
                new.append(type)
            else:
                for r in type.requires.all():
                    if cart[member][r] or member.memberships.filter(type=r).count():
                        new.append(type)
                        break

    return new

register.filter('not_in_cart', not_in_cart)