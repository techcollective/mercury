import datetime
import decimal

from django.db import models
from django.utils.text import capfirst
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import admin
import pandora

from configuration.models import (PaymentType,
                                  InvoiceStatus,
                                  InvoiceTerm,
                                  ProductOrServiceCategory)
from accounts.fields import CurrencyField
from mercury.helpers import (check_deposited_payments,
                             get_change_url,
                             get_currency_symbol,
                             get_or_create_default_invoice_status,
                             get_tax_percentage,
                             get_or_create_default_invoice_term,
                             get_or_create_paid_invoice_status,
                             get_customer_taxable,
                             get_product_taxable,
                             get_manage_stock,
                             get_default_quantity,
                             get_invoice_padding,
                             get_fill_description,
                             get_negative_stock,
                             get_auto_invoice_status)
from accounts.exceptions import (DepositedPaymentsException,
                                         AccountsException)


class SelectRelatedManager(models.Manager):
    def __init__(self, select_related_fields=None):
        select_related_fields = select_related_fields or []
        self.select_related_fields = select_related_fields
        super(SelectRelatedManager, self).__init__()

    def get_query_set(self):
        # this is to help with the performance of __unicode__ on the model
        return super(SelectRelatedManager,
                     self).get_query_set().select_related(
                                                *self.select_related_fields)


class Customer(models.Model):
    class Meta:
        ordering = ["name"]
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=50, blank=True)
    is_taxable = models.BooleanField(default=get_customer_taxable)
    default_payment_terms = models.ForeignKey(InvoiceTerm,
                                    default=get_or_create_default_invoice_term)

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # prevent a delete that will cascade to deposited payments
        check_deposited_payments(self, "invoice__customer__pk")
        super(Customer, self).delete(*args, **kwargs)


class ProductOrService(models.Model):
    name = models.CharField(max_length=100)
    price = CurrencyField(null=True, blank=True)
    stock = models.DecimalField(null=True, blank=True, max_digits=14,
                                decimal_places=2)
    manage_stock = models.BooleanField(default=get_manage_stock)
    is_taxable = models.BooleanField(default=get_product_taxable)
    categories = models.ManyToManyField(ProductOrServiceCategory, blank=True)

    def clean(self):
        if self.manage_stock and (self.stock is None):
            raise ValidationError("Number in stock must be set when managing "
                                  "stock. Please enter a number or switch "
                                  "stock management off for this item.")

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Products and services"


def check_negative_stock(sender, **kwargs):
    instance = kwargs["instance"]
    if instance.manage_stock:
        # re-fetch the product/service instance from the db to get the actual
        # stock number. it is set to an F() expression by the invoice entry
        # creation signal handler. see
        # ("https://docs.djangoproject.com/en/1.4/ref/models/instances/"
        #  "#updating-attributes-based-on-existing-fields")
        obj = sender.objects.get(pk=instance.pk)
        allow_negative = get_negative_stock()
        if not allow_negative and obj.stock < 0:
            obj.stock = 0
            obj.save()
            # pass audit_stock=False since the appropriate number will
            # appear in the LogEntry of the event that triggered this hook.
            log_stock_change(obj, "Auto-set stock to zero since current "
                             "settings do not allow negative stock.",
                             audit_stock=False)

models.signals.post_save.connect(check_negative_stock, sender=ProductOrService)


