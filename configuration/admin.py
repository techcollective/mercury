from configuration.models import (PaymentType,
                                  InvoiceStatus,
                                  InvoiceTerm,
                                  Template,
                                  Config,
                                  Image,
                                  ProductOrServiceTag,
                                  CustomerTag)
from mercury.admin import MercuryAdmin, site


class ConfigAdmin(MercuryAdmin):
    search_fields = ["name"]


# All models must have MercuryAdmin (or subclasses) ModelAdmins
# so that global list_per_page and other functionality works.
site.register(PaymentType, MercuryAdmin)
site.register(InvoiceStatus, MercuryAdmin)
site.register(InvoiceTerm, MercuryAdmin)
site.register(ProductOrServiceTag, MercuryAdmin)
site.register(CustomerTag, MercuryAdmin)
site.register(Template, MercuryAdmin)
site.register(Config, ConfigAdmin)
site.register(Image, MercuryAdmin)
