from django.contrib import admin
from datetime import datetime

from convention.reg.models import *

class AffiliationOptions(admin.ModelAdmin):
    list_display = ('name', 'tag', 'color')


class MembershipInline(admin.TabularInline):
    model = MembershipSold


class MembershipTypeInline(admin.TabularInline):
    model = MembershipType


class EventOptions(admin.ModelAdmin):
    readonly_fields = ('slug',) # Django 1.2
    fieldsets = (
        (None, {'fields': (
            'name',  'to_print', 'badge_number',
        ), }),
    )

    inlines = (
        MembershipTypeInline,
    )


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

    inlines = (
        MembershipInline,
    )


class MembershipTypeOptions(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'approval_needed', 'numbered')
    list_display_links = ('name',)
    list_filter = ('event',)
    ordering = ('event',)


class MembershipSoldOptions(admin.ModelAdmin):

    def reprint(modeladmin, request, queryset):
        queryset.update( needs_printed=True, print_timestamp=datetime.now() )
    reprint.short_description = 'Mark selected as needing printing'

    raw_id_fields = ('member',)
    search_fields = ('member__name',)
    list_display = (
        'member',
        'type',
        'badge_number',
        'needs_printed',
        'sold_by',
        'sold_at',
        'state',
    )
    list_filter = ('needs_printed', 'type', 'state')
    actions = [reprint]


admin.site.register(Affiliation, AffiliationOptions)
admin.site.register(PaymentMethod)
admin.site.register(Event, EventOptions)
admin.site.register(Person, PersonOptions)
#admin.site.register(MembershipType, MembershipTypeOptions)
admin.site.register(MembershipSold, MembershipSoldOptions)
