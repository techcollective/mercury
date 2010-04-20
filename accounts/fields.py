from django.db import models
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.forms import fields

from configuration.models import Config


class CurrencyInputWidget(Widget):
    """
    Widget class for currency. Displays a text input with a currency symbol
    positioned according to user defined settings.
    """
    input_type = "text"

    def render(self, name, value, attrs=None):
        prefix = ""
        suffix = ""
        symbol = Config.settings.get_setting("currency symbol")
        if not symbol:
            symbol = "please set the 'currency symbol' setting"
        after_number = False
        if Config.settings.get_setting("currency symbol after number").lower() == "true":
            after_number = True
        if after_number:
            suffix = symbol
        else:
            prefix = symbol
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'%s <input%s /> %s' % (prefix, flatatt(final_attrs), suffix))


class CurrencyFormField(fields.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"widget": CurrencyInputWidget})
        super(CurrencyFormField, self).__init__(*args, **kwargs)


class CurrencyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"decimal_places": 2, "max_digits": 15})
        super(CurrencyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": CurrencyFormField}
        defaults.update(kwargs)
        return super(CurrencyField, self).formfield(**defaults)
