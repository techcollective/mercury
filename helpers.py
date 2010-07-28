import decimal

from mercury.configuration.models import Config, InvoiceStatus, InvoiceTerm


class SettingFetcher(object):
    def __init__(self, setting):
        self.setting = setting

    def get_setting(self):
        return Config.settings.get_setting(self.setting)


class BooleanFetcher(SettingFetcher):
    def get_setting(self):
        value = super(BooleanFetcher, self).get_setting()
        if value and value.lower() == "true":
            return True
        else:
            return False


class TaxableDefault(BooleanFetcher):
    def __init__(self, entity):
        self.setting = "new %s taxable by default" % entity


def get_or_create_default_invoice_status():
    desired_status = Config.settings.get_setting("default invoice status")
    status = None
    if desired_status:
        status, created = InvoiceStatus.objects.get_or_create(
            status=desired_status)
    return status


def get_currency_symbol():
    prefix = ""
    suffix = ""
    symbol = Config.settings.get_setting("currency symbol")
    after_number = False
    if Config.settings.get_setting("currency symbol after number").lower() == "true":
        after_number = True
    if after_number:
        suffix = symbol
    else:
        prefix = symbol
    return (prefix, suffix)


def get_tax_percentage():
    tax_percentage = Config.settings.get_setting("tax as percentage")
    try:
        tax_percentage = decimal.Decimal(tax_percentage)
    except (ValueError, TypeError):
        tax_percentage = 0
        # TODO: warn
    return tax_percentage


def get_customer_term(plural=False):
    default = "Customer"
    query = "term for customer"
    if plural:
        default = "Customers"
        query += " (plural)"
    result = Config.settings.get_setting(query)
    if not result:
        result = default
    return result


def get_invoice_number_padding():
    num_zeros = Config.settings.get_setting("pad invoice numbers with zeros")
    try:
        result = int(num_zeros)
    except ValueError:
        result = 0
    return result


def get_default_item_quantity():
    number = Config.settings.get_setting("default quantity for items added to invoices")
    try:
        result = int(number)
    except ValueError:
        result = 1
    return result


def get_or_create_default_invoice_term():
    desired_term = Config.settings.get_setting("default invoice term in days for new customers")
    default_term = None
    if desired_term:
        try:
            term = int(desired_term)
        except ValueError:
            pass
        else:
            default_term, created = InvoiceTerm.objects.get_or_create(
                                                days_until_invoice_due=term)
    return default_term
