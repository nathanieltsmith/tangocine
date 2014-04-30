# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Performer'
        db.create_table(u'tango_perfs_performer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstName', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lastName', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('fullName', self.gf('django.db.models.fields.CharField')(default='x', max_length=100)),
            ('simplifiedName', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, unique=True, null=True, blank=True)),
            ('totalFollowers', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'tango_perfs', ['Performer'])

        # Adding model 'Couple'
        db.create_table(u'tango_perfs_couple', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tango_perfs', ['Couple'])

        # Adding M2M table for field performers on 'Couple'
        m2m_table_name = db.shorten_name(u'tango_perfs_couple_performers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('couple', models.ForeignKey(orm[u'tango_perfs.couple'], null=False)),
            ('performer', models.ForeignKey(orm[u'tango_perfs.performer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['couple_id', 'performer_id'])

        # Adding model 'EventSeries'
        db.create_table(u'tango_perfs_eventseries', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'tango_perfs', ['EventSeries'])

        # Adding model 'DanceEvent'
        db.create_table(u'tango_perfs_danceevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('eventSeries', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_perfs.EventSeries'])),
        ))
        db.send_create_signal(u'tango_perfs', ['DanceEvent'])

        # Adding model 'Performance'
        db.create_table(u'tango_perfs_performance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('youtubeId', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('thumbnailUrl', self.gf('django.db.models.fields.CharField')(default='http://terryshoemaker.files.wordpress.com/2013/03/placeholder1.jpg', max_length=100)),
            ('totalViews', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('previousTotalViews', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('hotness', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_perfs.DanceEvent'], null=True, blank=True)),
            ('performance_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('performance_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('youtubeUploadDate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'tango_perfs', ['Performance'])

        # Adding M2M table for field couples on 'Performance'
        m2m_table_name = db.shorten_name(u'tango_perfs_performance_couples')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('performance', models.ForeignKey(orm[u'tango_perfs.performance'], null=False)),
            ('couple', models.ForeignKey(orm[u'tango_perfs.couple'], null=False))
        ))
        db.create_unique(m2m_table_name, ['performance_id', 'couple_id'])

        # Adding M2M table for field recordings on 'Performance'
        m2m_table_name = db.shorten_name(u'tango_perfs_performance_recordings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('performance', models.ForeignKey(orm[u'tango_perfs.performance'], null=False)),
            ('recording', models.ForeignKey(orm[u'tango_disco.recording'], null=False))
        ))
        db.create_unique(m2m_table_name, ['performance_id', 'recording_id'])


    def backwards(self, orm):
        # Deleting model 'Performer'
        db.delete_table(u'tango_perfs_performer')

        # Deleting model 'Couple'
        db.delete_table(u'tango_perfs_couple')

        # Removing M2M table for field performers on 'Couple'
        db.delete_table(db.shorten_name(u'tango_perfs_couple_performers'))

        # Deleting model 'EventSeries'
        db.delete_table(u'tango_perfs_eventseries')

        # Deleting model 'DanceEvent'
        db.delete_table(u'tango_perfs_danceevent')

        # Deleting model 'Performance'
        db.delete_table(u'tango_perfs_performance')

        # Removing M2M table for field couples on 'Performance'
        db.delete_table(db.shorten_name(u'tango_perfs_performance_couples'))

        # Removing M2M table for field recordings on 'Performance'
        db.delete_table(db.shorten_name(u'tango_perfs_performance_recordings'))


    models = {
        u'tango_disco.genre': {
            'Meta': {'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'tango_disco.musician': {
            'Meta': {'object_name': 'Musician'},
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'simplifiedName': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'})
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
            'itunesId': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.RecordLabel']", 'null': 'True', 'blank': 'True'}),
            'matrixNo': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'orchestra': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Orchestra']"}),
            'recorded': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Song']"})
        },
        u'tango_disco.recordlabel': {
            'Meta': {'object_name': 'RecordLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tango_disco.song': {
            'Meta': {'object_name': 'Song'},
            'composer': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tango_disco.Musician']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyricist': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'composer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['tango_disco.Musician']"}),
            'simplifiedTitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'couples': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tango_perfs.Couple']", 'symmetrical': 'False'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_perfs.DanceEvent']", 'null': 'True', 'blank': 'True'}),
            'hotness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performance_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'performance_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'previousTotalViews': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recordings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tango_disco.Recording']", 'null': 'True', 'blank': 'True'}),
            'thumbnailUrl': ('django.db.models.fields.CharField', [], {'default': "'http://terryshoemaker.files.wordpress.com/2013/03/placeholder1.jpg'", 'max_length': '100'}),
            'totalViews': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'youtubeId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'youtubeUploadDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'tango_perfs.performer': {
            'Meta': {'object_name': 'Performer'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'fullName': ('django.db.models.fields.CharField', [], {'default': "'x'", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'simplifiedName': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'totalFollowers': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['tango_perfs']