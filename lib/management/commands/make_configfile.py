#!/usr/bin/env python
from django.core.management.base import BaseCommand
import ConfigParser
import os
from random import choice
import string

from django.conf import settings

def secret_key():
    return ''.join([choice(string.letters + string.digits + string.punctuation) for i in range(50)])

DEFAULTS = {
    'database': {
        'engine': 'mysql',
        'name': 'convention',
        'user': 'convention',
        'password': 'changeme',
        'server_host': '',
        'server_port': '',
    },
    'quantum_gateway': {
        'login': '',
        'key': '',
        'transaction_type': 'CREDIT',
        'use_transparent': True,
    },
    'general': {
        'debugging': False
    },
    'log': {
        'enabled': True,
        'file': 'django.log',
    },
    'security': {
        'secret_key': secret_key()
    },
    'email': {
        'error_subject': 'Convention reg software error!',
        'server': 'localhost',
        'from_address': '',
    },
}

def update_file(filename):
    config=ConfigParser.RawConfigParser()

    # Import any existing settings.
    config.read(filename)

    # Add anything we need.
    for section in DEFAULTS:
        if not config.has_section(section):
            config.add_section(section)
        for option in DEFAULTS[section]:
            if not config.has_option(section, option):
                config.set(section, option, str(DEFAULTS[section][option]))

    # Remove anything we don't use.
    for section in config.sections():
        for item, value in config.items(section):
            if section not in DEFAULTS:
                config.remove_section(section)
            elif item not in DEFAULTS[section]:
                config.remove_option(section, item)

    # Save the new version.
    f = open(filename,'w')
    f.writelines([
        '# Be aware, the server rewrites this file on startup.\n',
        '# As such, new options will be added with default values.\n',
        '# Any options removed or unknown will be deleted. As will any extra comments.\n',
        '#   Example: Delete the secret_key line, and a new one will be genreated.\n',
        '# This also means that sections, and options can move around.\n',
    ])
    config.write(f)

    return config


class Command(BaseCommand):

    def handle(self, *args, **options):
        filename = settings.CONFIG_FILE
        update_file(filename)
