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
from mercury.helpers import (get_or_create_paid_invoice_status,
                             get_display_paid, refresh, get_change_url)


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
    form = make_ajax_form(InvoiceEntry, {"item": "product_or_service_name"})
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
    readonly_fields = [field.name for field in Payment._meta.fields]
    can_delete = False
    link_readonly = "amount"


class CustomerInvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    max_num = 0
    readonly_fields = [field.name for field in Invoice._meta.fields]
    can_delete = False
    link_readonly = "description"

    def queryset(self, request):
        qs = super(CustomerInvoiceInline, self).queryset(request)
        display_paid = get_display_paid()
        paid_status = get_or_create_paid_invoice_status()

        if not display_paid:
            qs = qs.exclude(status__status__exact=paid_status)
        return qs


# custom FilterSpecs (for list_filter)

class CustomFilterSpec(FilterSpec):
    def consumed_params(self):
        return self.links.values()

    def choices(self, cl):
        selected = [v for v in self.links.values() if v in self.params]
        yield {'selected': selected == [],
               'query_string': cl.get_query_string({}, selected),
               'display': 'All'}
        for title, key in self.links.items():
            yield {'selected': key in self.params,
                   'query_string': cl.get_query_string({key: 1}, selected),
                   'display': title}


class PaidFilterSpec(CustomFilterSpec):
    def __init__(self, request, params, model, model_admin):
        super(PaidFilterSpec, self).__init__(request, params, model,
                                             model_admin)
        self.links = SortedDict((
            ('Unpaid', 'unpaid'),
            ('Unpaid and Overdue', 'unpaid_overdue'),
        ))

    def get_query_set(self, cls, qs):
        paid_status = get_or_create_paid_invoice_status()
        if 'unpaid' in self.params:
            return qs.exclude(status__exact=paid_status)
        if 'unpaid_overdue' in self.params:
            return qs.exclude(status__exact=paid_status).filter(
                date_due__lt=datetime.date.today())
        return qs

    def title(self):
        return u'unpaid status'


class DepositedFilterSpec(CustomFilterSpec):
    def __init__(self, request, params, model, model_admin):
        super(DepositedFilterSpec, self).__init__(request, params, model,
                                                  model_admin)
        self.links = SortedDict((
            ('Deposited', 'deposited'),
            ('Undeposited', 'undeposited'),
        ))

    def get_query_set(self, cls, qs):
        if 'deposited'in self.params:
            return qs.filter(deposit__isnull=False).filter(
                payment_type__manage_deposits__exact=True)
        if 'undeposited'in self.params:
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
    hide_delete_warning = (InvoiceEntry,)
    inlines = [InvoiceEntryInline, InvoicePaymentInline]
    date_hierarchy = "date_created"
    list_display = ["get_number", "description", "get_customer_link", "status",
                    "grand_total", "date_created", "date_due"]
    list_display_links = ["get_number", "description"]
    list_filter = [PaidFilterSpec, "status"]

    def post_save(self, instance):
        # get the most recent instance from the db. the post save signal hook
        # may have made changes since the admin called save().
        instance = refresh(instance)
        instance.update()
        instance.save()

    def get_customer_link(self, instance):
        url = get_change_url(instance.customer)
        return "<a href=\"%s\">%s</a>" % (url, instance.customer.name)
    get_customer_link.allow_tags = True
    get_customer_link.short_description = "Customer"


class QuoteAdmin(MercuryAjaxAdmin):
    search_fields = ["customer__name", "description", "id"]
    form = make_ajax_form(Quote, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created",
                                    "description"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    hide_delete_warning = (QuoteEntry,)
    inlines = [QuoteEntryInline]
    date_hierarchy = "date_created"
    list_display = ["get_number", "description", "customer", "grand_total",
                    "date_created"]
    list_display_links = ["get_number", "description"]

    def post_save(self, instance):
        # get the most recent instance from the db. the post save hook may have
        # made changes since the admin called save().
        instance = refresh(instance)
        instance.update()
        instance.save()


class CustomerAdmin(MercuryAdmin):
    inlines = [CustomerInvoiceInline]
    search_fields = ["name", "phone_number"]
    list_display = ["name", "phone_number", "email_address", "is_taxable"]
    fieldsets = [
        (None, {"fields": ["name", "is_taxable", "default_payment_terms"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]

    def change_view(self, *args, **kwargs):
        display_paid = get_display_paid()
        if not display_paid:
            inline_title = "Unpaid invoices"
        else:
            inline_title = "Invoices"
        kwargs["extra_context"] = {"inline_title": inline_title}
        return super(CustomerAdmin, self).change_view(*args, **kwargs)


class DepositAdmin(MercuryAdmin):
    inlines = [DepositPaymentInline]
    hide_delete_warning = (Payment,)


class PaymentAdmin(MercuryAjaxAdmin):
    form = make_ajax_form(Payment, {"invoice": "invoice"})
    list_display = ["amount", "payment_type", "get_invoice_link",
                    "date_received", "comment", "get_deposit_link"]
    list_filter = [DepositedFilterSpec, "payment_type"]
    actions = ["deposit"]
    date_hierarchy = "date_received"
    search_fields = ["invoice__customer__name", "amount"]

    def get_invoice_link(self, instance):
        invoice = instance.invoice
        url = get_change_url(invoice)
        return "<a href=\"%s\">%s</a>" % (url, str(invoice))
    get_invoice_link.allow_tags = True
    get_invoice_link.short_description = "Invoice"

    def get_deposit_link(self, instance):
        deposit = instance.deposit
        if deposit is None:
            return "None"
        else:
            url = get_change_url(deposit)
            return "<a href=\"%s\">%s</a>" % (url, str(deposit))
    get_deposit_link.allow_tags = True
    get_deposit_link.short_description = "Deposit"

    def deposit(self, request, queryset):
        already_deposited = queryset.exclude(deposit=None)
        count = already_deposited.count()
        if count > 0:
            if count == 1:
                message = "One already deposited payment was left unchanged"
            else:
                message = ("%s already deposited payments were left "
                           "unchanged" % count)
            messages.warning(request, message)
            queryset = queryset.filter(deposit=None)
        not_depositable = queryset.filter(payment_type__manage_deposits=False)
        count = not_depositable.count()
        if count > 0:
            if count == 1:
                message = ("One payment was ignored as its type isn't "
                          "depositable")
            else:
                message = ("%s payments were ignored as their types "
                           "aren't depositable" % count)
            messages.warning(request, message)
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
            # update the deposit total field
            new_deposit.update_total()
            new_deposit.save()
            self.message_user(request, message)
        else:
            messages.warning(request, "No deposit was created as none of the "
                                      "selected payments were depositable")
    deposit.short_description = "Deposit selected payments"


class ProductOrServiceAdmin(MercuryAdmin):
    search_fields = ["name"]
    list_display = ["name", "price", "number_in_stock", "manage_stock",
                    "is_taxable"]

# Registration

admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductOrService, ProductOrServiceAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Deposit, DepositAdmin)
