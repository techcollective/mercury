from django.contrib import admin
from accounts.models import Customer, Product, Service, PaymentMethod,\
                           InvoiceStatus, Invoice, Payment

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(PaymentMethod)
admin.site.register(InvoiceStatus)
admin.site.register(Invoice)
admin.site.register(Payment)
