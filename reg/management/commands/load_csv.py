#!/usr/bin/env python
import csv
from decimal import Decimal
from datetime import datetime
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from convention.reg.models import Person, MembershipSold, MembershipType, Event, PaymentMethod

#0BADGENUM,1FULLNAME,2FIRSTNAME,3LASTNAME,4ADDRESS,5CITY,6STATE,7ZIP,8PHONE,
#9COUNTRY,10EMAIL,11ENTRYDATE,12BADGENAME,13COMMENTS,14AMOUNTPAID,15HOWPAID,16COMMENTS2
class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):

        added_members = 0
        added_memberships = 0
        now = datetime.now()

        try:
            filename = args[0]
            event_name = args[1]
            type_name = args[2]
        except IndexError:
            print "Syntax: load_csv <filename> <event_name> <type_name>"
            sys.exit(1)

        event = Event.objects.get(name=event_name)
        type = MembershipType.objects.get(event=event, name=type_name)

        file = csv.DictReader(open(filename))
        for rows in file:

            # First, handle making the member.
            full_name = rows['FULLNAME']

            # Skip blank rows.
            if not full_name:
                continue

            try:
                member = Person.objects.get(name=full_name)
            except Person.DoesNotExist:
                member = Person(name=full_name)
                added_members += 1

            member.address = rows['ADDRESS']
            member.city = rows['CITY']
            member.state = rows['STATE']
            member.zip = rows['ZIP']
            member.email = rows['EMAIL']
            member.phone = rows['PHONE']
            # Model defaults to US
            if rows['COUNTRY']:
                member.country = rows['COUNTRY']

            member.con_name = rows['BADGENAME']

            # Done with the member.
            try:
                member.save()
            except:
                print "Unable to save user: {0}".format(full_name)
                raise

            #------------------------------------------------------------------
            # Avoid errors when re-running.
            if MembershipSold.objects.filter(member=member, type=type).count():
                continue

            # Now, handle the membership.
            membership = MembershipSold(member=member, type=type)
            print 'Person: {0}'.format(member)
            added_memberships += 1

            membership.badge_number = rows['BADGENUM']
            membership.comment = rows['COMMENTS']

            if rows['AMOUNTPAID']:
                membership.price = Decimal(rows['AMOUNTPAID'].replace('$',''))
            else:
                membership.price = 0

            try:
                method = PaymentMethod.objects.get(name=rows['HOWPAID'])
            except PaymentMethod.DoesNotExist:
                method = PaymentMethod(name=rows['HOWPAID'])
                method.save()
            membership.payment_method = method

            membership.print_timestamp = now
            membership.save()
        print "Added {0} members, and {1} memberships.".format(added_members, added_memberships)
