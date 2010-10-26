# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models


class VtigerCrmentity(models.Model):
    crmid = models.IntegerField(primary_key=True)
    smcreatorid = models.IntegerField()
    smownerid = models.IntegerField()
    modifiedby = models.IntegerField()
    setype = models.CharField(max_length=90)
    description = models.TextField(blank=True)
    createdtime = models.DateTimeField()
    modifiedtime = models.DateTimeField()
    viewedtime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=150, blank=True)
    version = models.IntegerField()
    presence = models.IntegerField(null=True, blank=True)
    deleted = models.IntegerField()

    class Meta:
        db_table = u'vtiger_crmentity'

    def __unicode__(self):
        return str(self.crmid)


class VtigerAccount(models.Model):
    accountid = models.ForeignKey(VtigerCrmentity, db_column='accountid', primary_key=True)
    account_no = models.CharField(max_length=300)
    accountname = models.CharField(max_length=300)
    parentid = models.IntegerField(null=True, blank=True)
    account_type = models.CharField(max_length=600, blank=True)
    industry = models.CharField(max_length=600, blank=True)
    annualrevenue = models.IntegerField(null=True, blank=True)
    rating = models.CharField(max_length=600, blank=True)
    ownership = models.CharField(max_length=150, blank=True)
    siccode = models.CharField(max_length=150, blank=True)
    tickersymbol = models.CharField(max_length=90, blank=True)
    phone = models.CharField(max_length=90, blank=True)
    otherphone = models.CharField(max_length=90, blank=True)
    email1 = models.CharField(max_length=300, blank=True)
    email2 = models.CharField(max_length=300, blank=True)
    website = models.CharField(max_length=300, blank=True)
    fax = models.CharField(max_length=90, blank=True)
    employees = models.IntegerField(null=True, blank=True)
    emailoptout = models.CharField(max_length=9, blank=True)
    notify_owner = models.CharField(max_length=9, blank=True)

    class Meta:
        db_table = u'vtiger_account'

    def __unicode__(self):
        return self.accountname


class VtigerAccountbillads(models.Model):
    accountaddressid = models.ForeignKey(VtigerAccount, db_column='accountaddressid', primary_key=True)
    bill_city = models.CharField(max_length=90, blank=True)
    bill_code = models.CharField(max_length=90, blank=True)
    bill_country = models.CharField(max_length=90, blank=True)
    bill_state = models.CharField(max_length=90, blank=True)
    bill_street = models.CharField(max_length=750, blank=True)
    bill_pobox = models.CharField(max_length=90, blank=True)

    class Meta:
        db_table = u'vtiger_accountbillads'


class VtigerInvoice(models.Model):
    invoiceid = models.ForeignKey(VtigerCrmentity, db_column="invoiceid", primary_key=True)
    subject = models.CharField(max_length=300, blank=True)
    customerno = models.CharField(max_length=300, blank=True)
    contactid = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    invoicedate = models.DateField(null=True, blank=True)
    duedate = models.DateField(null=True, blank=True)
    invoiceterms = models.CharField(max_length=300, blank=True)
    type = models.CharField(max_length=300, blank=True)
    adjustment = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    salescommission = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    exciseduty = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    subtotal = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    total = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    taxtype = models.CharField(max_length=75, blank=True)
    discount_percent = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    discount_amount = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    s_h_amount = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    shipping = models.CharField(max_length=300, blank=True)
    accountid = models.ForeignKey(VtigerAccount, null=True, blank=True, db_column="accountid")
    terms_conditions = models.TextField(blank=True)
    purchaseorder = models.CharField(max_length=600, blank=True)
    invoicestatus = models.CharField(max_length=600, blank=True)
    invoice_no = models.CharField(max_length=300, blank=True)
    currency_id = models.IntegerField()
    conversion_rate = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)

    class Meta:
        db_table = u'vtiger_invoice'

    def __unicode__(self):
        return self.subject


class VtigerInventoryproductrel(models.Model):
    id = models.ForeignKey(VtigerInvoice, null=True, blank=True, primary_key=True, db_column="id")
    productid = models.IntegerField(null=True, blank=True)
    sequence_no = models.IntegerField(null=True, blank=True)
    quantity = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    listprice = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    discount_percent = models.DecimalField(null=True, max_digits=9, decimal_places=3, blank=True)
    discount_amount = models.DecimalField(null=True, max_digits=9, decimal_places=3, blank=True)
    comment = models.CharField(max_length=750, blank=True)
    description = models.TextField(blank=True)
    incrementondel = models.IntegerField()
    lineitem_id = models.IntegerField(primary_key=True)
    tax1 = models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)
    tax2 = models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)
    tax3 = models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)

    class Meta:
        db_table = u'vtiger_inventoryproductrel'

    def __unicode__(self):
        return str(self.id)


