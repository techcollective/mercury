import datetime

from django.db import models
from configuration.models import PaymentMethod, InvoiceStatus, Config
from accounts.fields import CurrencyField


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.name


class Product(models.Model):
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


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()

    def __unicode__(self):
        return self.name


class Invoice(models.Model):
    def get_default_status():
        desired_status = Config.settings.get_setting("default invoice status")
        status = InvoiceStatus.objects.filter(status=desired_status).all()
        default_status = None
        if status:
            default_status = status[0]
        elif desired_status:
            status = InvoiceStatus()
            status.status = desired_status
            status.save()
            default_status = status
        return default_status

    customer = models.ForeignKey(Customer)
    date_created = models.DateField(default=datetime.date.today)
    date_due = models.DateField(default=datetime.date.today)
    status = models.ForeignKey(InvoiceStatus, default=get_default_status)
    comment = models.CharField(max_length=200, blank=True)
    subtotal = CurrencyField()
    total_tax = CurrencyField()
    total = CurrencyField()

    def __unicode__(self):
        return "Invoice #%s - %s" % (str(self.id).zfill(5), self.customer)


class InvoiceProductEntry(models.Model):
    product = models.ForeignKey(Product)
    cost = CurrencyField()
    quantity = models.PositiveIntegerField(default=1)
    tax = models.DecimalField(max_digits=5, decimal_places=2, blank=True,
                              default=0)
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
        return "Invoice Product Entry #%s" % self.id

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product entries"


class InvoiceServiceEntry(models.Model):
    service = models.ForeignKey(Service)
    cost = CurrencyField()
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    invoice = models.ForeignKey(Invoice)

    def __unicode__(self):
        return "Invoice Service Entry #%s" % self.id

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Service entries"


class Deposit(models.Model):
    date = models.DateField(default=datetime.date.today)

    def total(self):
        return sum([x.amount for x in self.payment_set.all()])

    def __unicode__(self):
        return "Deposit of %s" % self.total()


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
