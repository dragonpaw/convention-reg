from datetime import date, timedelta, datetime
import logging
from reportlab.lib import colors

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

import payment_gateways

color_list = colors.getAllNamedColors().keys()
color_list.sort()
COLOR_OPTIONS = [(x, x) for x in color_list]


# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    badge_number = models.IntegerField("Next badge number", default=1)
    to_print = models.BooleanField("Print the badges for this event", default=True)
    end_date = models.DateField("Date the event ends")
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def next_badge_number(self):
        num = self.badge_number
        self.badge_number += 1
        self.save()
        return num

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)


class Person(models.Model):
    name = models.CharField("Legal name", max_length=100)
    con_name = models.CharField('Badge name', max_length=100, blank=True, help_text="Otherwise will print real name")
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=20, default='USA')
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    affiliation = models.ForeignKey('Affiliation', blank=True, null=True)
    email = models.EmailField('Email Address', blank=True, default='')
    public = models.BooleanField('Publish online?', default=True, help_text="Would you like your name listed in the public directory?")

    class Meta:
        verbose_name_plural = "People"
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/reg/person/{0}'.format(self.pk)

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

    def save(self, *args, **kwargs):
        if self.birth_date and self.birth_date > date.today():
            v = self.birth_date
            v = v.replace(year=v.year-100)
            self.birth_date = v
        super(Person, self).save(*args, **kwargs)


class MembershipTypeManager(models.Manager):
    def available(self, public=False):
        today = date.today()
        qs = super(MembershipTypeManager, self).get_query_set().exclude(
            sale_start__gt=today,
        ).exclude(
            sale_end__lt=today,
        ).exclude(
            event__end_date__lt=today,
        )
        if public:
            qs = qs.filter(approval_needed=False)
        return qs


