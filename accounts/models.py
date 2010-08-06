import datetime
import decimal

from django.db import models
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from mercury.configuration.models import (PaymentType,
                                          InvoiceStatus,
                                          InvoiceTerm)
from mercury.accounts.fields import CurrencyField
from mercury.helpers import (TaxableDefault,
                             BooleanFetcher,
                             model_to_dict,
                             get_change_url,
                             get_currency_symbol,
                             get_or_create_default_invoice_status,
                             get_tax_percentage,
                             get_customer_term,
                             get_invoice_number_padding,
                             get_default_item_quantity,
                             get_or_create_default_invoice_term,
                             get_max_customer_invoices,
                             get_or_create_paid_invoice_status)


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True)
    email_address = models.EmailField(blank=True)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_taxable = models.BooleanField(
        default=TaxableDefault("customers").get_setting)
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
        display_paid = BooleanFetcher(
                                "display paid invoices on customer page")()
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

    # TODO: how can this work? custom admin template?
    #class Meta:
    #    verbose_name = get_customer_term()
    #    verbose_name_plural = get_customer_term(plural=True)


class ProductOrService(models.Model):
    name = models.CharField(max_length=50)
    price = CurrencyField()
    number_in_stock = models.PositiveIntegerField(default=0)
    manage_stock = models.BooleanField(default=BooleanFetcher("manage stock " +
                                       "of new products and services " +
                                       "by default"))
    is_taxable = models.BooleanField(
        default=TaxableDefault("products and services"))

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
        update = BooleanFetcher("automatically fill in " +
                                "blank invoice description")()
        if update and not self.description:
            entries = self.get_entries()
            entries = [(entry.description or str(entry.item))
                       for entry in entries]
            entries = ", ".join(entries)
            description = "%s - %s" % (str(self.customer), entries)
            if len(description) > 200: # field length limit
                description = description[:197] + "..."
            self.description = description

    def update(self):
        self.update_totals()
        self.update_tax()
        self.update_description()

    def get_number(self):
        num_zeros = get_invoice_number_padding()
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
        total_payments = self.payment_set.all().aggregate(models.Sum("amount"))
        if total_payments["amount__sum"] >= self.grand_total:
            self.status = get_or_create_paid_invoice_status()


class Entry(models.Model):
    item = models.ForeignKey(ProductOrService)
    cost = CurrencyField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2,
                                   default=get_default_item_quantity)
    description = models.CharField(max_length=400, blank=True)
    discount = CurrencyField(default=0)
    total = CurrencyField()

    class Meta:
        abstract = True
        verbose_name_plural = "Invoice entries"

    def save(self, *args, **kwargs):
        self.total = self.cost * self.quantity - self.discount
        if self.item.manage_stock:
            if self.item.number_in_stock > 0:
                self.item.number_in_stock -= self.quantity
                self.item.save()
        super(Entry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.item.manage_stock:
            self.item.number_in_stock += self.quantity
            self.item.save()
        super(Entry, self).delete(*args, **kwargs)


class InvoiceEntry(Entry):
    invoice = models.ForeignKey(Invoice)

    def __unicode__(self):
        return "Entry #%s on %s" % (self.id, str(self.invoice))


class QuoteEntry(Entry):
    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        return "Entry #%s on %s" % (self.id, str(self.quote))


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
