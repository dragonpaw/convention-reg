from django.contrib import admin
from datetime import datetime

from convention.reg.models import *

class AffiliationOptions(admin.ModelAdmin):
    list_display = ('name', 'tag', 'color')


class MembershipInline(admin.TabularInline):
    model = MembershipSold
    readonly_fields = ('person','payment','price')
    fields = ('person','type','badge_number','price','state','quantity','payment')

class PaymentOptions(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'method', 'amount', 'people')
    search_fields = ('identifier','memberships__person__name')
    
    # Just about everything. Don't need people doctoring the evidence.
    readonly_fields = (
        'user','timestamp','method','amount','ui_used','authcode',
        'transaction_id','identifier'
    )
    
    def people(self, obj):
        return ", ".join([p.person.name for p in obj.memberships.all()])
        
    ordering = ('-timestamp',)
    inlines = (MembershipInline,)


class MembershipTypeInline(admin.TabularInline):
    model = MembershipType


class PaymentMethodOptions(admin.ModelAdmin):
    model = PaymentMethod
    list_display = ('name', 'gateway')


class EventOptions(admin.ModelAdmin):
    readonly_fields = ('slug',) # Django 1.2
    fieldsets = (
        (None, {'fields': (
            'name',  'to_print', 'badge_number',
        ), }),
    )
    inlines = (MembershipTypeInline,)


class PersonOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'name', 'con_name', 'affiliation', 'email', 'birth_date', 'public'
        ), }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip', 'country'),
        }),
    )
    search_fields = ('name', 'con_name', 'email')
    list_display = ('name', 'con_name', 'email', 'affiliation')
    inlines = (MembershipInline,)


class MembershipTypeOptions(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'approval_needed', 'numbered')
    list_display_links = ('name',)
    list_filter = ('event',)
    ordering = ('event',)


class MembershipSoldOptions(admin.ModelAdmin):
    raw_id_fields = ('person',)
    search_fields = ('person__name',)
    list_display = (
        'person',
        'type',
        'badge_number',
        'needs_printed',
        'state',
        'payment',
    )
    fieldsets = (
        (None, {'fields': (
            'person', 'type', 'badge_number', 'quantity', 'state',
        ), }),
        ('Payment Info', {
            'fields': ('price', 'payment', 'needs_printed'),
        }),
    )
    list_filter = ('needs_printed', 'type', 'state')
    readonly_fields = ('person','payment','price')

    def reprint(modeladmin, request, queryset):
        queryset.update( needs_printed=True, print_timestamp=datetime.now() )
    reprint.short_description = 'Mark selected as needing printing'

    actions = [reprint]


admin.site.register(Affiliation, AffiliationOptions)
admin.site.register(PaymentMethod, PaymentMethodOptions)
admin.site.register(Event, EventOptions)
admin.site.register(Person, PersonOptions)
admin.site.register(Payment, PaymentOptions)
#admin.site.register(MembershipType, MembershipTypeOptions)
admin.site.register(MembershipSold, MembershipSoldOptions)
