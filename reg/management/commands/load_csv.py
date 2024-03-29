#!/usr/bin/env python
import csv
from decimal import Decimal
from datetime import datetime
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from reg.models import *

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
            # type_name = args[2]
        except IndexError:
            print "Syntax: load_csv <filename> <event_name> <type_name>"
            sys.exit(1)

        event = Event.objects.get(name=event_name)

        file = csv.DictReader(open(filename))
        for row in file:
            for field in row:
                row[field] = row[field].strip()

            print(repr(row))
            # First, handle making the member.
            if 'FULLNAME' in row:
                full_name = row['FULLNAME']
            else:
                full_name = ' '.join([row['FIRST'], row['LAST']])
            full_name = full_name.strip()

            # Skip blank row.
            # if not full_name:
            #     continue

            try:
                member = Person.objects.get(name=full_name)
            except Person.DoesNotExist:
                member = Person(name=full_name)
                added_members += 1

            member.address = row['ADDRESS']
            member.city = row['CITY']
            member.state = row['STATE']
            member.zip = row['ZIP']
            member.email = row['EMAIL']
            member.phone = row['PHONE']
            # Model defaults to US
            if row['COUNTRY']:
                member.country = row['COUNTRY']
            if 'PUBLIC' in row:
                member.public = 'y' in row['PUBLIC'].lower()

            member.con_name = row['BADGENAME']

            # Done with the member.
            try:
                member.save()
            except:
                print "Unable to save user: {0}".format(full_name)
                raise

            type = MembershipType.objects.get(event=event, code__iexact=row['TYPE'])

            #------------------------------------------------------------------
            # Avoid errors when re-running.
            if MembershipSold.objects.filter(person=member, type=type).count():
                continue

            # Now, handle the membership.
            membership = MembershipSold(person=member, type=type)
            print 'Person: {0}'.format(member)
            added_memberships += 1

            if 'BADGENUM' in row:
                membership.badge_number = row['BADGENUM']
            if 'COMMENT' in row:
                membership.comment = row['COMMENT']

            if 'AMOUNTPAID' in row:
                membership.price = Decimal(row['AMOUNTPAID'].replace('$',''))
            else:
                membership.price = type.price

            if type.in_quantity:
                try:
                    if row['QUANTITY']:
                        membership.quantity = int(row['QUANTITY'])
                    else:
                        membership.quantity = 1
                except:
                    membership.quantity = 1

            if 'HOWPAID' in row:
                how = row['HOWPAID']
            else:
                how = 'CSV load'
            try:
                method = PaymentMethod.objects.get(name=how)
            except PaymentMethod.DoesNotExist:
                method = PaymentMethod(name=how)
                method.save()

            payment = Payment()
            payment.method = method
            payment.ui_used = 'csv'
            payment.amount = membership.price
            payment.save()

            membership.payment = payment
            membership.print_timestamp = now
            membership.save()
        print "Added {0} members, and {1} memberships.".format(
            added_members, added_memberships
        )
