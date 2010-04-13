import datetime

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    def __unicode__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    number_in_stock = models.PositiveIntegerField(default=0)
    is_taxable = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    def __unicode__(self):
        return self.name



class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name


class InvoiceStatus(models.Model):
    status = models.CharField(max_length=50)
    class Meta:
        verbose_name_plural = "Invoice statuses"
    def __unicode__(self):
        return self.status


class Invoice(models.Model):
    def get_default_status():
        status = InvoiceStatus.objects.filter(status="Created").all()
        if len(status) == 1:
            return status[0]
        else:
            return None
    customer = models.ForeignKey(Customer)
    date_created = models.DateField(default=datetime.date.today)
    date_due = models.DateField(default=datetime.date.today)
    status = models.ForeignKey(InvoiceStatus, default=get_default_status)
    comment = models.CharField(max_length=200, blank=True)
    subtotal = models.DecimalField(max_digits=8,decimal_places=2,
                                   blank=True, default=0)
    total_tax = models.DecimalField(max_digits=8,decimal_places=2,
                                    blank=True, default=0)
    total = models.DecimalField(max_digits=8,decimal_places=2,
                                blank=True, default=0)
    def __unicode__(self):
        return "Invoice #%s - %s" % (str(self.id).zfill(5), self.customer)


class InvoiceProductEntry(models.Model):
    product = models.ForeignKey(Product)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    tax = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    invoice = models.ForeignKey(Invoice)
    def save(self, *args, **kwargs):
        self.product.number_in_stock -= self.quantity
        self.product.save()
        super(InvoiceProductEntry, self).save(*args, **kwargs)
    def delete(self):
        self.product.number_in_stock += self.quantity
        self.product.save()
        super(InvoiceProductEntry, self).delete(*args, **kwargs)
    def __unicode__(self):
        return "Invoice Product Entry #%s" % self.id
    class Meta:
        verbose_name_plural = "Invoice product entries"



class InvoiceServiceEntry(models.Model):
    service = models.ForeignKey(Service)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    invoice = models.ForeignKey(Invoice)
    def __unicode__(self):
        return "Invoice Service Entry #%s" % self.id
    class Meta:
        verbose_name_plural = "Invoice service entries"


class Deposit(models.Model):
    date = models.DateField(default=datetime.date.today)


class Payment(models.Model):
    amount = models.DecimalField(max_digits=8,decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod)
    date_received = models.DateField(default=datetime.date.today)
    invoice = models.ForeignKey(Invoice)
    deposit = models.ForeignKey(Deposit, blank=True)
    def __unicode__(self):
        return "%s payment of %s for invoice #%s" % (self.payment_method,
                                                     self.amount,
                                                     self.invoice.id)
