# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (("accounts", "0008_add_m2m_customer_categories"),)

    def forwards(self, orm):
        db.rename_column("accounts_customer_categories", "customercategory_id", "customertag_id")
        db.rename_column("accounts_productorservice_categories", "productorservicecategory_id", "productorservicetag_id")

    def backwards(self, orm):
        db.rename_column("accounts_customer_categories","customertag_id", "customercategory_id")
        db.rename_column("accounts_productorservice_categories","productorservicetag_id", "productorservicecategory_id")

    models = {
        'configuration.config': {
            'Meta': {'object_name': 'Config'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'configuration.customertag': {
            'Meta': {'object_name': 'CustomerTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'configuration.productorservicetag': {
            'Meta': {'object_name': 'ProductOrServiceTag'},
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
