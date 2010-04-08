from django.db import models

class DollarField(models.DecimalField):
    def __init__(self, **kwargs):
        super(DollarField, self).__init__(self, decimal_places=2,
                                          max_digits=8, **kwargs)

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
    price = DollarField()
    number_in_stock = models.PositiveIntegerField(default=0)
    is_taxable = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = DollarField()
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
    customer = models.ForeignKey(Customer)
    date_created = models.DateField(auto_now_add=True)
    date_due = models.DateField(auto_now=True)
    status = models.ForeignKey(InvoiceStatus)
    comment = models.CharField(max_length=200)
    total = DollarField()
    total_tax = DollarField()
    def __unicode__(self):
        return "Invoice #%s - %s" % (self.id, self.customer)


class InvoiceProductEntry(models.Model):
    def get_default_cost(self):
        return self.product.price
    product = models.ForeignKey(Product)
    cost = DollarField(default=get_default_cost)
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



class InvoiceServiceEntry(models.Model):
    def get_default_cost(self):
        return self.service.price
    service = models.ForeignKey(Service)
    cost = DollarField(default=get_default_cost)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    invoice = models.ForeignKey(Invoice)
    def __unicode__(self):
        return "Invoice Service Entry #%s" % self.id


class Payment(models.Model):
    amount = DollarField()
    payment_method = models.ForeignKey(PaymentMethod)
    invoice = models.ForeignKey(Invoice)
    def __unicode__(self):
        return "%s payment of %s for invoice #%s" % (self.self.payment_method, self.amount, self.invoice.id)
