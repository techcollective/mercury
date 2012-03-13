from django.db import models

from configuration.exceptions import NoSuchSetting


class PaymentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    manage_deposits = models.BooleanField(help_text="Check this if you want " +
                                          "payments received with this " +
                                          "type to be managed by the " +
                                          "deposit system")

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        from mercury.helpers import check_deposited_payments
        check_deposited_payments(self, "payment_type__pk")
        super(PaymentType, self).delete(*args, **kwargs)


class InvoiceStatus(models.Model):
    status = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Invoice status options"

    def __unicode__(self):
        return self.status

    def delete(self, *args, **kwargs):
        from mercury.helpers import check_deposited_payments
        check_deposited_payments(self, "invoice__status__pk")
        super(InvoiceStatus, self).delete(*args, **kwargs)


class InvoiceTerm(models.Model):
    days_until_invoice_due = models.PositiveIntegerField(default=0, unique=True)

    def __unicode__(self):
        if self.days_until_invoice_due > 0:
            name = "Payment due in %s days" % self.days_until_invoice_due
        else:
            name = "Payment due on receipt"
        return name

    def delete(self, *args, **kwargs):
        from mercury.helpers import check_deposited_payments
        check_deposited_payments(self,
                                "invoice__customer__default_payment_terms__pk")
        super(InvoiceTerm, self).delete(*args, **kwargs)


class Image(models.Model):
    image_name = models.CharField(max_length=50, unique=True)
    path = models.ImageField(upload_to="images")

    def __unicode__(self):
        return self.image_name


class Template(models.Model):
    name = models.CharField(max_length=50, unique=True)
    template = models.TextField(help_text="The invoice template is processed "
                                          "using the django template language "
                                          "and should yield valid html.",
                                blank=True)
    # not sure if this is the right approach
    #image = models.ForeignKey(Image, null=True, blank=True)

    def __unicode__(self):
        return self.name


class ConfigManager(models.Manager):
    def get_setting(self, setting_name, **kwargs):
        """
        Returns the value of the specified setting, or the value of the
        'default' keyword argument if the setting is missing.
        Raises NoSuchSetting if the setting is missing and the 'default' arg
        is not supplied.
        """
        try:
            value = self.get(name=setting_name.lower()).value
        except Config.DoesNotExist:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise NoSuchSetting(setting_name)
        return value

    def get_boolean_setting(self, setting_name, **kwargs):
        """
        Returns True if the specified setting is set to "true" (case
        insensitive), False otherwise, and the value of the 'default' argument
        if the specified setting is missing.
        Raises NoSuchSetting if the setting is missing and the 'default' arg
        is not supplied.
        """
        value = self.get_setting(setting_name, **kwargs)
        if str(value).lower() == "true":
            value = True
        else:
            value = False
        return value

    def get_integer_setting(self, setting_name, **kwargs):
        """
        Returns int() of the specified setting. The 'default' keyword argument
        (or None if it's not supplied) is returned if the setting is an
        invalid int literal.
        Raises NoSuchSetting if the setting is missing and 'default' arg
        is not supplied.
        """
        try:
            value = int(self.get_setting(setting_name, **kwargs))
        except (ValueError, TypeError):
            if "default" in kwargs:
                value = kwargs["default"]
            else:
                value = None
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
