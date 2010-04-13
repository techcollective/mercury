from django.contrib import admin
from accounts.models import Customer, Product, Service, PaymentMethod,\
                           InvoiceStatus, Invoice, Payment,\
                           InvoiceProductEntry, InvoiceServiceEntry


class ProductInline(admin.TabularInline):
    model = InvoiceProductEntry
    extra = 2

class ServiceInline(admin.TabularInline):
    model = InvoiceServiceEntry
    extra = 2


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    exclude = ["deposit"]


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["customer", "date_created", "date_due", "status"]}),
        ("More", {"fields": ["comment"], "classes": ["collapse"]}),
    ]
    inlines = [ServiceInline, ProductInline, PaymentInline]


admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(PaymentMethod)
admin.site.register(InvoiceStatus)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Payment)