class VtigerInvoicecf(models.Model):
    invoiceid = models.ForeignKey(VtigerInvoice, db_column='invoiceid', primary_key=True)
    cf_538 = models.TextField(blank=True)
    cf_541 = models.CharField(max_length=60, blank=True)
    cf_544 = models.DecimalField(null=True, max_digits=7, decimal_places=0, blank=True)
    cf_550 = models.CharField(max_length=9, blank=True)
    cf_557 = models.CharField(max_length=9, blank=True)
    cf_559 = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = u'vtiger_invoicecf'

class VtigerInvoicestatus(models.Model):
    inovicestatusid = models.IntegerField(primary_key=True)
    invoicestatus = models.CharField(unique=True, max_length=600)
    presence = models.IntegerField()
    picklist_valueid = models.IntegerField()

    class Meta:
        db_table = u'vtiger_invoicestatus'

    def __unicode__(self):
        return self.invoicestatus

class VtigerProducts(models.Model):
    productid = models.ForeignKey(VtigerCrmentity, db_column='productid', primary_key=True)
    product_no = models.CharField(max_length=300)
    productname = models.CharField(max_length=150)
    productcode = models.CharField(max_length=120, blank=True)
    productcategory = models.CharField(max_length=600, blank=True)
    manufacturer = models.CharField(max_length=600, blank=True)
    qty_per_unit = models.DecimalField(null=True, max_digits=13, decimal_places=2, blank=True)
    unit_price = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    weight = models.DecimalField(null=True, max_digits=13, decimal_places=3, blank=True)
    pack_size = models.IntegerField(null=True, blank=True)
    sales_start_date = models.DateField(null=True, blank=True)
    sales_end_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    cost_factor = models.IntegerField(null=True, blank=True)
    commissionrate = models.DecimalField(null=True, max_digits=9, decimal_places=3, blank=True)
    commissionmethod = models.CharField(max_length=150, blank=True)
    discontinued = models.IntegerField()
    usageunit = models.CharField(max_length=600, blank=True)
    handler = models.IntegerField(null=True, blank=True)
    reorderlevel = models.IntegerField(null=True, blank=True)
    website = models.CharField(max_length=300, blank=True)
    taxclass = models.CharField(max_length=600, blank=True)
    mfr_part_no = models.CharField(max_length=600, blank=True)
    vendor_part_no = models.CharField(max_length=600, blank=True)
    serialno = models.CharField(max_length=600, blank=True)
    qtyinstock = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    productsheet = models.CharField(max_length=600, blank=True)
    qtyindemand = models.IntegerField(null=True, blank=True)
    glacct = models.CharField(max_length=600, blank=True)
    vendor_id = models.IntegerField(null=True, blank=True)
    imagename = models.TextField(blank=True)
    currency_id = models.IntegerField()

    class Meta:
        db_table = u'vtiger_products'

    def __unicode__(self):
        return self.productname


class VtigerQuotes(models.Model):
    quoteid = models.ForeignKey(VtigerCrmentity, db_column="quoteid", primary_key=True)
    subject = models.CharField(max_length=300, blank=True)
    quotestage = models.CharField(max_length=600, blank=True)
    validtill = models.DateField(null=True, blank=True)
    contactid = models.IntegerField(null=True, blank=True)
    quote_no = models.CharField(max_length=300, blank=True)
    subtotal = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    carrier = models.CharField(max_length=600, blank=True)
    shipping = models.CharField(max_length=300, blank=True)
    inventorymanager = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=300, blank=True)
    adjustment = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    total = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    taxtype = models.CharField(max_length=75, blank=True)
    discount_percent = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    discount_amount = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    s_h_amount = models.DecimalField(null=True, max_digits=27, decimal_places=3, blank=True)
    accountid = models.IntegerField(null=True, blank=True)
    terms_conditions = models.TextField(blank=True)
    currency_id = models.IntegerField()
    conversion_rate = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = u'vtiger_quotes'

    def __unicode__(self):
        return str(self.quoteid)


class VtigerService(models.Model):
    serviceid = models.ForeignKey(VtigerCrmentity, db_column='serviceid', primary_key=True)
    service_no = models.CharField(max_length=300)
    servicename = models.CharField(max_length=150)
    servicecategory = models.CharField(max_length=600, blank=True)
    qty_per_unit = models.DecimalField(null=True, max_digits=13, decimal_places=2, blank=True)
    unit_price = models.DecimalField(null=True, max_digits=27, decimal_places=2, blank=True)
    sales_start_date = models.DateField(null=True, blank=True)
    sales_end_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    discontinued = models.IntegerField()
    service_usageunit = models.CharField(max_length=600, blank=True)
    handler = models.IntegerField(null=True, blank=True)
    website = models.CharField(max_length=300, blank=True)
    taxclass = models.CharField(max_length=600, blank=True)
    currency_id = models.IntegerField()
    commissionrate = models.DecimalField(null=True, max_digits=9, decimal_places=3, blank=True)

    class Meta:
        db_table = u'vtiger_service'

    def __unicode__(self):
        return self.servicename
