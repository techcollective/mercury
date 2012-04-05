from django.contrib import admin

from mercury.admin import MercuryAdmin
from accounts.models import InvoiceEntry


class SalesReportAdmin(MercuryAdmin):
    pass

admin.site.register(InvoiceEntry, SalesReportAdmin)
