from django.contrib import admin

from mercury.configuration.models import (PaymentType,
                                          InvoiceStatus,
                                          InvoiceTerm,
                                          Template,
                                          Config,
                                         )
from mercury.admin import MercuryAdmin


class ConfigAdmin(MercuryAdmin):
    search_fields = ["name"]


# All models must have MercuryAdmin (or subclasses) ModelAdmins
# so that global list_per_page and other functionality works.
admin.site.register(PaymentType, MercuryAdmin)
admin.site.register(InvoiceStatus, MercuryAdmin)
admin.site.register(InvoiceTerm, MercuryAdmin)
admin.site.register(Template, MercuryAdmin)
admin.site.register(Config, ConfigAdmin)
