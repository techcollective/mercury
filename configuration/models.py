from django.db import models


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class InvoiceStatus(models.Model):
    status = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Invoice status options"

    def __unicode__(self):
        return self.status


class InvoiceTerm(models.Model):
    days_until_invoice_due = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        if self.days_until_invoice_due > 0:
            name = "Payment due in %s days" % self.days_until_invoice_due
        else:
            name = "Payment due on receipt"
        return name


class InvoiceTemplate(models.Model):
    html = models.TextField()


class ConfigManager(models.Manager):
    def get_setting(self, setting_name):
        try:
            value = self.get(name=setting_name).value
        except Config.DoesNotExist:
            value = ""
        return value


class Config(models.Model):
    name = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=200)
    settings = ConfigManager()

    def __unicode__(self):
        return "'%s' is set to '%s'" % (self.name, self.value)

    class Meta:
        verbose_name = "System Setting"
