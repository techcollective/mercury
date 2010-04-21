from django.contrib import admin
from accounts.models import Customer, Product, Service, PaymentMethod, \
                           InvoiceStatus, Invoice, Payment, Quote, \
                           InvoiceProductEntry, InvoiceServiceEntry, Deposit, \
                           QuoteProductEntry, QuoteServiceEntry


class ServiceInline(admin.TabularInline):
    extra = 1
    verbose_name = "Service"
    verbose_name_plural = "Services"


class ProductInline(admin.TabularInline):
    extra = 1
    verbose_name = "Product"
    verbose_name_plural = "Products"


class InvoiceProductInline(ProductInline):
    model = InvoiceProductEntry


class InvoiceServiceInline(ServiceInline):
    model = InvoiceServiceEntry


class QuoteProductInline(ProductInline):
    model = QuoteProductEntry


class QuoteServiceInline(ServiceInline):
    model = QuoteServiceEntry


class InvoicePaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    exclude = ["deposit"]
    show_last = True


class DepositPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "date_due", "status", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    readonly_fields = ["subtotal", "total_tax", "grand_total"]
    inlines = [InvoiceServiceInline, InvoiceProductInline,
               InvoicePaymentInline]
    date_hierarchy = "date_created"


class QuoteAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    readonly_fields = ["subtotal", "total_tax", "grand_total"]
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
