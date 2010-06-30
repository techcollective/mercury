import datetime
import decimal

from django.db import models

from mercury.configuration.models import PaymentMethod, InvoiceStatus, Config
from mercury.accounts.fields import CurrencyField
from mercury.helpers import get_currency_symbol, \
     get_or_create_default_invoice_status, get_tax_percentage, \
     TaxableDefault


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_taxable = models.BooleanField(
        default=TaxableDefault("customer").get_setting)
    default_payment_terms = models.ForeignKey(InvoiceTerms)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = Customer.get_term()
        verbose_name_plural = get_term(plural=True)


class ProductOrService(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()
    number_in_stock = models.PositiveIntegerField(default=0)
    manage_stock = models.BooleanField(default=True, help_text="Uncheck this \
                                       to prevent the stock count being \
                                       changed when this item is added to \
                                       an invoice.")
    is_taxable = models.BooleanField(
        default=TaxableDefault("products and services").get_setting)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products and services"


class QuoteInvoiceBase(models.Model):
    customer = models.ForeignKey(Customer)
    date_created = models.DateField(default=datetime.date.today)
    comment = models.CharField(max_length=200, blank=True)
    subtotal = CurrencyField(default=0, read_only=True)
    total_tax = CurrencyField(default=0, read_only=True)
    grand_total = CurrencyField(default=0, read_only=True)

    def update_totals(self, *args, **kwargs):
        subtotal = 0
        tax = 0
        grand_total = 0

        for item in self.invoiceentry_set.all():
            subtotal += item.cost
            tax += item.tax
        grand_total = subtotal + tax
        self.total_tax = tax
        self.subtotal = subtotal
        self.grand_total = grand_total
        self.save()

    class Meta:
        abstract = True


class Quote(QuoteInvoiceBase):
    def __unicode__(self):
        # TODO: make zero padding a setting
        return "Quote #%s - %s" % (str(self.id).zfill(5), self.customer)


class Invoice(QuoteInvoiceBase):
    status = models.ForeignKey(InvoiceStatus,
                               default=get_or_create_default_invoice_status)
    # TODO: auto-add customer's terms to date due
    date_due = models.DateField(default=datetime.date.today)

    def __unicode__(self):
        # TODO: make zero padding a setting
        return "Invoice #%s - %s" % (str(self.id).zfill(5), self.customer)


class Entry(models.Model):
    item = models.ForeignKey(ProductOrService)
    cost = CurrencyField()
    discount = CurrencyField()
    tax = CurrencyField(read_only=True)
    total = CurrencyField(read_only=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=1)

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"

    def save(self, *args, **kwargs):
        tax_percentage = get_tax_percentage()
        # FIXME calculate and save tax.
        if self.product.manage_stock:
            self.product.number_in_stock -= self.quantity
            self.product.save()
        super(Entry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.product.manage_stock:
            self.product.number_in_stock += self.quantity
            self.product.save()
        super(Entry, self).delete(*args, **kwargs)


class InvoiceEntry(Entry):
    invoice = models.ForeignKey(Invoice)

    def __unicode__(self):
        return "Entry #%s on %s" % (self.id, str(self.invoice))


class QuoteEntry(Entry):
    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        return "Entry #%s on %s" % (self.id, str(self.quote))


class Deposit(models.Model):
    date = models.DateField(default=datetime.date.today)

    def total(self):
        return sum([x.amount for x in self.payment_set.all()])

    def __unicode__(self):
        return "Deposit of %s on %s" % (self.total(), self.date)


class Payment(models.Model):
    amount = CurrencyField()
    payment_method = models.ForeignKey(PaymentMethod)
    date_received = models.DateField(default=datetime.date.today)
    invoice = models.ForeignKey(Invoice)
    deposit = models.ForeignKey(Deposit, blank=True, null=True)

    def __unicode__(self):
        return "%s payment of %s for invoice #%s" % (self.payment_method,
                                                     self.amount,
                                                     self.invoice.id)
