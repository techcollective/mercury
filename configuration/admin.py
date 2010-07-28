from django.contrib import admin

from mercury.configuration.models import (PaymentMethod,
                                          InvoiceStatus,
                                          InvoiceTerm,
                                          Template,
                                          Config,
                                         )


class ConfigAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(PaymentMethod)
admin.site.register(InvoiceStatus)
admin.site.register(InvoiceTerm)
admin.site.register(Template)
admin.site.register(Config, ConfigAdmin)
