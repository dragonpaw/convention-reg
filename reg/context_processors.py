#!/usr/bin/env python
from datetime import datetime
from collections import defaultdict
from convention.reg.models import MembershipType

def open_events(request):
    now = datetime.now()

    events = defaultdict(list)

    types = MembershipType.objects.select_related('event').filter(
        sale_start__lte=now,
        sale_end__gte=now
    )
    for t in types:
        events[t.event].append(t)
    return { 'events': events }