class QuoteInvoiceBase(models.Model):
    customer = models.ForeignKey(Customer)
    date_created = models.DateField(default=datetime.date.today)
    # help_text for description is dynamically set in the ModelAdmin's
    # render_change_form()
    description = models.CharField(max_length=200, blank=True)
    subtotal = CurrencyField(default=0, read_only=True)
    total_tax = CurrencyField(default=0, read_only=True)
    grand_total = CurrencyField(default=0, read_only=True)
    notes = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   help_text="This will automatically be set "
                                   "to the current user if left blank.")
    objects = SelectRelatedManager(select_related_fields=["created_by",
                                                          "customer",
                                                          "status"])

    def update_tax(self):
        tax = decimal.Decimal(0)
        tax_percentage = get_tax_percentage()
        if self.customer.is_taxable:
            for entry in self.get_entries():
                if entry.is_taxable:
                    tax += entry.total * tax_percentage / 100
        self.total_tax = tax

    def update_totals(self):
        self.update_tax()
        subtotal = decimal.Decimal(0)
        grand_total = decimal.Decimal(0)
        for entry in self.get_entries():
            subtotal += entry.total
        self.subtotal = subtotal
        self.grand_total = subtotal + self.total_tax

    def update_description(self):
        update = get_fill_description()
        if update and not self.description:
            entries = self.get_entries()
            entries = [(entry.description or unicode(entry.item))
                       for entry in entries]
            entries = ", ".join(entries)
            description = u"%s - %s" % (unicode(self.customer), entries)
            if len(description) > 200:  # field length limit
                description = description[:197] + "..."
            self.description = description

    def update(self):
        self.update_totals()
        self.update_description()

    def get_number(self):
        num_zeros = get_invoice_padding()
        return unicode(self.pk).zfill(num_zeros)
    get_number.short_description = "Number"
    get_number.admin_order_field = "id"

    def get_formatted_total(self):
        # i'm hoping there's a nicer way to get the formatted
        # currencyfield that i haven't thought of
        grand_total = self._meta.get_field_by_name("grand_total")[0]
        return grand_total.value_to_string(self)

    def get_change_url(self):
        return get_change_url(self)

    def __unicode__(self):
        status = unicode(getattr(self, "status", ""))
        if status:
            status = " - %s" % status
        return (capfirst(self._meta.verbose_name) + " " +
                unicode(self.get_number()) + status + " - " +
                unicode(self.customer) + " - " + self.get_formatted_total())

    class Meta:
        abstract = True
        ordering = ["-date_created", "-pk"]


class Quote(QuoteInvoiceBase):
    def get_entries(self):
        return self.quoteentry_set.all()

    def create_invoice(self):
        from accounts.helpers import get_date_due
        new_invoice = Invoice()
        fields = [f.name for f in self._meta.fields if f.name != "id"]
        for field in fields:
            setattr(new_invoice, field, getattr(self, field))
        new_invoice.date_due = get_date_due(self.customer)
        new_invoice.save()
        entries = self.get_entries()
        for entry in entries:
            entry.copy_to_invoice(new_invoice)
        return new_invoice


class Invoice(QuoteInvoiceBase):
    status = models.ForeignKey(InvoiceStatus,
                               default=get_or_create_default_invoice_status)
    date_due = models.DateField(default=datetime.date.today)

    def get_entries(self):
        return self.invoiceentry_set.all()

    def delete(self, *args, **kwargs):
        # prevent a delete that will cascade to deposited payments
        check_deposited_payments(self, "invoice__pk")
        super(Invoice, self).delete(*args, **kwargs)

    def update(self):
        super(Invoice, self).update()
        self.update_status()

    def update_status(self):
        if get_auto_invoice_status():
            # this method is usually called right after self.update_totals(),
            # so grand_total has been calculated but not yet stored in the DB.
            # if the calculated total has extra decimal places, it will appear
            # that the payment entered by the user isn't enough to mark the
            # invoice as paid. e.g. grand_total could be calculated to be
            # 10.073, which != the payment of 10.07. the solution here is we
            # first round the just-calculated grand_total in the same way as it
            # will be rounded in the DB.
            # rounding copied from django.db.backends.utils.format_number
            context = decimal.getcontext().copy()
            field = Invoice._meta.get_field_by_name("grand_total")[0]
            context.prec = field.max_digits
            self.grand_total = self.grand_total.quantize(
                decimal.Decimal(".1") ** field.decimal_places, context=context)
            total_payments = self.payment_set.all().aggregate(
                                           total=models.Sum("amount"))["total"]
            paid_status = get_or_create_paid_invoice_status()
            if total_payments >= self.grand_total:
                self.status = paid_status
            elif (self.status == paid_status) and \
                 (total_payments < self.grand_total):
                self.status = get_or_create_default_invoice_status()


