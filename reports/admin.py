import datetime

from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from mercury.admin import MercuryAdmin
from mercury.helpers import get_or_create_paid_invoice_status
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
                    "total", "invoice"]
    list_filter = ["invoice__status", UnpaidStatusListFilter,
                   "item__is_taxable", "invoice__created_by"]

admin.site.register(InvoiceEntry, SalesReportAdmin)
