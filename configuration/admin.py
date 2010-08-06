from django.contrib import admin

from mercury.configuration.models import (PaymentType,
                                          InvoiceStatus,
                                          InvoiceTerm,
                                          Template,
                                          Config,
                                         )


class ConfigAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(PaymentType)
admin.site.register(InvoiceStatus)
admin.site.register(InvoiceTerm)
admin.site.register(Template)
admin.site.register(Config, ConfigAdmin)