class Entry(models.Model):
    item = models.ForeignKey(ProductOrService)
    cost = CurrencyField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2,
                                   default=get_default_quantity)
    description = models.CharField(max_length=200, blank=True)
    discount = CurrencyField(default=0)
    total = CurrencyField()
    is_taxable = models.BooleanField()

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"

    def save(self, *args, **kwargs):
        self.total = self.cost * self.quantity - self.discount
        super(Entry, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.quantity > 1:
            add = " (%s)" % self.quantity
        else:
            add = ""
        return u"%s%s" % (unicode(self.item), add)


class InvoiceEntry(Entry):
    class Meta:
        verbose_name = "sale"
        ordering = ["invoice", "-pk"]

    invoice = models.ForeignKey(Invoice)


def invoiceentry_edit(sender, **kwargs):
    # if editing an invoice entry, both quantity and item could change.
    new_instance = kwargs["instance"]
    if new_instance.pk and not kwargs["raw"]:
        old_instance = sender.objects.get(pk=new_instance.pk)
        if (new_instance.item == old_instance.item and
            new_instance.item.manage_stock):
            quantity_increase = new_instance.quantity - old_instance.quantity
            stock_change = - quantity_increase
            invoiceentry_increment_stock(new_instance, stock_change, "Editing")
        else:
            # for stock puposes changing item is treated as if the old entry
            # was deleted and the new entry was created.
            if old_instance.item.manage_stock:
                invoiceentry_increment_stock(old_instance, old_instance.quantity,
                                             "Editing")
            if new_instance.item.manage_stock:
                change = - new_instance.quantity
                invoiceentry_increment_stock(new_instance, change, "Editing")


def invoiceentry_create(sender, **kwargs):
    # if creating a new invoice entry, update stock by removing quantity used
    if kwargs["created"] and not kwargs["raw"]:
        instance = kwargs["instance"]
        change = - instance.quantity
        invoiceentry_increment_stock(instance, change, "Creating")


def invoiceentry_delete(sender, **kwargs):
    # If deleting an an invoice entry, put the stock back
    instance = kwargs["instance"]
    # if someone alters the quantity field on an invoice entry and also checks
    # "delete", we end up with their newly entered quantity here. i don't see
    # why someone would do that, but IMO if it happens the best thing to do is
    # to ignore the altered quantity. so we re-fetch from the DB just to cover
    # this unusual scenario
    instance = sender.objects.get(pk=instance.pk)
    if instance.item.manage_stock:
        invoiceentry_increment_stock(instance, instance.quantity, "Deleting")


def invoiceentry_increment_stock(entry, change, action):
    if change:
        # fixme: don't hardcode decimal places (issue #165)
        msg = ("%s sale #%s on invoice #%s auto-incremented stock (%+0.2f)." %
                   (action, entry.pk, entry.invoice.pk, change))
        increment_stock(entry.item, change, msg)


models.signals.pre_save.connect(invoiceentry_edit, sender=InvoiceEntry)
models.signals.post_save.connect(invoiceentry_create, sender=InvoiceEntry)
models.signals.pre_delete.connect(invoiceentry_delete, sender=InvoiceEntry)


def increment_stock(item, change, message):
    """
    Increase the amount of an `item` in stock by `change`, creating an admin
    log entry for auditing purposes. If no `message` is supplied, a generic
    one is created.
    """
    item.stock = models.F("stock") + change
    item.save()
    log_stock_change(item, message)


def log_stock_change(item, message, audit_stock=True):
    if "request" in pandora.box:
        ProductOrServiceAdmin = admin.site._registry[ProductOrService]
        # re-fetch from db, see comment for check_negative_stock for infos
        obj = ProductOrService.objects.get(pk=item.pk)
        ProductOrServiceAdmin.log_change(pandora.box["request"], obj, message,
                                         audit_stock=audit_stock)


class QuoteEntry(Entry):
    class Meta:
        verbose_name = "quote item"

    quote = models.ForeignKey(Quote)

    def copy_to_invoice(self, invoice):
        new_invoice_entry = InvoiceEntry()
        skip = ["id", "quote"]
        fields = [f.name for f in self._meta.fields if f.name not in skip]
        for field in fields:
            setattr(new_invoice_entry, field, getattr(self, field))
        new_invoice_entry.invoice = invoice
        new_invoice_entry.save()


class Deposit(models.Model):
    date = models.DateField(default=datetime.date.today)
    total = CurrencyField(default=0, read_only=True)
    comment = models.CharField(max_length=200, blank=True)
    made_by = models.ForeignKey(User, blank=True, null=True, help_text="This "
                                "will automatically be set to the current "
                                "user if left blank.")
    objects = SelectRelatedManager(select_related_fields=["made_by"])

    def update_total(self):
        total = self.payment_set.all().aggregate(
                                         total=models.Sum("amount"))["total"]
        if total:
            self.total = total

    def delete(self, *args, **kwargs):
        # don't delete associated payments, just set their deposit to None.
        self.payment_set.clear()
        super(Deposit, self).delete(*args, **kwargs)

    def __unicode__(self):
        prefix, suffix = get_currency_symbol()
        return u"Deposit of %s%s%s on %s" % (prefix, self.total, suffix,
                                             self.date)

    class Meta:
        ordering = ["-date"]


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice,
                                help_text="Note that only unpaid invoices are "
                                "searchable here.<br/>You can search by "
                                "invoice number, total, and customer name.")
    amount = CurrencyField()
    payment_type = models.ForeignKey(PaymentType)
    date_received = models.DateField(default=datetime.date.today)
    comment = models.CharField(max_length=200, blank=True)
    deposit = models.ForeignKey(Deposit, blank=True, null=True)
    received_by = models.ForeignKey(User, blank=True, null=True,
                                    help_text="This will automatically be "
                                    "set to the current user if left blank.")
    objects = SelectRelatedManager(select_related_fields=["invoice",
                                                          "invoice__status",
                                                          "invoice__customer",
                                                          "payment_type",
                                                          "deposit",
                                                          "received_by"])

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Payment, self).save(*args, **kwargs)
        if self.deposit:
            # update deposit total
            self.deposit.update_total()
            self.deposit.save()

    def delete(self, *args, **kwargs):
        if self.deposit:
            message = "Can't delete: " + unicode(self) + " has been deposited"
            url = get_change_url(self)
            raise DepositedPaymentsException(message, url=url)
        else:
            super(Payment, self).delete(*args, **kwargs)

    def clean(self):
        if hasattr(self, "payment_type"):  # it doesn't on an empty form
            if not self.payment_type.manage_deposits and self.deposit:
                message = ("The payment type '%s' isn't depositable, so this "
                           "payment can't belong to a deposit"
                           % unicode(self.payment_type))
                raise ValidationError(message)

    def get_change_url(self):
        return get_change_url(self)

    def __unicode__(self):
        prefix, suffix = get_currency_symbol()
        return u"%s%s%s %s payment for %s" % (prefix,
                                              self.amount,
                                              suffix,
                                              self.payment_type,
                                              self.invoice)

    class Meta:
        ordering = ["-date_received"]


def payment_presave(sender, **kwargs):
    instance = kwargs["instance"]
    if instance.pk:
        # it might already exist in the DB
        try:
            original = Payment.objects.get(pk=instance.pk)
        except:
            return
        if original.deposit:
            if instance.deposit:
                raise AccountsException("Deposited payments can't be edited. "
                                        "The deposit must first be deleted or "
                                        "removed from the payment.")
            else:
                deposit = original.deposit
                deposit.total -= original.amount
                deposit.save()

models.signals.pre_save.connect(payment_presave, sender=Payment)
