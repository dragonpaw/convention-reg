#!/usr/bin/env python
from datetime import datetime
from collections import defaultdict
from convention.reg.models import MembershipType, Event

def open_events(request):
    return {
        'events': Event.objects.all(),
        #'types': MembershipType.objects.available().select_related('event')
    }
