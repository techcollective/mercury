import decimal

from django.db.models import ForeignKey
from django.core.urlresolvers import reverse

from mercury.configuration.models import Config, InvoiceStatus, InvoiceTerm


class Callable(object):
    def __init__(self, method, args, kwargs={}):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.method(*args, **kwargs)


def get_model_info(model):
    return (model._meta.app_label, model._meta.module_name)


def get_changelist_url(model):
    info = get_model_info(model)
    return reverse("admin:%s_%s_changelist" % info)


def get_change_url(instance):
    info = get_model_info(instance)
    return reverse("admin:%s_%s_change" % info, args=[instance.pk])


def model_to_dict(instance):
    data = {}
    for field in instance._meta.fields:
        if isinstance(field, ForeignKey):
            value = getattr(instance, field.name)
            value = str(value)
        else:
            value = field.value_to_string(instance)
        data[field.name] = value
    return data


def get_setting(setting, default=None):
    """
    Returns the value of the specified setting, or the value of the 'default'
    argument if the setting is missing.
    """
    value = Config.settings.get_setting(setting)
    if value is None:
        # this means the setting didn't exist
        value = default
    return value


def get_boolean_setting(setting, default=None):
    """
    Returns True if the specified setting is set to "true" (case insensitive),
    or the value of the 'default' argument otherwise.
    """
    value = get_setting(setting, default=default)
    if str(value).lower() == "true":
        value = True
    else:
        value = default
    return value


def get_integer_setting(setting, default=None):
    """
    Returns an int of the specified setting, or the value of the 'default'
    argument if the setting is missing or an invalid int literal.
    """
    value = get_setting(setting, default=default)
    try:
        value = int(value)
    except ValueError, TypeError:
        value = default
    return value


def get_or_create_default_invoice_status():
    desired_status = get_setting("default invoice status")
    status = None
    if desired_status:
        status, created = InvoiceStatus.objects.get_or_create(
            status=desired_status)
    return status


def get_currency_symbol():
    prefix = ""
    suffix = ""
    default = "Please set the \"currency symbol\" setting"
    symbol = get_setting("currency symbol", default=default)
    if get_boolean_setting("currency symbol after number"):
        suffix = symbol
    else:
        prefix = symbol
    return (prefix, suffix)


def get_tax_percentage():
    tax_percentage = get_setting("tax as percentage")
    try:
        tax_percentage = decimal.Decimal(tax_percentage)
    except (ValueError, TypeError):
        tax_percentage = 0
    return tax_percentage


def get_or_create_default_invoice_term():
    setting = "default invoice term in days for new customers"
    desired_term = get_integer_setting(setting)
    default_term = None
    if desired_term is not None:
            default_term, created = InvoiceTerm.objects.get_or_create(
                                           days_until_invoice_due=desired_term)
    return default_term


def get_max_customer_invoices():
    setting = "max number of invoices on customer detail page"
    return get_integer_setting(setting, default=20)


def get_or_create_paid_invoice_status():
    desired_status = get_setting("status for paid invoices", default="Paid")
    status, created = InvoiceStatus.objects.get_or_create(
                                                        status=desired_status)
    return status


def get_currency_decimal_places():
    setting = "number of decimal places for currency display"
    default = 2
    places = get_integer_setting(setting, default=default)
    if places < 0:
        places = default
    return places
