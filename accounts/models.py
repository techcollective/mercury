import datetime
import decimal

from django.db import models
from django.utils.text import capfirst
from django.core.exceptions import ValidationError

from mercury.configuration.models import (PaymentType,
                                          InvoiceStatus,
                                          InvoiceTerm)
from mercury.accounts.fields import CurrencyField
from mercury.helpers import (model_to_dict,
                             refresh,
                             get_change_url,
                             get_currency_symbol,
                             get_or_create_default_invoice_status,
                             get_tax_percentage,
                             get_or_create_default_invoice_term,
                             get_max_customer_invoices,
                             get_or_create_paid_invoice_status,
                             get_customer_taxable,
                             get_product_taxable,
                             get_manage_stock,
                             get_default_quantity,
                             get_invoice_padding,
                             get_display_paid,
                             get_fill_description,
                             get_negative_stock,
                             get_auto_invoice_status)


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_taxable = models.BooleanField(default=get_customer_taxable)
    default_payment_terms = models.ForeignKey(InvoiceTerm,
                                    default=get_or_create_default_invoice_term)

    def __unicode__(self):
        return self.name

    def get_invoice_list(self):
        """
        This is used by the custom customer change template to show a
        customer's invoice list. It should belong in a view, but it's
        easier to do it here than create a custom admin view that would first
        have to duplicate the current render_change_form functionality.
        """
        max_invoices = get_max_customer_invoices()
        display_paid = get_display_paid()
        paid_status = get_or_create_paid_invoice_status()

        qs = self.invoice_set.all()
        if not display_paid:
            qs = qs.exclude(status__status__iexact=paid_status)
        # the code below was written with the following in mind:
        # 1) the most common scenario of len(invoices) < max_invoices is the
        #    shortest fastest code path
        # 2) there's no need to call .count() when we're retrieving the
        #    objects anyway. i retrieve max_count+1 to avoid treating the
        #    case of qs.count() == max_invoices the same way as when the
        #    count has actually been exceeded.
        invoices = qs[:max_invoices + 1]
        if len(invoices) > max_invoices:
            title = "%s most recent " % max_invoices
            invoices = invoices[:max_invoices]
        else:
            title = ""
        if not display_paid:
            title += "unpaid "
        title += "invoices"
        if max_invoices == 1:
            title = "most recent invoice"
        title = capfirst(title)
        invoice_list = []
        for invoice in invoices:
            data = model_to_dict(invoice)
            data["number"] = invoice.get_number()
            data["url"] = get_change_url(invoice)
            invoice_list.append(data)
        return {"title": title, "invoices": invoice_list}


