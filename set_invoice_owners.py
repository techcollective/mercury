#!/usr/bin/env python

import os
import sys
env_var = "DJANGO_SETTINGS_MODULE"
if not env_var in os.environ:
    os.environ[env_var] = "mercury.settings"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION

from mercury.accounts.models import Invoice


ct = ContentType.objects.get_for_model(Invoice)

for invoice in Invoice.objects.all():
    try:
        user = LogEntry.objects.get(content_type=ct, action_flag=ADDITION,
                                    object_id=invoice.pk).user
        print invoice, user
    except LogEntry.DoesNotExist:
        print "Couldn't figure out who created", invoice
