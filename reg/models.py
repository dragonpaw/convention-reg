from django.db import models
from datetime import date, timedelta
from convention import settings
from reportlab.lib import colors

color_list = colors.getAllNamedColors().keys()
color_list.sort()

COLOR_OPTIONS = [  (x, x) for x in color_list ]

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    badge_number = models.IntegerField("Next badge number", default=0)
    to_print = models.BooleanField("Print the badges for this event.", default=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def next_badge_number(self):
        num = self.badge_number
        self.badge_number += 1
        self.save()
        return num

class Member(models.Model):
    name = models.CharField("Legal name", max_length=100)
    con_name = models.CharField('Badge name', max_length=100, blank=True, help_text="Otherwise will print real name")
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=20, default='USA')
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    affiliation = models.ForeignKey('Affiliation', blank=True, null=True)
    email = models.EmailField('Email Address', blank=True, default='')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def age(self):
        delta = date.today() - self.birth_date
        return delta.days / 365

    def is_adult(self):
        return self.age >= 18

    def is_drinking_age(self):
        return self.age >= 21

    def age_code(self):
        if not self.birth_date:
            return 'unknown'

        age = self.age()
        if age < 18:
            return 'minor'
        elif age < 21:
            return '18'
        else:
            return 'adult'

    def badge_name(self):
        if self.con_name:
            return self.con_name
        else:
            return self.name

class MembershipType(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=20)
    code = models.CharField("Code to put on badges", max_length=3, blank=True, default='')
    sale_start = models.DateTimeField("When to start selling badges")
    sale_end = models.DateTimeField("When to stop selling badges")
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ('event',)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s>' % (self.event, self.name)

    def count(self):
        return self.members.count()

class PaymentMethod(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Affiliation(models.Model):
    name = models.CharField('Description of the group', max_length=40)
    tag = models.CharField('Tag for printing', max_length=10)
    color = models.CharField('Color for background', max_length=40, choices=COLOR_OPTIONS)
    text_color = models.CharField('Color for text', max_length=40, default='black', choices=COLOR_OPTIONS)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class MembershipManager(models.Manager):
    def to_print(self):
        return super(MembershipManager, self).get_query_set().filter(
            needs_printed = True,
            type__event__to_print = True,
        ).order_by(
            'print_timestamp'
        )

class Membership(models.Model):
    member = models.ForeignKey(Member, related_name='memberships')
    type = models.ForeignKey(MembershipType, related_name='members')
    needs_printed = models.BooleanField(default=True)
    sold_by = models.ForeignKey('auth.User', editable=False, null=True)
    badge_number = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=500, blank=True, default='')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod)
    print_timestamp = models.DateTimeField('Time the printing was requested', blank=True, null=True)

    objects = MembershipManager()

    class Meta:
        unique_together = (('member', 'type'),)
        ordering = ('member',)

    def __unicode__(self):
        return '%s: %s' % (self.member, self.type)

    def event(self):
        return self.type.event
