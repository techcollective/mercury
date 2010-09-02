"""
Helper classes and functions for the accounts app
"""

from mercury.accounts import models


class AjaxChannel(object):
    def __init__(self, model, field):
        """
        Sets up a simple AJAX search channel that searches a single field.
        The model class and the field name need to be supplied as args.
        """
        self.model = model
        self.field = field

    def _get_queryset(self, q):
        kwargs = {"%s__icontains" % self.field : q}
        return self.model.objects.filter(**kwargs).order_by(self.field)

    def get_query(self, q, request):
        """
        Return a QuerySet searching for the query string q
        """
        if request.user.is_authenticated():
            return self._get_queryset(q)
        else:
            return None

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


class CustomerNameAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.Customer
        self.field = "name"


class ProductNameAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.ProductOrService
        self.field = "name"


class PaymentInvoiceAjaxChannel(AjaxChannel):
    def __init__(self):
        self.model = models.Invoice
        self.field = "pk"
