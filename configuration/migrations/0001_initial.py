# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PaymentType'
        db.create_table('configuration_paymenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('manage_deposits', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('configuration', ['PaymentType'])

        # Adding model 'InvoiceStatus'
        db.create_table('configuration_invoicestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('configuration', ['InvoiceStatus'])

        # Adding model 'InvoiceTerm'
        db.create_table('configuration_invoiceterm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('days_until_invoice_due', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, unique=True)),
        ))
        db.send_create_signal('configuration', ['InvoiceTerm'])

        # Adding model 'Image'
        db.create_table('configuration_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('path', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('configuration', ['Image'])

        # Adding model 'Template'
        db.create_table('configuration_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('template', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('configuration', ['Template'])

        # Adding model 'Config'
        db.create_table('configuration_config', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('configuration', ['Config'])

    def backwards(self, orm):
        # Deleting model 'PaymentType'
        db.delete_table('configuration_paymenttype')

        # Deleting model 'InvoiceStatus'
        db.delete_table('configuration_invoicestatus')

        # Deleting model 'InvoiceTerm'
        db.delete_table('configuration_invoiceterm')

        # Deleting model 'Image'
        db.delete_table('configuration_image')

        # Deleting model 'Template'
        db.delete_table('configuration_template')

        # Deleting model 'Config'
        db.delete_table('configuration_config')

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
        'configuration.template': {
            'Meta': {'object_name': 'Template'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'template': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['configuration']