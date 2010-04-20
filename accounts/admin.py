from django.contrib import admin
from accounts.models import Customer, Product, Service, PaymentMethod, \
                           InvoiceStatus, Invoice, Payment, Quote, \
                           InvoiceProductEntry, InvoiceServiceEntry, Deposit, \
                           QuoteProductEntry, QuoteServiceEntry


class InvoiceProductInline(admin.TabularInline):
    model = InvoiceProductEntry
    extra = 1


class InvoiceServiceInline(admin.TabularInline):
    model = InvoiceServiceEntry
    extra = 1


class QuoteProductInline(admin.TabularInline):
    model = QuoteProductEntry
    extra = 1


class QuoteServiceInline(admin.TabularInline):
    model = QuoteServiceEntry
    extra = 1


class InvoicePaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    exclude = ["deposit"]


class DepositPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["customer", "date_created", "date_due", "status"]}),
        ("More", {"fields": ["comment"], "classes": ["collapse"]}),
    ]
    inlines = [InvoiceServiceInline, InvoiceProductInline,
               InvoicePaymentInline]
    date_hierarchy = "date_created"


class QuoteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["customer", "date_created"]}),
        ("More", {"fields": ["comment"], "classes": ["collapse"]}),
    ]
    inlines = [QuoteServiceInline, QuoteProductInline]
    date_hierarchy = "date_created"


class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]


class DepositAdmin(admin.ModelAdmin):
    inlines = [DepositPaymentInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment)
admin.site.register(Deposit, DepositAdmin)
