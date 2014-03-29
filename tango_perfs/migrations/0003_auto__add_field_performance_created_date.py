# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Performance.created_date'
        db.add_column(u'tango_perfs_performance', 'created_date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 3, 25, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Performance.created_date'
        db.delete_column(u'tango_perfs_performance', 'created_date')


    models = {
        u'tango_disco.genre': {
            'Meta': {'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'tango_disco.musician': {
            'Meta': {'object_name': 'Musician'},
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'tango_disco.orchestra': {
            'Meta': {'object_name': 'Orchestra'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Musician']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ocode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'tango_disco.recording': {
            'Meta': {'object_name': 'Recording'},
            'discNo': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Genre']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.RecordLabel']", 'null': 'True', 'blank': 'True'}),
            'matrixNo': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'orchestra': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Orchestra']"}),
            'recorded': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Song']"})
        },
        u'tango_disco.recordlabel': {
            'Meta': {'object_name': 'RecordLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'tango_disco.song': {
            'Meta': {'object_name': 'Song'},
            'composer': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tango_disco.Musician']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyricist': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'composer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['tango_disco.Musician']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'})
        },
        u'tango_perfs.couple': {
            'Meta': {'object_name': 'Couple'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tango_perfs.Performer']", 'symmetrical': 'False'})
        },
        u'tango_perfs.danceevent': {
            'Meta': {'object_name': 'DanceEvent'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'eventSeries': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_perfs.EventSeries']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'tango_perfs.eventseries': {
            'Meta': {'object_name': 'EventSeries'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'tango_perfs.performance': {
            'Meta': {'object_name': 'Performance'},
            'couples': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tango_perfs.Couple']", 'symmetrical': 'False'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_perfs.DanceEvent']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performance_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'recordings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tango_disco.Recording']", 'null': 'True', 'blank': 'True'}),
            'youtubeId': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'tango_perfs.performer': {
            'Meta': {'object_name': 'Performer'},
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['tango_perfs']