import decimal

from django.db.models import ForeignKey
from django.core.urlresolvers import reverse

from mercury.configuration.models import Config, InvoiceStatus, InvoiceTerm


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


def get_setting(setting, default=""):
    if not isinstance(default, str):
        # make sure the default arg is the right type
        raise TypeError("The 'default' argument must be a string")
    value = Config.settings.get_setting(setting)
    if value is None:
        # this means the setting didn't exist
        value = default
    return value


def get_boolean_setting(setting, default=False):
    if not isinstance(default, bool):
        # make sure the default arg is the right type
        raise TypeError("The 'default' argument must be True or False")
    value = get_setting(setting, default="")
    if value.lower() == "true":
        value = True
    else:
        value = default
    return value


def get_integer_setting(setting, default=0):
    # make sure the default arg is the right type
    if not isinstance(default, int):
        raise TypeError("The 'default' argument must be an int")
    value = get_setting(setting, default="")
    try:
        value = int(value)
    except ValueError, TypeError:
        value = default
    return value


class TaxableDefault(object):
    def __init__(self, entity, default=False):
        self.setting = "new %s taxable by default" % entity
        self.default = default

    def __call__(self):
        return get_boolean_setting(self.setting, default=self.default)


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
    symbol = get_setting("currency symbol")
    after_number = False
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


def get_invoice_number_padding():
    return get_integer_setting("pad invoice numbers with zeros", default=0)


def get_default_item_quantity():
    return get_integer_setting("default quantity for items added to invoices",
                               default=1)


def get_or_create_default_invoice_term():
    desired_term = get_integer_setting("default invoice term in days for new customers")
    default_term = None
    if desired_term:
            default_term, created = InvoiceTerm.objects.get_or_create(
                                           days_until_invoice_due=desired_term)
    return default_term


def get_max_customer_invoices():
    max_invoices = IntegerFetcher("max number of invoices on customer detail page")()
    if max_invoices is None:
        max_invoices = 20
    return max_invoices


def get_or_create_paid_invoice_status():
    desired_status = SettingFetcher("status for paid invoices")()
    desired_status = desired_status or "Paid"
    status, created = InvoiceStatus.objects.get_or_create(
                                                        status=desired_status)
    return status


def get_currency_decimal_places():
    places = IntegerFetcher("number of decimal places for currency display")()
    if places is None:
        places = 2
    if places < 0:
        places = 2
    return places
