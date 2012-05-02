import decimal

from django.db.models import Q

from accounts import models

from mercury.helpers import (get_or_create_paid_invoice_status,
                             get_autocomplete_limit)


class AjaxChannel(object):
    def __init__(self, model, field):
        """
        Sets up a simple AJAX search channel that searches a single field.
        The model class and the field name need to be supplied as args.
        """
        self.model = model
        self.field = field

    def _get_queryset(self, q, request):
        """
        Return a QuerySet searching for the query string q
        """
        kwargs = {"%s__icontains" % self.field: q}
        return self.model.objects.filter(**kwargs).order_by(self.field)

    def get_query(self, q, request):
        max_num = get_autocomplete_limit()
        return self._get_queryset(q, request)[:max_num]

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
        return {"date_due": get_date_due(model_instance)}


class ProductNameAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.ProductOrService
        self.field = "name"

    def generate_autofill(self, model_instance):
        return {"cost": model_instance.price, "is_taxable": model_instance.is_taxable}


class InvoiceAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.Invoice
        self.field = "pk"

    def _get_queryset(self, q, request):
        lookup = Q()

        # search for invoice number if q is an int
        try:
            pk = int(q)
        except (ValueError, TypeError):
            pass
        else:
            lookup = lookup | Q(pk=q)

        # also search for total if q is a decimal
        try:
            total = decimal.Decimal(q)
        except (decimal.InvalidOperation, TypeError):
            pass
        else:
            lookup = lookup | Q(grand_total__contains=q)

        # also search for customer name
        lookup = lookup | Q(customer__name__icontains=q)

        return models.Invoice.objects.filter(lookup)


class UnpaidInvoiceAjaxChannel(InvoiceAjaxChannel):
    def _get_queryset(self, q, request):
        paid_status = get_or_create_paid_invoice_status()
        qs = super(UnpaidInvoiceAjaxChannel, self)._get_queryset(q, request)
        return qs.exclude(status=paid_status)

    def generate_autofill(self, model_instance):
        """
        Autofill for the Payment add page "amount" field
        """
        return {"amount": model_instance.grand_total}
