import datetime

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.filterspecs import FilterSpec
from django.utils.datastructures import SortedDict

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add

from mercury.accounts.models import (Customer,
                                     ProductOrService,
                                     Invoice,
                                     Quote,
                                     InvoiceEntry,
                                     QuoteEntry,
                                     Payment,
                                     Deposit,)
from mercury.admin import MercuryAdmin, MercuryAjaxAdmin
from mercury.helpers import get_or_create_paid_invoice_status


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
    max_num = 0

# custom FilterSpecs (for list_filter)

class CustomFilterSpec(FilterSpec):
    def consumed_params(self):
        return self.links.values()

    def choices(self, cl):
        selected = [v for v in self.links.values() if self.params.has_key(v)]
        for title, key in self.links.items():
            yield {'selected': self.params.has_key(key),
                   'query_string': cl.get_query_string({key:1}, selected),
                   'display': title}


class PaidFilterSpec(CustomFilterSpec):
    def __init__(self, request, params, model, model_admin):
        super(PaidFilterSpec, self).__init__(request, params, model, model_admin)
        self.links = SortedDict((
            ('All', 'all'),
            ('Unpaid', 'unpaid'),
            ('Unpaid and Overdue', 'unpaid_overdue'),
        ))

    def get_query_set(self, cls, qs):
        paid_status = get_or_create_paid_invoice_status()
        if self.params.has_key('unpaid'):
            return qs.exclude(status__exact=paid_status)
        if self.params.has_key('unpaid_overdue'):
            return qs.exclude(status__exact=paid_status).filter(
                date_due__lte=datetime.date.today())
        return qs

    def title(self):
        return u'unpaid status'


class DepositedFilterSpec(CustomFilterSpec):
    def __init__(self, request, params, model, model_admin):
        super(DepositedFilterSpec, self).__init__(request, params, model, model_admin)
        self.links = SortedDict((
            ('All', 'all'),
            ('Deposited', 'deposited'),
            ('Undeposited', 'undeposited'),
        ))

    def get_query_set(self, cls, qs):
        if self.params.has_key('deposited'):
            return qs.filter(deposit__isnull=False).filter(
                payment_type__manage_deposits__exact=True)
        if self.params.has_key('undeposited'):
            return qs.filter(deposit__isnull=True).filter(
                payment_type__manage_deposits__exact=True)
        return qs

    def title(self):
        return u'deposited status'


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
    list_filter = [PaidFilterSpec, "status"]

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
    list_display = ["__str__", "amount", "date_received", "deposit"]
    list_filter = [DepositedFilterSpec, "payment_type"]
    actions = ["deposit"]
    date_hierarchy = "date_received"
    search_fields = ["invoice__customer__name", "amount"]

    def deposit(self, request, queryset):
        already_deposited = queryset.filter(deposit__isnull=False)
        count = already_deposited.count()
        if count > 0:
            messages.warning(request, "One or more already deposited payments "
                                      "were left unchanged")
            queryset = queryset.filter(deposit__isnull=True)
        not_depositable = queryset.filter(payment_type__manage_deposits=False)
        count = not_depositable.count()
        if count > 0:
            messages.warning(request, "One or more payments were ignored as "
                                      "their type isn't depositable ")
            queryset = queryset.exclude(payment_type__manage_deposits=False)
        count = queryset.count()
        if count > 0:
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
        else:
            messages.warning(request, "No deposit was created as none of the "
                                      "selected payments were depositable")
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
