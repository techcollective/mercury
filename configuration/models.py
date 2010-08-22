from django.db import models

from tinymce.models import HTMLField


class PaymentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    manage_deposits = models.BooleanField(help_text="Check this if you want " +
                                          "payments received with this " +
                                          "type to be managed by the " +
                                          "deposit system")

    def __unicode__(self):
        return self.name


class InvoiceStatus(models.Model):
    status = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Invoice status options"

    def __unicode__(self):
        return self.status


class InvoiceTerm(models.Model):
    days_until_invoice_due = models.PositiveIntegerField(default=0, unique=True)

    def __unicode__(self):
        if self.days_until_invoice_due > 0:
            name = "Payment due in %s days" % self.days_until_invoice_due
        else:
            name = "Payment due on receipt"
        return name


class Template(models.Model):
    name = models.CharField(max_length=50, unique=True)
    template = HTMLField(help_text="The invoice template is " +
                                   "processed using the django template " +
                                   "language and should yield valid html.")

    def __unicode__(self):
        return self.name


class ConfigManager(models.Manager):
    def get_setting(self, setting_name, default=None):
        """
        Returns the value of the specified setting, or the value of the 'default'
        argument if the setting is missing.
        """
        try:
            value = self.get(name=setting_name).value
        except Config.DoesNotExist:
            value = default
        return value


    def get_boolean_setting(self, setting_name, default=False):
        """
        Returns True if the specified setting is set to "true" (case insensitive),
        False otherwise, and the value of the 'default' argument if the specified
        setting doesn't exist.
        """
        value = self.get_setting(setting_name)
        if value is None:
            value = default
        elif str(value).lower() == "true":
            value = True
        else:
            value = False
        return value


    def get_integer_setting(self, setting_name, default=None):
        """
        Returns int() of the specified setting, or the value of the 'default'
        argument if the setting is missing or an invalid int literal.
        """
        value = self.get_setting(setting_name)
        try:
            value = int(value)
        except ValueError, TypeError:
            value = default
        return value





class Config(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=200, blank=True)
    settings = ConfigManager()

    def __unicode__(self):
        return "'%s' is set to '%s'" % (self.name, self.value)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Config, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "System Setting"
