# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table('accounts_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('is_taxable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('default_payment_terms', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['configuration.InvoiceTerm'])),
        ))
        db.send_create_signal('accounts', ['Customer'])

        # Adding model 'ProductOrService'
        db.create_table('accounts_productorservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('accounts.fields.CurrencyField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('number_in_stock', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('manage_stock', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_taxable', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('accounts', ['ProductOrService'])

        # Adding model 'Quote'
        db.create_table('accounts_quote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Customer'])),
            ('date_created', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('subtotal', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('total_tax', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('grand_total', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['Quote'])

        # Adding model 'Invoice'
        db.create_table('accounts_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Customer'])),
            ('date_created', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('subtotal', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('total_tax', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('grand_total', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['configuration.InvoiceStatus'])),
            ('date_due', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal('accounts', ['Invoice'])

        # Adding model 'InvoiceEntry'
        db.create_table('accounts_invoiceentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.ProductOrService'])),
            ('cost', self.gf('accounts.fields.CurrencyField')(max_digits=15, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=14, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('discount', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('total', self.gf('accounts.fields.CurrencyField')(max_digits=15, decimal_places=2)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Invoice'])),
        ))
        db.send_create_signal('accounts', ['InvoiceEntry'])

        # Adding model 'QuoteEntry'
        db.create_table('accounts_quoteentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.ProductOrService'])),
            ('cost', self.gf('accounts.fields.CurrencyField')(max_digits=15, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=14, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('discount', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('total', self.gf('accounts.fields.CurrencyField')(max_digits=15, decimal_places=2)),
            ('quote', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Quote'])),
        ))
        db.send_create_signal('accounts', ['QuoteEntry'])

        # Adding model 'Deposit'
        db.create_table('accounts_deposit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('total', self.gf('accounts.fields.CurrencyField')(default=0, max_digits=15, decimal_places=2)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('made_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['Deposit'])

        # Adding model 'Payment'
        db.create_table('accounts_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Invoice'])),
            ('amount', self.gf('accounts.fields.CurrencyField')(max_digits=15, decimal_places=2)),
            ('payment_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['configuration.PaymentType'])),
            ('date_received', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('deposit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Deposit'], null=True, blank=True)),
            ('received_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['Payment'])

    def backwards(self, orm):
        # Deleting model 'Customer'
        db.delete_table('accounts_customer')

        # Deleting model 'ProductOrService'
        db.delete_table('accounts_productorservice')

        # Deleting model 'Quote'
        db.delete_table('accounts_quote')

        # Deleting model 'Invoice'
        db.delete_table('accounts_invoice')

        # Deleting model 'InvoiceEntry'
        db.delete_table('accounts_invoiceentry')

        # Deleting model 'QuoteEntry'
        db.delete_table('accounts_quoteentry')

        # Deleting model 'Deposit'
        db.delete_table('accounts_deposit')

        # Deleting model 'Payment'
        db.delete_table('accounts_payment')

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
            'Meta': {'ordering': "['invoice']", 'object_name': 'InvoiceEntry'},
            'cost': ('accounts.fields.CurrencyField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'discount': ('accounts.fields.CurrencyField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Invoice']"}),
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