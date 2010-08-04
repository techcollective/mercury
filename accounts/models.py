import datetime
import decimal

from django.db import models

from mercury.configuration.models import (PaymentMethod,
                                          InvoiceStatus,
                                          InvoiceTerm)
from mercury.accounts.fields import CurrencyField
from mercury.helpers import (TaxableDefault,
                             BooleanFetcher,
                             get_currency_symbol,
                             get_or_create_default_invoice_status,
                             get_tax_percentage,
                             get_customer_term,
                             get_invoice_number_padding,
                             get_default_item_quantity,
                             get_or_create_default_invoice_term)


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_taxable = models.BooleanField(
        default=TaxableDefault("customers").get_setting)
    default_payment_terms = models.ForeignKey(InvoiceTerm,
                                    default=get_or_create_default_invoice_term)

    def __unicode__(self):
        return self.name

    # TODO: how can this work? custom admin template?
    #class Meta:
    #    verbose_name = get_customer_term()
    #    verbose_name_plural = get_customer_term(plural=True)


class ProductOrService(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()
    number_in_stock = models.PositiveIntegerField(default=0)
    manage_stock = models.BooleanField(default=BooleanFetcher("manage stock " +
                                       "of new products and services " +
                                       "by default").get_setting)
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

    def update_tax(self):
        tax = 0
        tax_percentage = get_tax_percentage()
        if self.customer.is_taxable:
            for entry in self.get_entries():
                if entry.item.is_taxable:
                    tax += entry.total * tax_percentage / 100
        self.total_tax = tax

    def update_totals(self, *args, **kwargs):
        self.update_tax()
        subtotal = 0
        grand_total = 0
        for entry in self.get_entries():
            subtotal += entry.total
        self.subtotal = subtotal
        self.grand_total = subtotal + self.total_tax
        self.save()

    def get_number(self):
        num_zeros = get_invoice_number_padding()
        return str(self.id).zfill(num_zeros)

    class Meta:
        abstract = True


class Quote(QuoteInvoiceBase):
    def __unicode__(self):
        return "Quote #%s - %s" % (self.get_number(), self.customer)

    def get_entries(self):
        return self.quoteentry_set.all()


class Invoice(QuoteInvoiceBase):
    status = models.ForeignKey(InvoiceStatus,
                               default=get_or_create_default_invoice_status)
    date_due = models.DateField(default=datetime.date.today)

    def __unicode__(self):
        return "Invoice #%s - %s" % (self.get_number(), self.customer)

    def get_entries(self):
        return self.invoiceentry_set.all()


class Entry(models.Model):
    item = models.ForeignKey(ProductOrService)
    cost = CurrencyField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2,
                                   default=get_default_item_quantity)
    discount = CurrencyField(default=0)
    total = CurrencyField()

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"

    def save(self, *args, **kwargs):
        self.total = self.cost * self.quantity - self.discount
        if self.item.manage_stock:
            if self.item.number_in_stock > 0:
                self.item.number_in_stock -= self.quantity
                self.item.save()
        super(Entry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.item.manage_stock:
            self.item.number_in_stock += self.quantity
            self.item.save()
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
        prefix, suffix = get_currency_symbol()
        return "Deposit of %s%s%s on %s" % (prefix, self.total(), suffix,
                                            self.date)


class Payment(models.Model):
    amount = CurrencyField()
    payment_method = models.ForeignKey(PaymentMethod)
    date_received = models.DateField(default=datetime.date.today)
    invoice = models.ForeignKey(Invoice)
    deposit = models.ForeignKey(Deposit, blank=True, null=True)

    def __unicode__(self):
        prefix, suffix = get_currency_symbol()
        return "%s%s%s %s payment for %s" % (prefix,
                                                      self.amount,
                                                      suffix,
                                                      self.payment_method,
                                                      str(self.invoice))
