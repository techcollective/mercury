import datetime

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import SimpleListFilter

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add

from accounts.models import (Customer,
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
    readonly_fields = ["received_by"]
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
        query_set = super(CustomerInvoiceInline, self).queryset(request)
        display_paid = get_display_paid()
        paid_status = get_or_create_paid_invoice_status()

        if not display_paid:
            query_set = query_set.exclude(status__status=paid_status)
        return query_set


# custom filters (for list_filter)


class UnpaidStatusListFilter(SimpleListFilter):
    title = "unpaid status"
    parameter_name = "unpaid_status"

    def lookups(self, request, model_admin):
        return (
            ("unpaid", "Unpaid"),
            ("unpaid_overdue", "Unpaid and Overdue"),
        )

    def queryset(self, request, queryset):
        paid_status = get_or_create_paid_invoice_status()
        if self.value() == "unpaid":
            return queryset.exclude(status=paid_status)
        if self.value() == "unpaid_overdue":
            return queryset.exclude(status=paid_status).filter(
                date_due__lt=datetime.date.today())


class StockStatusListFilter(SimpleListFilter):
    title = "stock status"
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("instock", "In Stock"),
            ("nostock", "Out of Stock"),
        )

    def queryset(self, request, queryset):
        if self.value() == "instock":
            return queryset.exclude(number_in_stock__lte=0).filter(
                manage_stock=True)
        if self.value() == "nostock":
            return queryset.filter(number_in_stock__lte=0).filter(
                manage_stock=True)


class DepositedStatusListFilter(SimpleListFilter):
    title = "deposited status"
    parameter_name = "deposited_status"

    def lookups(self, request, model_admin):
        return (
            ("deposited", "Deposited"),
            ("undeposited", "Undeposited"),
        )

    def queryset(self, request, queryset):
        if self.value() == "deposited":
            return queryset.filter(deposit__isnull=False).filter(
                payment_type__manage_deposits=True)
        if self.value() == "undeposited":
            return queryset.filter(deposit__isnull=True).filter(
                payment_type__manage_deposits=True)


# Admin classes

class InvoiceQuoteBaseAdmin(MercuryAjaxAdmin):
    search_fields = ["customer__name", "description", "id"]
    date_hierarchy = "date_created"

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.save()

    def get_customer_link(self, instance):
        url = get_change_url(instance.customer)
        return "<a href=\"%s\">%s</a>" % (url, instance.customer.name)
    get_customer_link.allow_tags = True
    get_customer_link.short_description = "Customer"
    get_customer_link.admin_order_field = "customer"

    def save_related(self, request, form, formsets, change):
        super(InvoiceQuoteBaseAdmin, self).save_related(request, form,
                                                        formsets, change)
        instance = form.instance
        instance.update()
        instance.save()


