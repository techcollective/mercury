from django.contrib import admin

from mercury.configuration.models import PaymentMethod, InvoiceStatus, Config


admin.site.register(PaymentMethod)
admin.site.register(InvoiceStatus)
admin.site.register(Config)
