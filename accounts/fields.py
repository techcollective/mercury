from django.db import models
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.forms import fields

from mercury.helpers import get_currency_symbol, get_currency_decimal_places


class CurrencyInputWidget(Widget):
    """
    Widget class for currency. Displays a text input with a currency symbol
    positioned according to user defined settings.
    """
    input_type = "text"

    def _get_render_result(self, name, value, attrs):
        prefix, suffix = get_currency_symbol()
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return (prefix, final_attrs, suffix)

    def render(self, name, value, attrs=None):
        prefix, final_attrs, suffix = self._get_render_result(name, value,
                                                              attrs)
        return mark_safe(u'%s <input%s /> %s' % (prefix, flatatt(final_attrs),
                                                 suffix))


class ReadOnlyCurrencyInputWidget(CurrencyInputWidget):
    def render(self, name, value, attrs=None):
        prefix, final_attrs, suffix = self._get_render_result(name, value,
                                                              attrs)
        final_attrs.update({"readonly": ""})
        return mark_safe(u'%s <input%s /> %s' % (prefix, flatatt(final_attrs),
                                                 suffix))


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
        prefix, suffix = get_currency_symbol()
        value = self.value_from_object(obj)
        sub = "%" + "0.%sf" % get_currency_decimal_places()
        value = sub % value
        return "%s%s%s" % (prefix, value, suffix)
