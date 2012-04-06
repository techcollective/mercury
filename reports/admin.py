import datetime

from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from mercury.admin import MercuryAdmin
from mercury.helpers import (get_or_create_paid_invoice_status,
                             get_change_url)
from accounts.models import InvoiceEntry


class UnpaidStatusListFilter(SimpleListFilter):
    title = "unpaid status"
    parameter_name = "unpaid_status"

    def lookups(self, request, model_admin):
        return (
            ("unpaid", "Unpaid"),
            ("unpaid_overdue", "Unpaid and Overdue"),
        )

    def queryset(self, request, queryset):
        paid_status = get_or_create_paid_invoice_status()
        if self.value() == "unpaid":
            return queryset.exclude(invoice__status=paid_status)
        if self.value() == "unpaid_overdue":
            return queryset.exclude(invoice__status=paid_status).filter(
                invoice__date_due__lt=datetime.date.today())


class SalesReportAdmin(MercuryAdmin):
    list_display = ["item", "cost", "quantity", "description", "discount",
                    "total", "get_invoice_link"]
    list_filter = ["invoice__status", UnpaidStatusListFilter,
                   "item__is_taxable", "invoice__created_by"]

    def get_invoice_link(self, instance):
        invoice = instance.invoice
        url = get_change_url(invoice)
        return "<a href=\"%s\">%s</a>" % (url, str(invoice))
    get_invoice_link.allow_tags = True
    get_invoice_link.short_description = "Invoice"


admin.site.register(InvoiceEntry, SalesReportAdmin)
