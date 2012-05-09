from django.db import models
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.forms import fields

from mercury.helpers import add_currency_symbol, get_currency_decimal_places


class CurrencyInputWidget(Widget):
    """
    Widget class for currency. Displays a text input with a currency symbol
    positioned according to user defined settings.
    """
    input_type = "text"

    def _get_final_attrs(self, name, value, attrs):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return final_attrs

    def render(self, name, value, attrs=None):
        final_attrs = self._get_final_attrs(name, value, attrs)
        return mark_safe(add_currency_symbol(u' <input%s /> ' %
                                             flatatt(final_attrs)))


class ReadOnlyCurrencyInputWidget(CurrencyInputWidget):
    def _get_final_attrs(self, *args, **kwargs):
        final_attrs = super(ReadOnlyCurrencyInputWidget,
                            self)._get_final_attrs(*args, **kwargs)
        final_attrs.update({"readonly": ""})
        return final_attrs


class CurrencyFormField(fields.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"widget": CurrencyInputWidget})
        super(CurrencyFormField, self).__init__(*args, **kwargs)


class ReadOnlyCurrencyFormField(fields.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"widget": ReadOnlyCurrencyInputWidget})
        super(ReadOnlyCurrencyFormField, self).__init__(*args, **kwargs)


class CurrencyField(models.DecimalField):
    def __init__(self, read_only=False, *args, **kwargs):
        kwargs.update({"decimal_places": 2, "max_digits": 15})
        if read_only:
            self._formfield_class = ReadOnlyCurrencyFormField
        else:
            self._formfield_class = CurrencyFormField
        super(CurrencyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": self._formfield_class}
        defaults.update(kwargs)
        return super(CurrencyField, self).formfield(**defaults)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        # fixme: don't format decimal places here (issue #165)
        sub = "%" + "0.%sf" % get_currency_decimal_places()
        value = sub % value
        return add_currency_symbol(value)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^accounts\.fields\.CurrencyField"])
