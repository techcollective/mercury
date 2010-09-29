"""
Helper classes and functions for the accounts app
"""

import decimal
import datetime

from django.db.models import Q

from mercury.accounts import models
from mercury.helpers import get_or_create_paid_invoice_status


class AjaxChannel(object):
    def __init__(self, model, field):
        """
        Sets up a simple AJAX search channel that searches a single field.
        The model class and the field name need to be supplied as args.
        """
        self.model = model
        self.field = field

    def get_query(self, q, request):
        """
        Return a QuerySet searching for the query string q
        """
        kwargs = {"%s__icontains" % self.field: q}
        return self.model.objects.filter(**kwargs).order_by(self.field)

    def format_item(self, obj):
        """
        Format item for simple list of currently selected items
        """
        return unicode(obj)

    def format_result(self, obj):
        """
        Format search result for the drop down of search results.
        May include html """
        return unicode(obj)

    def get_objects(self, ids):
        """
        Get the currently selected objects
        """
        return self.model.objects.filter(pk__in=ids).order_by(self.field)

    def generate_autofill(self, model_instance):
        return {}


class CustomerNameAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.Customer
        self.field = "name"

    def generate_autofill(self, model_instance):
        now = datetime.date.today()
        term = model_instance.default_payment_terms.days_until_invoice_due
        term = datetime.timedelta(days=term)
        date_due = now + term
        return {"date_due": date_due}


class ProductNameAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.ProductOrService
        self.field = "name"

    def generate_autofill(self, model_instance):
        return {"cost": model_instance.price}


class InvoiceAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.Invoice
        self.field = "pk"

    def get_query(self, q, request):
        filter = Q()

        # search for invoice number if q is an int
        try:
            pk = int(q)
        except (ValueError, TypeError):
            pass
        else:
            filter = filter | Q(pk=q)

        # also search for total if q is a decimal
        try:
            total = decimal.Decimal(q)
        except (decimal.InvalidOperation, TypeError):
            pass
        else:
            filter = filter | Q(grand_total__contains=q)

        # also search for customer name
        filter = filter | Q(customer__name__icontains=q)

        paid_status = get_or_create_paid_invoice_status()
        return models.Invoice.objects.filter(filter).order_by(
            "date_created").exclude(status=paid_status)

    def generate_autofill(self, model_instance):
        return {"amount": model_instance.grand_total}
