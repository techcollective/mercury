# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProductOrServiceCategory'
        db.create_table('configuration_productorservicecategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('configuration', ['ProductOrServiceCategory'])

    def backwards(self, orm):
        # Deleting model 'ProductOrServiceCategory'
        db.delete_table('configuration_productorservicecategory')

    models = {
        'configuration.config': {
            'Meta': {'object_name': 'Config'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'configuration.image': {
            'Meta': {'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'path': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
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
        'configuration.productorservicecategory': {
            'Meta': {'object_name': 'ProductOrServiceCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'configuration.template': {
            'Meta': {'object_name': 'Template'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'template': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['configuration']