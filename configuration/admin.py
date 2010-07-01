from django.contrib import admin

from mercury.configuration.models import (PaymentMethod,
                                          InvoiceStatus,
                                          InvoiceTerm,
                                          InvoiceTemplate,
                                          Config,
                                         )


admin.site.register(PaymentMethod)
admin.site.register(InvoiceStatus)
admin.site.register(InvoiceTerm)
admin.site.register(InvoiceTemplate)
admin.site.register(Config)