class InvoiceAdmin(InvoiceQuoteBaseAdmin):
    form = make_ajax_form(Invoice, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "date_due",
                                    "status", "description", "notes",
                                    "created_by"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    hide_delete_warning = (InvoiceEntry,)
    inlines = [InvoiceEntryInline, InvoicePaymentInline]
    list_display = ["get_number", "description", "notes", "get_customer_link",
                    "status", "grand_total", "date_created", "date_due",
                    "created_by"]
    list_display_links = ["get_number", "description"]
    list_filter = [UnpaidStatusListFilter, "status", "created_by"]

    def save_formset(self, request, form, formset, change):
        # if adding inline payments to an invoice, set the creator of
        # the payments.
        if formset.model == Payment:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.received_by:
                    instance.received_by = request.user
                    instance.save()
            formset.save_m2m()
        else:
            super(InvoiceAdmin, self).save_formset(request, form, formset,
                                                   change)


class QuoteAdmin(InvoiceQuoteBaseAdmin):
    form = make_ajax_form(Quote, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created",
                                    "description", "notes", "created_by"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    hide_delete_warning = (QuoteEntry,)
    inlines = [QuoteEntryInline]
    list_display = ["get_number", "description", "notes", "get_customer_link",
                    "grand_total", "date_created", "created_by"]
    list_filter = ["created_by"]
    list_display_links = ["get_number", "description"]


class CustomerAdmin(MercuryAdmin):
    inlines = [CustomerInvoiceInline]
    search_fields = ["name", "phone_number", "address", "city", "state",
                     "zip_code"]
    list_display = ["name", "phone_number", "email_address", "get_address",
                    "is_taxable"]
    fieldsets = [
        (None, {"fields": ["name", "is_taxable", "default_payment_terms"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]
    list_filter = ["is_taxable"]

    def get_address(self, instance):
        address = [instance.address, instance.city, instance.state]
        return ", ".join(filter(None, address))
    get_address.short_description = "Address"

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
    list_display = ["total", "date", "comment", "made_by"]
    date_hierarchy = "date"
    list_filter = ["made_by"]

    def save_model(self, request, obj, form, change):
        if not obj.made_by:
            obj.made_by = request.user
        obj.save()


class PaymentAdmin(MercuryAjaxAdmin):
    # these allow the custom querystring lookups used to show the user
    # which deposited payments are preventing the deletion of a particular
    # model instance. this will at some point be replaced with a different
    # system. see https://github.com/techcollective/mercury/issues/153
    allowed_lookups = ["invoice__customer__pk",  # customer
                       "invoice__pk",  # invoice
                       "payment_type__pk",  # payment type
                       "invoice__status__pk",  # invoice status
                       "invoice__customer__default_payment_terms__pk",  # terms
                       ]
    form = make_ajax_form(Payment, {"invoice": "invoice"})
    list_display = ["get_invoice_link", "get_customer_link", "date_received",
                    "comment", "get_deposit_link", "received_by",
                    "payment_type", "amount"]
    list_display_links = ["amount"]
    list_filter = [DepositedStatusListFilter, "payment_type", "received_by"]
    actions = ["deposit"]
    date_hierarchy = "date_received"
    search_fields = ["invoice__customer__name", "invoice__pk", "amount"]

    def get_customer_link(self, instance):
        url = get_change_url(instance.invoice.customer)
        return "<a href=\"%s\">%s</a>" % (url, instance.invoice.customer.name)
    get_customer_link.allow_tags = True
    get_customer_link.short_description = "Customer"
    get_customer_link.admin_order_field = "invoice__customer"

    def get_invoice_link(self, instance):
        invoice = instance.invoice
        url = get_change_url(invoice)
        return "<a href=\"%s\">%s</a>" % (url, str(invoice))
    get_invoice_link.allow_tags = True
    get_invoice_link.short_description = "Invoice"
    get_invoice_link.admin_order_field = "invoice"

    def get_deposit_link(self, instance):
        deposit = instance.deposit
        if deposit is None:
            return "None"
        else:
            url = get_change_url(deposit)
            return "<a href=\"%s\">%s</a>" % (url, str(deposit))
    get_deposit_link.allow_tags = True
    get_deposit_link.short_description = "Deposit"
    get_deposit_link.admin_order_field = "deposit"

    def save_model(self, request, obj, form, change):
        if not obj.received_by:
            obj.received_by = request.user
        obj.save()
        obj.invoice.update_status()
        obj.invoice.save()

    def delete_model(self, request, obj):
        super(PaymentAdmin, self).delete_model(request, obj)
        obj.invoice.update_status()
        obj.invoice.save()

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
            new_deposit.made_by = request.user
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
    list_filter = ["manage_stock", "is_taxable", StockStatusListFilter]
    list_editable = ["number_in_stock"]


class SalesReportAdmin(MercuryAdmin):
    actions = None
    date_range = "invoice__date_created"
    list_display = ["item", "description", "cost", "quantity", "discount",
                    "total", "get_invoice_link"]
    # todo: custom default filter that shows only paid stuff? after all
    # this is a *sales* report
    list_filter = ["invoice__status", "item__is_taxable",
                   "invoice__created_by"]
    allowed_lookups = ["invoice__date_created__gte",
                       "invoice__date_created__lte"]

    def get_invoice_link(self, instance):
        invoice = instance.invoice
        url = get_change_url(invoice)
        return "<a href=\"%s\">%s - %s</a>" % (url, invoice, invoice.date_created)
    get_invoice_link.allow_tags = True
    get_invoice_link.short_description = "Invoice"
    get_invoice_link.admin_order_field = "invoice"


# Registration

admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductOrService, ProductOrServiceAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(InvoiceEntry, SalesReportAdmin)
