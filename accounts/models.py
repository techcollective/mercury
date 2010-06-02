import datetime
import decimal

from django.db import models

from mercury.configuration.models import PaymentMethod, InvoiceStatus
from mercury.accounts.fields import CurrencyField
from mercury.helpers import get_currency_symbol, \
     get_or_create_default_invoice_status, get_tax_percentage, \
     get_taxable_default


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_taxable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class ProductOrService(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()
    number_in_stock = models.PositiveIntegerField(default=0)
    manage_stock = models.BooleanField(default=True, help_text="Uncheck this \
                                       to prevent the stock count being \
                                       changed when this product is added to \
                                       an invoice.")
    is_taxable = models.BooleanField(default=True)

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

    def update_tax(self, *args, **kwargs):
        subtotal = 0
        tax = 0
        grand_total = 0
        tax_percentage = get_tax_percentage()
        for product in self.invoiceproductentry_set.all():
            subtotal += product.cost
            tax += product.cost * tax_percentage / 100
        for service in self.invoiceserviceentry_set.all():
            subtotal += service.cost
        grand_total = subtotal + tax
        self.total_tax = tax
        self.subtotal = subtotal
        self.grand_total = grand_total
        self.save()

    class Meta:
        abstract = True


class Quote(QuoteInvoiceBase):
    def __unicode__(self):
        return "Quote #%s - %s" % (str(self.id).zfill(5), self.customer)


class Invoice(QuoteInvoiceBase):
    status = models.ForeignKey(InvoiceStatus,
                               default=get_or_create_default_invoice_status)
    # TODO: default should be customizable, default=in a month
    date_due = models.DateField(default=datetime.date.today)

    def __unicode__(self):
        return "Invoice #%s - %s" % (str(self.id).zfill(5), self.customer)


class Entry(models.Model):
    cost = CurrencyField()
    discount = CurrencyField()
    tax = CurrencyField(read_only=True)
    total = CurrencyField(read_only=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=1)

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"


class InvoiceProductEntry(ProductEntry):
    invoice = models.ForeignKey(Invoice)

    def save(self, *args, **kwargs):
        if self.product.manage_stock:
            self.product.number_in_stock -= self.quantity
            self.product.save()
        super(InvoiceProductEntry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.product.manage_stock:
            self.product.number_in_stock += self.quantity
            self.product.save()
        super(InvoiceProductEntry, self).delete(*args, **kwargs)

    def __unicode__(self):
        return "Product Entry #%s on %s" % (self.id, str(self.invoice))


class ServiceEntry(InvoiceEntry):
    service = models.ForeignKey(Service)

    class Meta:
        abstract = True
        verbose_name_plural = "Service entries"


class QuoteServiceEntry(ServiceEntry):
    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        return "Service Entry #%s on %s" % (self.id, str(self.quote))


class InvoiceServiceEntry(ServiceEntry):
    invoice = models.ForeignKey(Invoice)

    def __unicode__(self):
        return "Service Entry #%s on %s" % (self.id, str(self.invoice))


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
