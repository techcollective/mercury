from django.contrib import admin

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add

from mercury.accounts.models import (Customer,
                                     ProductOrService,
                                     Invoice,
                                     Quote,
                                     InvoiceEntry,
                                     QuoteEntry,
                                     Payment,
                                     Deposit,
                                    )

# Custom inline classes

class AjaxTabularInline(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AjaxTabularInline, self).get_formset(request, obj,
                                                            **kwargs)
        autoselect_fields_check_can_add(formset.form, self.model, request.user)
        return formset


# Inlines

class ProductOrServiceInline(AjaxTabularInline):
    extra = 0
    verbose_name = "Product or service"
    verbose_name_plural = "Products or services"
    form = make_ajax_form(InvoiceEntry, {"item": "product_or_service_name"},
                          autofill={"item": {"field": "cost",
                                             "related_field": "price",
                                             }})
    exclude = ["total"]


class InvoiceEntryInline(ProductOrServiceInline):
    model = InvoiceEntry


class QuoteEntryInline(ProductOrServiceInline):
    model = QuoteEntry


class InvoicePaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    exclude = ["deposit"]
    show_last = True


class DepositPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


# Admin classes

class InvoiceAdmin(AjaxSelectAdmin):
    search_fields = ["customer__name"]
    form = make_ajax_form(Invoice, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "date_due",
                                    "status", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    inlines = [InvoiceEntryInline, InvoicePaymentInline]
    date_hierarchy = "date_created"

    def post_save(self, instance):
        instance.update_totals()


class QuoteAdmin(AjaxSelectAdmin):
    search_fields = ["customer__name"]
    form = make_ajax_form(Quote, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    inlines = [QuoteEntryInline]
    date_hierarchy = "date_created"

    def post_save(self, instance):
        instance.update_totals()


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    fieldsets = [
        (None, {"fields": ["name", "is_taxable", "default_payment_terms"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]


class DepositAdmin(admin.ModelAdmin):
    inlines = [DepositPaymentInline]

    def merge_deposits(self, request, queryset):
        pass


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "date_received", "deposit"]
    list_filter = ["deposit"]
    actions = ["deposit"]

    def deposit(self, request, queryset):
        new_deposit = Deposit()
        new_deposit.save()
        rows_updated = queryset.update(deposit=new_deposit)
        if rows_updated == 1:
            message = "1 payment was"
        else:
            message = "%s payments were" % rows_updated
        message += " deposited successfully"
        new_deposit.update_total()
        self.message_user(request, message)
    deposit.short_description = "Deposit selected payments"


# Registration

admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductOrService)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Deposit, DepositAdmin)
