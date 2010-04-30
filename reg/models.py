from datetime import date, timedelta, datetime
from reportlab.lib import colors

from django.db import models
from django.template.defaultfilters import slugify

from convention import settings

color_list = colors.getAllNamedColors().keys()
color_list.sort()

COLOR_OPTIONS = [  (x, x) for x in color_list ]

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    badge_number = models.IntegerField("Next badge number", default=1)
    to_print = models.BooleanField("Print the badges for this event.", default=True)
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
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=20, default='USA')
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    affiliation = models.ForeignKey('Affiliation', blank=True, null=True)
    email = models.EmailField('Email Address', blank=True, default='')
    public = models.BooleanField('Publish?', default=True)

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
    def available(self):
        today = date.today()
        return super(MembershipTypeManager, self).get_query_set().filter(
            sale_start__lte = today,
            sale_end__gte = today,
        )


class MembershipType(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField("Name", max_length=20, help_text="Name of the type of membership: Staff, Full, Saturday, Vendor.")
    code = models.CharField("Code", max_length=3, blank=True, default='')
    sale_start = models.DateTimeField("Sales Start Time", help_text="Staff cannot sell this membership before this date.")
    sale_end = models.DateTimeField("Sales End Time", help_text="Staff cannot sell this membership after this date.")
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
    member = models.ForeignKey(Person, related_name='memberships')
    type = models.ForeignKey(MembershipType, related_name='members')
    badge_number = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=500, blank=True, default='')

    # Payment info
    price = models.DecimalField(max_digits=6, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, blank=True, null=True)
    sold_by = models.ForeignKey('auth.User', editable=False, null=True)
    sold_at = models.DateTimeField(auto_now_add=True, editable=False)

    # Printing info
    needs_printed = models.BooleanField(default=True)
    print_timestamp = models.DateTimeField('Time printing was requested')

    # Used by complex types
    state = models.CharField(choices=APPROVAL_CHOICES, default='pending', max_length=20)
    quantity = models.IntegerField(default=1)

    # Custom handler
    objects = MembershipManager()

    class Meta:
        verbose_name_plural = 'Sold: Memberships'
        #unique_together = (('member', 'type'),)
        ordering = ('member__name','type__name')

    def __unicode__(self):
        return '%s: %s' % (self.member, self.type)

    @property
    def event(self):
        return self.type.event

    def save(self, *args, **kwargs):
        if not self.badge_number and self.type.numbered:
            self.badge_number = self.type.event.next_badge_number()

        if not self.type.approval_needed:
            self.state = 'approved'

        if not self.print_timestamp:
            self.print_timestamp = datetime.now()

        super(MembershipSold, self).save(*args, **kwargs)
