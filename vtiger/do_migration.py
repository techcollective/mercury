#!/usr/bin/env python

import sys
import os
import logging
from optparse import OptionParser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ["DJANGO_SETTINGS_MODULE"] = "mercury.settings"

from django.db import transaction
from mercury.accounts.models import *
from mercury.vtiger.models import *

parser = OptionParser()
parser.add_option("-n",
                  "--dry-run",
                  action="store_true",
                  dest="dry_run",
                  help="Don't actully save into the mercury db. Note that duplicates are checked against the mercury db, so if it's empty no duplicate warnings will be printed.",
                  default=False
                  )
parser.add_option("-d",
                  "--debug",
                  action="store_true",
                  dest="debug",
                  help="Show lots of output",
                  default=False
                  )
(options, args) = parser.parse_args()

DRY_RUN = options.dry_run

logging.basicConfig()
logging = logging.getLogger(sys.argv[0])

if options.debug:
    logging.setLevel(logging.DEBUG)

@transaction.commit_on_success
def migrate():
    # products
    for product in VtigerProducts.objects.all():
        try:
            if product.productid.deleted == 1:
                logging.debug("not creating deleted product \"%s\"" % product.productname)
            else:
                try:
                    duplicate = ProductOrService.objects.get(name=product.productname)
                    logging.warning("ignoring duplicate product name %s" % product.productname)
                    continue
                except:
                    pass
                new_product = ProductOrService()
                new_product.name = product.productname
                new_product.price = product.unit_price or None
                new_product.manage_stock = False
                new_product.is_taxable = True
                if not DRY_RUN:
                    new_product.save()
        except Exception as e:
            logging.error("error creating product %s: %s" % (product.productname, e))

    # services
    for service in VtigerService.objects.all():
        try:
            if service.serviceid.deleted == 1:
                logging.debug("not creating deleted service \"%s\"" % product.productname)
            else:
                try:
                    duplicate = ProductOrService.objects.get(name=service.servicename)
                    logging.warning("ignoring duplicate service name %s" % service.servicename)
                    continue
                except:
                    pass
                new_service = ProductOrService()
                new_service.name = service.servicename
                new_service.price = service.unit_price or None
                new_service.manage_stock = False
                new_service.is_taxable = False
                if not DRY_RUN:
                    new_service.save()
        except Exception as e:
            logging.error("error creating service %s: %s" % (service.servicename, e))

    # accounts
    for account in VtigerAccount.objects.all():
        try:
            if account.accountid.deleted == 1:
                logging.debug("not creating deleted customer %s" % account.accountname)
            else:
                try:
                    duplicate = Customer.objects.get(name=account.accountname)
                    logging.warning("creating duplicate customer name %s" % account.accountname)
                except:
                    pass
                new_customer = Customer()
                new_customer.name = account.accountname or ""
                new_customer.phone_number = account.phone or ""
                if account.otherphone:
                    new_customer.phone_number += " or %s" % account.otherphone
                new_customer.email_address = account.email1 or account.email2 or ""
                address = account.vtigeraccountbillads_set.all()[0]
                new_customer.address = address.bill_street or ""
                new_customer.city = address.bill_city or ""
                new_customer.state = address.bill_state or ""
                new_customer.zip_code = address.bill_code or ""
                if not DRY_RUN:
                    new_customer.save()
                logging.info("created %s with id %s" % (new_customer, new_customer.pk))
        except Exception as e:
            logging.error("error creating customer %s: %s" % (account.accountname, e))


if __name__ == '__main__':
    migrate()
