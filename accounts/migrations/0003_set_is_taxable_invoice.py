# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Set the is_taxable flag correctly. Note that no end users but
        TechCollective should ever have to run this migration, so its logic
        depends on tax rates used in TechCollective's database.
        """
        import decimal
        currency_field = orm.Invoice._meta.get_field_by_name("grand_total")[0]
        context = decimal.getcontext().copy()
        context.prec = currency_field.max_digits
        def round_decimal(number, places=None):
            if places is None:
                places = currency_field.decimal_places
            return number.quantize(
                decimal.Decimal(".1") ** places, context=context)
        for invoice in orm.Invoice.objects.all():
            items = invoice.invoiceentry_set.all()
            if invoice.total_tax:
                old_tax = invoice.total_tax
                old_grand_total = invoice.grand_total
                old_subtotal = invoice.subtotal
                taxable_subtotal = decimal.Decimal(0)
                subtotal = decimal.Decimal(0)
                for item in items:
                    subtotal += item.total
                    if item.item.is_taxable:
                        taxable_subtotal += item.total
                if taxable_subtotal == 0:
                    print ("invoice %s has tax but no taxable items" %
                           invoice.pk)
                    continue
                # calculate what the tax rate was when this invoice was created
                # assuming that the guessed is_taxable settings are correct
                old_tax_rate = round_decimal(old_tax * 100 / taxable_subtotal, 1)
                # if the calculated tax rate doesn't make sense, our is_taxable
                # assumptions were wrong
                if ((old_tax_rate != decimal.Decimal("8.5")) and
                    (old_tax_rate != decimal.Decimal("9.5"))):
                    print ("invoice %s needs checking, the tax came out as %s"
                           % (invoice.pk, old_tax_rate))
                    continue
                # re-total the invoice as a sanity check
                tax = round_decimal(taxable_subtotal * old_tax_rate / 100)
                grand_total = subtotal + tax
                if (tax != old_tax or grand_total != old_grand_total
                    or subtotal != old_subtotal):
                    print "check invoice %s, things didn't add up" % invoice.pk
                    print "calculated tax rate", old_tax_rate
                    print "tax", tax, old_tax
                    print "subtotal", subtotal, old_subtotal
                    print "grand total", grand_total, old_grand_total
                    continue
                # if we reached this point, our guesses for is_taxable were
                # correct
                for item in items:
                    item.is_taxable = item.item.is_taxable
                    item.save()
            else:
                # nothing on this invoice should be marked taxable
                for item in items:
                    item.is_taxable = False
                    item.save()


    def backwards(self, orm):
        "No need to undo anything here."


    models = {
        'accounts.customer': {
            'Meta': {'ordering': "['name']", 'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'default_payment_terms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['configuration.InvoiceTerm']"}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'accounts.deposit': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Deposit'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'total': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'})
        },
        'accounts.invoice': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Invoice'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Customer']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'date_due': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'grand_total': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['configuration.InvoiceStatus']"}),
            'subtotal': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'total_tax': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'})
        },
        'accounts.invoiceentry': {
            'Meta': {'ordering': "['invoice', 'pk']", 'object_name': 'InvoiceEntry'},
            'cost': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'discount': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Invoice']"}),
            'is_taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.ProductOrService']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '14', 'decimal_places': '2'}),
            'total': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'})
        },
        'accounts.payment': {
            'Meta': {'ordering': "['-date_received']", 'object_name': 'Payment'},
            'amount': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'date_received': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'deposit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Deposit']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Invoice']"}),
            'payment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['configuration.PaymentType']"}),
            'received_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'accounts.productorservice': {
            'Meta': {'object_name': 'ProductOrService'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'manage_stock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number_in_stock': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('accounts.fields.CurrencyField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'})
        },
        'accounts.quote': {
            'Meta': {'ordering': "['-date_created', '-id']", 'object_name': 'Quote'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Customer']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'grand_total': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'subtotal': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'total_tax': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'})
        },
        'accounts.quoteentry': {
            'Meta': {'object_name': 'QuoteEntry'},
            'cost': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'discount': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.ProductOrService']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '14', 'decimal_places': '2'}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Quote']"}),
            'total': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'configuration.invoicestatus': {
            'Meta': {'object_name': 'InvoiceStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'configuration.invoiceterm': {
            'Meta': {'object_name': 'InvoiceTerm'},
            'days_until_invoice_due': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'configuration.paymenttype': {
            'Meta': {'object_name': 'PaymentType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage_deposits': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']
    symmetrical = True
