#!/usr/bin/env python
from jinja2.filters import contextfilter

@contextfilter
def filter_not_in_cart(context, types):
    """Filter a list of types to only those that should be able to be added
    for the current member. This includes checking dependencies, as well as seeing
    if it's already in the cart and not a type that accepts multiples.
    """

    # Has to runtime import, as views calls the parent module that loads this module.
    from convention.reg.views import _get_cart
    cart = _get_cart(context['request'])

    new = list()

    # This is the current member being viewed.
    member = context['member']

    for type in types:
        if member in cart and type in cart[member]:
            if type.in_quantity:
                new.append(type)
            else:
                pass # Don't re-add a non-in_quantity type.
        elif member.memberships.filter(type=type).count():
            if type.in_quantity:
                new.append(type)
            else:
                pass # Don't re-add a non-in_quantity type.
        else:
            if type.requires.count() == 0:
                new.append(type)
            else:
                for r in type.requires.all():
                    if r in cart[member]:
                        new.append(type)
                        break
                    elif member.memberships.filter(type=r).count():
                        new.append(type)
                        break

    return new
