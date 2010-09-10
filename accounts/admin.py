from django.contrib import admin

from ajax_select import make_ajax_form
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
from mercury.helpers import MercuryAdmin, MercuryAjaxAdmin


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
    exclude = ["deposit", "depositable"]
    show_last = True


class DepositPaymentInline(admin.TabularInline):
    model = Payment
    exclude = ["depositable"]
    extra = 0
    max_num = 0


# Admin classes

class InvoiceAdmin(MercuryAjaxAdmin):
    search_fields = ["customer__name", "description", "id"]
    form = make_ajax_form(Invoice, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "date_due",
                                    "status", "description"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    inlines = [InvoiceEntryInline, InvoicePaymentInline]
    date_hierarchy = "date_created"
    list_display = ["get_number", "description", "customer", "status", "grand_total", "date_created", "date_due"]
    list_display_links = ["get_number", "description"]
    list_filter = ["status"]

    def post_save(self, instance):
        instance.update()
        instance.save()

    def get_actions(self, *args, **kwargs):
        actions = super(InvoiceAdmin, self).get_actions(*args, **kwargs)
        actions['delete_selected'][0].short_description = "Delete selected invoices without re-adding items to stock"
        return actions


class QuoteAdmin(MercuryAjaxAdmin):
    search_fields = ["customer__name", "description", "id"]
    form = make_ajax_form(Quote, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "description"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    inlines = [QuoteEntryInline]
    date_hierarchy = "date_created"
    list_display = ["get_number", "description", "customer", "grand_total", "date_created"]
    list_display_links = ["get_number", "description"]

    def post_save(self, instance):
        instance.update()
        instance.save()


class CustomerAdmin(MercuryAdmin):
    search_fields = ["name"]
    fieldsets = [
        (None, {"fields": ["name", "is_taxable", "default_payment_terms"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]


class DepositAdmin(MercuryAdmin):
    inlines = [DepositPaymentInline]

    def merge_deposits(self, request, queryset):
        pass


class PaymentAdmin(MercuryAdmin):
#class PaymentAdmin(MercuryAjaxAdmin):
    #form = make_ajax_form(Payment, {"invoice": "invoice"})
    list_display = ["__str__", "date_received", "deposited"]
    list_filter = ["depositable"]
    actions = ["deposit"]
    exclude = ["depositable"]
    date_hierarchy = "date_received"

    def deposited(self, instance):
        return (instance.deposit is not None) or \
               (instance.depositable == False)
    deposited.boolean = True
    deposited.admin_order_field = 'deposit'

    def deposit(self, request, queryset):
        new_deposit = Deposit()
        # save() to create the deposit, otherwise it can't have
        # payments assigned to it.
        new_deposit.save()
        rows_updated = queryset.update(deposit=new_deposit)
        if rows_updated == 1:
            message = "1 payment was"
        else:
            message = "%s payments were" % rows_updated
        message += " deposited successfully"
        # save() again to update the deposit total field
        new_deposit.save()
        self.message_user(request, message)
    deposit.short_description = "Deposit selected payments"

    def get_actions(self, *args, **kwargs):
        actions = super(PaymentAdmin, self).get_actions(*args, **kwargs)
        del actions['delete_selected']
        return actions


# Registration

admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductOrService)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Deposit, DepositAdmin)
