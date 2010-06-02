import decimal

from mercury.configuration.models import Config, InvoiceStatus


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


def get_taxable_default(entity):
    taxable = Config.settings.get_setting("%s taxable by default")
    if taxable and taxable.lower() == "true":
        return True
    else:
        return False


def get_default_customer_taxable():
