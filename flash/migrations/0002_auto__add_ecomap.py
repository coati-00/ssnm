# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ecomap'
        db.create_table('flash_ecomap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('flash', ['Ecomap'])


    def backwards(self, orm):
        # Deleting model 'Ecomap'
        db.delete_table('flash_ecomap')


    models = {
        'flash.ecomap': {
            'Meta': {'object_name': 'Ecomap'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['flash']