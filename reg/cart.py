'''Simple cart object to save and restore from the session.'''
from collections import defaultdict
from decimal import Decimal

class CartItem(object):
    def __init__(self, type, person):
        self.type = type
        self.person = person
        self._quantity = 0

    @property
    def price(self):
        return self.type.price * self.quantity

    def set_quantity(self, quantity):
        if self.type.in_quantity:
            self._quantity = quantity
        else:
            self._quantity = 1
    def get_quantity(self):
        return self._quantity
    quantity = property(get_quantity, set_quantity)


class Cart(object):
    def __init__(self):
        self._cart_empty()

    def __iter__(self):
        return self._cart.values().__iter__()

    def __len__(self):
        return len(self._cart)

    def _recalculate(self):
        self.items = 0
        self.quantity = 0
        self.total = Decimal(0)
        for item in self._cart.values():
            self.items += 1
            self.quantity += item.quantity
            self.total += item.price

    def _cart_empty(self):
        self._cart = dict()
        self._recalculate()

    def key(self, person, type):
        return "{0}-{1}".format(type.pk, person.pk)

    def has(self, person, type):
        return self.key(person, type) in self._cart

    def add(self, person, type, qty=1):
        """Add an item to a cart.

        Requires: Person and MembershipType.
        Optional: quantity. Defaults to 1.
        Quantity over 1 for types that don't accept a quantity is ignored silently.
        """

        key = self.key(person, type)
        if key in self._cart:
            self._cart[key].quantity += qty
        else:
            item = CartItem(type, person)
            item.quantity = qty
            self._cart[key] = item
        self._recalculate()

    def remove(self, person, type):
        key = self.key(person, type)
        try:
            del self._cart[key]
        except KeyError:
            pass
        self._recalculate()

