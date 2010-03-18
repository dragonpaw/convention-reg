from django.contrib import admin
from datetime import datetime

from convention.reg.models import *

class AffiliationOptions(admin.ModelAdmin):
    list_display = ('name', 'tag', 'color')

class MembershipInline(admin.TabularInline):
    model = Membership

class MembershipTypeInline(admin.TabularInline):
    model = MembershipType

class EventOptions(admin.ModelAdmin):
    inlines = (
        MembershipTypeInline,
    )
    readonly_fields = ('slug',) # Django 1.2
    fieldsets = (
        (None, {'fields': (
            'name',  'to_print', 'badge_number',
        ), }),
    )

class MemberOptions(admin.ModelAdmin):
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

    inlines = (
        MembershipInline,
    )

def reprint(modeladmin, request, queryset):
    queryset.update( needs_printed=True, print_timestamp=datetime.now() )
reprint.short_description = 'Mark selected as needing printing'

class MembershipOptions(admin.ModelAdmin):
    raw_id_fields = ('member',)
    search_fields = ('member__name',)
    list_display = (
        'member',
        'badge_number',
        'needs_printed',
        'print_timestamp',
        'event',
        'type',
        'sold_by',
    )
    list_filter = ('needs_printed',)
    actions = [reprint]

admin.site.register(Affiliation, AffiliationOptions)
admin.site.register(PaymentMethod)
admin.site.register(Event, EventOptions)
admin.site.register(Member, MemberOptions)
admin.site.register(Membership, MembershipOptions)
#admin.site.register(MembershipType)