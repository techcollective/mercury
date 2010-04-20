from django.contrib import admin
from accounts.models import Customer, Product, Service, PaymentMethod,\
                           InvoiceStatus, Invoice, Payment,\
                           InvoiceProductEntry, InvoiceServiceEntry, Deposit


class ProductInline(admin.TabularInline):
    model = InvoiceProductEntry
    extra = 1


class ServiceInline(admin.TabularInline):
    model = InvoiceServiceEntry
    extra = 1


class PaymentInvoiceInline(admin.TabularInline):
    model = Payment
    extra = 1
    exclude = ["deposit"]


class PaymentDepositInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["customer", "date_created", "date_due", "status"]}),
        ("More", {"fields": ["comment"], "classes": ["collapse"]}),
    ]
    inlines = [ServiceInline, ProductInline, PaymentInvoiceInline]
    date_hierarchy = "date_created"


class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]


class DepositAdmin(admin.ModelAdmin):
    inlines = [PaymentDepositInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Payment)
admin.site.register(Deposit, DepositAdmin)