class MembershipType(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField("Name", max_length=20, help_text="Name of the type of membership: Staff, Full, Saturday, Vendor.")
    code = models.CharField("Code", max_length=3, blank=True, default='')
    sale_start = models.DateField("Sales Start Time", help_text="Staff cannot sell this membership before this date.", blank=True, null=True)
    sale_end = models.DateField("Sales End Time", help_text="Staff cannot sell this membership after this date.", blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    approval_needed = models.BooleanField(default=False, help_text="Requires reg manager approval before will be printed. E.g.: Vendor.")
    requires = models.ManyToManyField('self',
        blank = True, null = True,
        help_text = "Other type to require before can be sold. Use for add-on types such as 'Extra Table' or 'Art Panel'.",
        related_name = 'allows',
        symmetrical = False,
    )
    in_quantity = models.BooleanField('In Quantity?', default=False, help_text="Allow one person to buy multiple. Only really used for add-on types, such as 'Vendor Frontage' or 'Extra Table'")
    numbered = models.BooleanField('Print and number?', default=True, help_text="If unchecked, badges will not be printed. Generally used for add-on types. ")

    # Custom manager so I can see available membership types available.
    objects = MembershipTypeManager()

    class Meta:
        ordering = ('event', 'name',)
        permissions = (
            ("print_badges", "Can view the queue and print the badges."),
        )

    def __unicode__(self):
        return "{0}: {1}".format(self.event.name, self.name)

    def __repr__(self):
        return '<%s: %s>' % (self.event, self.name)

    def count(self):
        return self.members.count()


class PaymentMethod(models.Model):
    GATEWAYS = (
        ('cash', "Cash/Check/Whatever."),
        ('quantum', "Quantum Gateway. (Credit Card/EFT)"),
    )

    name = models.CharField(max_length=20)
    gateway = models.CharField(max_length=20, choices=GATEWAYS, default='cash')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def process(self, payment, form, request):
        func_name = 'process_' + self.gateway
        func = getattr(self, func_name, None)
        if not func:
            raise NotImplementedError('No such processing gateway known: %s' % self.method.gateway)
        return func(payment, form, request)

    def process_cash(self, payment, form, request):
        return True

    def process_quantum(self, payment, form, request):
        log = logging.getLogger('reg.PaymentMethod.process_quantum')

        #def quantum_gateway(login, key, amount, zip, ip, number, month, year, cvv=None, transparent=True, trans_type=None):

        login = settings.LOCAL_SETTINGS.get('quantum_gateway','login')
        key = settings.LOCAL_SETTINGS.get('quantum_gateway','key')

        trans_type = settings.LOCAL_SETTINGS.get('quantum_gateway','transaction_type')

        amount = payment.amount

        ip = request.META['REMOTE_ADDR']

        args = form.cleaned_data.copy()
        args['invoice'] = payment.pk

        if settings.LOCAL_SETTINGS.get('quantum_gateway','use_transparent'):
            args['transparent'] = True
            #number = form.cleaned_data['number']
            #expires = form.cleaned_data['expires']
            #month = expires.month
            #year = expires.year
            #cvv = form.cleaned_data['cvv']
        else:
            args['transparent'] = False
            #number = None
            #month = None
            #year = None
            #cvv = None

        try:
            auth, id = payment_gateways.quantum_gateway(login, key, amount, **args)
            payment.authcode = auth
            payment.transaction_id = id
            payment.identifier = args['number'][-4:]
            payment.save()
            return True
        except payment_gateways.PaymentDeclinedError, e:
            payment.error_message = str(e)
            return False


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
            type__numbered = True,
            state = 'approved',
        ).order_by(
            'print_timestamp'
        )


class MembershipSold(models.Model):
    APPROVAL_CHOICES = (
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('pending', 'Pending'),
    )

    # Basic fields
    person = models.ForeignKey(Person, related_name='memberships')
    type = models.ForeignKey(MembershipType, related_name='members')
    badge_number = models.IntegerField(null=True, blank=True)

    # Payment info
    price = models.DecimalField(max_digits=6, decimal_places=2)
    payment = models.ForeignKey('Payment', related_name='memberships')

    # Printing info
    needs_printed = models.BooleanField(default=True)
    print_timestamp = models.DateTimeField('Time printing was requested', blank=True)

    # Used by complex types
    state = models.CharField(choices=APPROVAL_CHOICES, default='pending', max_length=20)
    quantity = models.IntegerField(default=1)

    # Custom handler
    objects = MembershipManager()

    class Meta:
        verbose_name_plural = 'Sold: Memberships'
        ordering = ('person__name','type__name')
        #unique_together = (('person', 'type'),) # Types with multiple can be sold twice.

    def __unicode__(self):
        return '%s: %s' % (self.person, self.type)

    def save(self, *args, **kwargs):
        if not self.badge_number and self.type.numbered:
            self.badge_number = self.type.event.next_badge_number()

        if not self.type.approval_needed:
            self.state = 'approved'

        if not self.print_timestamp:
            self.print_timestamp = datetime.now()

        super(MembershipSold, self).save(*args, **kwargs)

    @property
    def event(self):
        return self.type.event


class Payment(models.Model):
    UI_CHOICES = (
        ('admin', 'Administrative interface'),
        ('self','Self-Service UI'),
        ('event', 'At-event registration'),
        ('migration', 'Ported over from old transactions.'),
        ('csv', 'Loaded from a CSV file.'),
    )

    user = models.ForeignKey('auth.User', blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    method = models.ForeignKey(PaymentMethod, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ui_used = models.CharField(max_length=20, choices=UI_CHOICES)
    comment = models.CharField(max_length=500, blank=True, default='')
    authcode = models.CharField("Credit card gateway authorization code.", max_length=10, null=True, blank=True)
    transaction_id = models.CharField("Credit card gateway transaction ID.", max_length=10, null=True, blank=True)
    identifier = models.IntegerField("Partial CC #.", null=True, blank=True)

    error_message = None

    def __unicode__(self):
        return "#%d: %s for $%s" % (self.id, self.method, self.amount)

    def process(self, form, request):
        return self.method.process(payment=self, form=form, request=request)
