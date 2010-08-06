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
            # todo: better to do getattr(instance, field.name)? if the
            # instance was obtained with select_related(), even better.
            value = field.rel.to.objects.get(id=field.value_from_object(instance))
            value = str(value)
        else:
            value = field.value_to_string(instance)
        data[field.name] = value
    return data


class SettingFetcher(object):
    def __init__(self, setting):
        self.setting = setting

    def get_setting(self):
        return Config.settings.get_setting(self.setting) or ""

    def __call__(self):
        return self.get_setting()


class BooleanFetcher(SettingFetcher):
    def get_setting(self):
        value = super(BooleanFetcher, self).get_setting()
        if value and value.lower() == "true":
            return True
        else:
            return False


class IntegerFetcher(SettingFetcher):
    def get_setting(self):
        try:
            value = int(super(IntegerFetcher, self).get_setting())
        except ValueError, TypeError:
            value = None
        return value


class TaxableDefault(BooleanFetcher):
    def __init__(self, entity):
        self.setting = "new %s taxable by default" % entity


def get_or_create_default_invoice_status():
    desired_status = SettingFetcher("default invoice status")()
    status = None
    if desired_status:
        status, created = InvoiceStatus.objects.get_or_create(
            status=desired_status)
    return status


def get_currency_symbol():
    prefix = ""
    suffix = ""
    symbol = SettingFetcher("currency symbol")()
    after_number = False
    if SettingFetcher("currency symbol after number")().lower() == "true":
        after_number = True
    if after_number:
        suffix = symbol
    else:
        prefix = symbol
    return (prefix, suffix)


def get_tax_percentage():
    tax_percentage = SettingFetcher("tax as percentage")()
    try:
        tax_percentage = decimal.Decimal(tax_percentage)
    except (ValueError, TypeError):
        tax_percentage = 0
        # TODO: warn
    return tax_percentage


# TODO: not currently used
def get_customer_term(plural=False):
    default = "Customer"
    query = "term for customer"
    if plural:
        default = "Customers"
        query += " (plural)"
    result = SettingFetcher(query)()
    if not result:
        result = default
    return result


def get_invoice_number_padding():
    num_zeros = IntegerFetcher("pad invoice numbers with zeros")()
    num_zeros = num_zeros or 0
    return num_zeros


def get_default_item_quantity():
    number = IntegerFetcher("default quantity for items added to invoices")()
    if number is None:
        number = 1
    return number


def get_or_create_default_invoice_term():
    desired_term = IntegerFetcher("default invoice term in days for new customers")()
    default_term = None
    if desired_term is not None:
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
