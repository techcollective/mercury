#!/usr/bin/env python

import os
import sys
env_var = "DJANGO_SETTINGS_MODULE"
if not env_var in os.environ:
    os.environ[env_var] = "mercury.settings"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION
from django.db import transaction

from mercury.accounts.models import Invoice, Payment, Deposit


@transaction.commit_on_success
def set_all():
    ct = ContentType.objects.get_for_model(Invoice)

    # invoices
    for invoice in Invoice.objects.all():
        try:
            user = LogEntry.objects.get(content_type=ct, action_flag=ADDITION,
                                        object_id=invoice.pk).user
            print "linking invoice %s to %s" % (invoice, user)
            invoice.created_by = user
            invoice.save()
        except LogEntry.DoesNotExist:
            print "Couldn't figure out who created", invoice

    # note: neither of the below find anything, as payments were added inline
    # and deposits created with a custom action.

    # payments
    ct = ContentType.objects.get_for_model(Payment)
    for payment in Payment.objects.all():
        try:
            user = LogEntry.objects.get(content_type=ct, action_flag=ADDITION,
                                        object_id=payment.pk).user
            print "linking payment %s to %s" % (payment, user)
            payment.received_by = user
            payment.save()
        except LogEntry.DoesNotExist:
            print "Couldn't figure out who created", payment

    # deposits
    ct = ContentType.objects.get_for_model(Deposit)
    for deposit in Deposit.objects.all():
        try:
            user = LogEntry.objects.get(content_type=ct, action_flag=ADDITION,
                                        object_id=deposit.pk).user
            print "linking deposit %s to %s" % (deposit, user)
            deposit.made_by = user
            deposit.save()
        except LogEntry.DoesNotExist:
            print "Couldn't figure out who created", deposit

if __name__ == '__main__':
    set_all()
