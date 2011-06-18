"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".
"""

from django.test import TestCase

from datetime import timedelta, datetime
from models import Person, Event, MembershipType
from cart import Cart

class CartTest(TestCase):

    def setUp(self):
        self.cart = Cart()

        self.person = Person.objects.create(
            name = "William Arnold",
            email = "ash@dragonpaw.org",
            con_name = "Ash"
        )

        self.event = Event.objects.create(
            name = "Test Event"
        )

        sale_start = datetime.now() - timedelta(2)
        sale_end = datetime.now() + timedelta(2)

        self.type = MembershipType.objects.create(
            event = self.event,
            name = "Weekend",
            code = "FULL",
            price = 50,
            in_quantity = False,
            sale_start = sale_start,
            sale_end = sale_end,
        )

        self.addon_type = MembershipType.objects.create(
            event = self.event,
            name = "Kid-in-tow",
            price = 20,
            in_quantity = True,
            sale_start = sale_start,
            sale_end = sale_end,
        )
        self.addon_type.requires.add(self.type)

    def runTest(self):
        self.assertEqual(self.cart.total, 0)
        self.assertEqual(self.cart.quantity, 0)
        self.assertEqual(self.cart.items, 0)

        # should only add one.
        self.cart.add(self.person, self.type, 2)
        self.assertEqual(self.cart.quantity, 1)
        self.assertEqual(self.cart.items, 1)
        self.assertEqual(self.cart.total, 50)

        # should not add anything.
        self.cart.add(self.person, self.type, 2)
        self.assertEqual(self.cart.quantity, 1)
        self.assertEqual(self.cart.items, 1)
        self.assertEqual(self.cart.total, 50)

        # Add two of the addon type...
        self.cart.add(self.person, self.addon_type, 2)
        self.assertEqual(self.cart.quantity, 3)
        self.assertEqual(self.cart.items, 2)
        self.assertEqual(self.cart.total, 90)
        
        self.assertEqual(len(self.cart), 2)

        # Remove one addon.
        self.cart.remove(self.person, self.addon_type)
        self.assertEqual(self.cart.quantity, 1)
        self.assertEqual(self.cart.items, 1)
        self.assertEqual(self.cart.total, 50)
