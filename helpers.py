import decimal

from django.db.models import ForeignKey
from django.core.urlresolvers import reverse
from django.utils.text import capfirst

from mercury.configuration.models import Config, InvoiceStatus, InvoiceTerm
from mercury.accounts.exceptions import DepositedPaymentsException


get_setting = Config.settings.get_setting
get_boolean_setting = Config.settings.get_boolean_setting
get_integer_setting = Config.settings.get_integer_setting


def check_deposited_payments(obj, field_lookup):
    """
    Checks if applying field_lookup to the Payment model returns any deposited
    payments. If so, it raises DepositedPaymentsException.
    """
    from mercury.accounts.models import Payment
    filter = {field_lookup: obj.pk}
    num_payments = Payment.objects.filter(**filter).exclude(
                                                        deposit=None).count()
    if num_payments != 0:
        url = get_changelist_url(Payment) + "?" + field_lookup + "=%s" % obj.pk
        message = ("Can't delete: " + capfirst(obj._meta.verbose_name) + " \""
                   + str(obj) + "\" is linked to")
        if num_payments == 1:
            message += " one deposited payment."
        else:
            message += " %s deposited payments." % num_payments
        raise DepositedPaymentsException(message, url=url)


def refresh(instance):
    """
    Returns the same model instance fresh from the DB.
    """
    return instance.__class__.objects.get(pk=instance.pk)


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
    desired_status = get_setting("default status for new invoices",
                                 default=None)
    if desired_status is not None:
        desired_status, created = InvoiceStatus.objects.get_or_create(
                                                     status=desired_status)
    return desired_status


def get_currency_symbol():
    prefix = ""
    suffix = ""
    default = """Please set the "currency symbol" setting"""
    symbol = get_setting("currency symbol", default=default)
    if get_boolean_setting("currency symbol after number", default=False):
        suffix = symbol
    else:
        prefix = symbol
    return (prefix, suffix)


def get_tax_percentage():
    tax_percentage = get_setting("tax as percentage", default=0)
    try:
        tax_percentage = decimal.Decimal(tax_percentage)
    except (ValueError, TypeError):
        tax_percentage = 0
    return tax_percentage


def get_or_create_default_invoice_term():
    setting = "default invoice term in days for new customers"
    desired_term = get_integer_setting(setting, default=None)
    if desired_term is not None:
            desired_term, created = InvoiceTerm.objects.get_or_create(
                                           days_until_invoice_due=desired_term)
    return desired_term


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


def get_negative_stock():
    return get_boolean_setting("allow negative stock counts", default=False)


def get_auto_invoice_status():
    return get_boolean_setting(
                        "update invoice status when full payment is received",
                        default=True)


def get_template_name(entity):
    return get_setting("%s template" % entity)


def get_items_per_page():
    return get_integer_setting("list items per page (requires restart)",
                               default=50)