class ProductOrService(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()
    number_in_stock = models.IntegerField(default=0)
    manage_stock = models.BooleanField(default=get_manage_stock)
    is_taxable = models.BooleanField(default=get_product_taxable)

    def save(self, *args, **kwargs):
        allow_negative = get_negative_stock()
        if not allow_negative and self.number_in_stock < 0:
            self.number_in_stock = 0
        super(ProductOrService, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products and services"


class QuoteInvoiceBase(models.Model):
    customer = models.ForeignKey(Customer)
    date_created = models.DateField(default=datetime.date.today)
    description = models.CharField(max_length=200, blank=True)
    subtotal = CurrencyField(default=0, read_only=True)
    total_tax = CurrencyField(default=0, read_only=True)
    grand_total = CurrencyField(default=0, read_only=True)

    def update_tax(self):
        tax = 0
        tax_percentage = get_tax_percentage()
        if self.customer.is_taxable:
            for entry in self.get_entries():
                if entry.item.is_taxable:
                    tax += entry.total * tax_percentage / 100
        self.total_tax = tax

    def update_totals(self):
        self.update_tax()
        subtotal = 0
        grand_total = 0
        for entry in self.get_entries():
            subtotal += entry.total
        self.subtotal = subtotal
        self.grand_total = subtotal + self.total_tax

    def update_description(self):
        update = get_fill_description()
        if update and not self.description:
            entries = self.get_entries()
            entries = [(entry.description or str(entry.item))
                       for entry in entries]
            entries = ", ".join(entries)
            description = "%s - %s" % (str(self.customer), entries)
            if len(description) > 200:  # field length limit
                description = description[:197] + "..."
            self.description = description

    def update(self):
        self.update_totals()
        self.update_tax()
        self.update_description()

    def get_number(self):
        num_zeros = get_invoice_padding()
        return str(self.id).zfill(num_zeros)
    get_number.short_description = "Number"
    get_number.admin_order_field = "id"

    def get_formatted_total(self):
        # i'm hoping there's a nicer way to get the formatted
        # currencyfield that i haven't thought of
        grand_total = self._meta.get_field_by_name("grand_total")[0]
        return grand_total.value_to_string(self)

    def __unicode__(self):
        return self.description + " - " + self.get_formatted_total()

    class Meta:
        abstract = True
        ordering = ["-date_created", "-id"]


class Quote(QuoteInvoiceBase):
    def get_entries(self):
        return self.quoteentry_set.all()

    def create_invoice(self):
        new_invoice = Invoice()
        fields = [f.name for f in self._meta.fields if f.name !="id"]
        for field in fields:
            setattr(new_invoice, field, getattr(self, field))
        # todo: date_due can be set based on customer terms
        new_invoice.save()
        entries = self.get_entries()
        for entry in entries:
            entry.copy_to_invoice(new_invoice)
        return new_invoice


class Invoice(QuoteInvoiceBase):
    status = models.ForeignKey(InvoiceStatus,
                               default=get_or_create_default_invoice_status)
    date_due = models.DateField(default=datetime.date.today)

    def get_entries(self):
        return self.invoiceentry_set.all()

    def update(self):
        super(Invoice, self).update()
        self.update_status()

    def update_status(self):
        if get_auto_invoice_status():
            total_payments = self.payment_set.all().aggregate(
                                                        models.Sum("amount"))
            if total_payments["amount__sum"] >= self.grand_total:
                self.status = get_or_create_paid_invoice_status()

    def delete(self, *args, **kwargs):
        for entry in self.get_entries():
            # this is done so that stock is updated
            entry.delete()
        super(Invoice, self).delete(*args, **kwargs)


class Entry(models.Model):
    item = models.ForeignKey(ProductOrService)
    cost = CurrencyField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2,
                                   default=get_default_quantity)
    description = models.CharField(max_length=400, blank=True)
    discount = CurrencyField(default=0)
    total = CurrencyField()

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"

    def save(self, *args, **kwargs):
        self.total = self.cost * self.quantity - self.discount
        super(Entry, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.quantity > 1:
            add = " (%s)" % self.quantity
        else:
            add = ""
        return "%s%s" % (str(self.item), add)


class InvoiceEntry(Entry):
    invoice = models.ForeignKey(Invoice)

    def delete(self, *args, **kwargs):
        if self.item.manage_stock:
            # refresh is called because if multiple items are deleted, they
            # contain stale versions of item.number_in_stock
            item = refresh(self.item)
            item.number_in_stock += self.quantity
            item.save()
        super(InvoiceEntry, self).delete(*args, **kwargs)


def stock_callback(sender, **kwargs):
    new_instance = kwargs["instance"]
    if new_instance.item.manage_stock:
        try:
            old_instance = sender.objects.get(pk=new_instance.pk)
        except sender.DoesNotExist:
            # a new entry is being added
            stock_change = new_instance.quantity
        else:
            # an existing entry is being edited
            stock_change = new_instance.quantity - old_instance.quantity
        # refresh is called because if multiple items are modified, they
        # contain stale versions of item.number_in_stock
        item = refresh(new_instance.item)
        item.number_in_stock -= stock_change
        item.save()

# this is to manage stock when invoice items are added or edited
models.signals.pre_save.connect(stock_callback, sender=InvoiceEntry)


class QuoteEntry(Entry):
    quote = models.ForeignKey(Quote)

    def copy_to_invoice(self, invoice):
        new_invoice_entry = InvoiceEntry()
        skip = ["id", "quote"]
        fields = [f.name for f in self._meta.fields if f.name not in skip]
        for field in fields:
            setattr(new_invoice_entry, field, getattr(self, field))
        new_invoice_entry.invoice = invoice
        new_invoice_entry.save()



class Deposit(models.Model):
    date = models.DateField(default=datetime.date.today)
    total = CurrencyField(default=0, read_only=True)
    comment = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        total = self.payment_set.all().aggregate(models.Sum("amount"))
        self.total = total["amount__sum"]
        super(Deposit, self).save(*args, **kwargs)

    def __unicode__(self):
        prefix, suffix = get_currency_symbol()
        return "Deposit of %s%s%s on %s" % (prefix, self.total, suffix,
                                            self.date)

    class Meta:
        ordering = ["-date"]


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice)
    amount = CurrencyField()
    payment_type = models.ForeignKey(PaymentType)
    date_received = models.DateField(default=datetime.date.today)
    comment = models.CharField(max_length=200, blank=True)
    deposit = models.ForeignKey(Deposit, blank=True, null=True)
    depositable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.payment_type.manage_deposits:
            self.depositable = True
        super(Payment, self).save(*args, **kwargs)
        if self.deposit:
            # call save() on deposit to update total
            self.deposit.save()
        self.invoice.update_status()
        self.invoice.save()

    def clean(self):
        if not self.depositable and self.deposit:
            message = "The payment type '%s' isn't " % str(self.payment_type)
            message += "depositable, so this payment can't belong to a deposit"
            raise ValidationError(message)

    def __unicode__(self):
        prefix, suffix = get_currency_symbol()
        return "%s%s%s %s payment for %s" % (prefix,
                                             self.amount,
                                             suffix,
                                             self.payment_type,
                                             str(self.invoice))

    class Meta:
        ordering = ["payment_type", "-date_received"]
