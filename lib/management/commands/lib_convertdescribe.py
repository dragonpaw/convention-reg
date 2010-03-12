#!/usr/bin/env python
from django.core.management.base import BaseCommand
import sys
import re

subs = (
    (r' varchar2\((\d+) byte\),', r' = models.CharField(max_length=\1, null=True, blank=True)'),
    (r' varchar2\((\d+) byte\) not null,', r' = models.CharField(max_length=\1)'),
    (r' date,', r' = models.DateTimeField(null=True, blank=True)'),
    (r' date not null,', r' = models.DateTimeField()'),
    (r' number,', r' = models.IntegerField(null=True, blank=True)'),
    (r' number not null,', r' = models.IntegerField()'),
    (r' clob,', r' = models.TextField(null=True, blank=True)'),
    #(r'', r''),
)

class Command(BaseCommand):
    def handle(self, *args, **options):

        new_lines = list()
        for line in sys.stdin.readlines():
            line = line.lower()
            for pair in subs:
                line = re.sub(pair[0], pair[1], line)
            new_lines.append(line)
        new_lines.sort()
        for line in new_lines:
            print line,