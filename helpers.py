import decimal

from django.db.models import ForeignKey
from django.core.urlresolvers import reverse

from mercury.configuration.models import Config, InvoiceStatus, InvoiceTerm


get_setting = Config.settings.get_setting
get_boolean_setting = Config.settings.get_boolean_setting
get_integer_setting = Config.settings.get_integer_setting


class Callable(object):
    def __init__(self, method, args=None, kwargs=None):
        self.method = method
        self.args = args or []
        self.kwargs = kwargs or {}

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
    default = """Please set the "currency symbol" setting"""
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


def get_customer_taxable():
    return get_boolean_setting("new customers taxable by default",
                               default=True)


def get_manage_stock():
    return get_boolean_setting(
                     "manage stock of new products and services by default",
                     default=True)


def get_product_taxable():
    return get_boolean_setting("new products and services taxable by default",
                               default=True)


def get_default_quantity():
    return get_integer_setting("default quantity for items added to invoices",
                               default=1)


def get_invoice_padding():
    return get_integer_setting("pad invoice numbers with zeros", default=0)


def get_display_paid():
    return get_boolean_setting("display paid invoices on customer page",
                               default=True)


def get_fill_description():
    return get_boolean_setting(
                        "automatically fill in blank invoice description",
                        default=True)
