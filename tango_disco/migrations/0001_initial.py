# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Musician'
        db.create_table(u'tango_disco_musician', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstName', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lastName', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'tango_disco', ['Musician'])

        # Adding model 'MusicianRole'
        db.create_table(u'tango_disco_musicianrole', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'tango_disco', ['MusicianRole'])

        # Adding model 'RecordLabel'
        db.create_table(u'tango_disco_recordlabel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'tango_disco', ['RecordLabel'])

        # Adding model 'Genre'
        db.create_table(u'tango_disco_genre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'tango_disco', ['Genre'])

        # Adding model 'Song'
        db.create_table(u'tango_disco_song', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
        ))
        db.send_create_signal(u'tango_disco', ['Song'])

        # Adding M2M table for field composer on 'Song'
        m2m_table_name = db.shorten_name(u'tango_disco_song_composer')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm[u'tango_disco.song'], null=False)),
            ('musician', models.ForeignKey(orm[u'tango_disco.musician'], null=False))
        ))
        db.create_unique(m2m_table_name, ['song_id', 'musician_id'])

        # Adding M2M table for field lyricist on 'Song'
        m2m_table_name = db.shorten_name(u'tango_disco_song_lyricist')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm[u'tango_disco.song'], null=False)),
            ('musician', models.ForeignKey(orm[u'tango_disco.musician'], null=False))
        ))
        db.create_unique(m2m_table_name, ['song_id', 'musician_id'])

        # Adding model 'Orchestra'
        db.create_table(u'tango_disco_orchestra', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('leader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Musician'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ocode', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
        ))
        db.send_create_signal(u'tango_disco', ['Orchestra'])

        # Adding model 'Recording'
        db.create_table(u'tango_disco_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Song'])),
            ('orchestra', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Orchestra'])),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.RecordLabel'], null=True, blank=True)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Genre'])),
            ('recorded', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('discNo', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('matrixNo', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal(u'tango_disco', ['Recording'])

        # Adding model 'PlayedOn'
        db.create_table(u'tango_disco_playedon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('musician', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Musician'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.Recording'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tango_disco.MusicianRole'])),
        ))
        db.send_create_signal(u'tango_disco', ['PlayedOn'])


    def backwards(self, orm):
        # Deleting model 'Musician'
        db.delete_table(u'tango_disco_musician')

        # Deleting model 'MusicianRole'
        db.delete_table(u'tango_disco_musicianrole')

        # Deleting model 'RecordLabel'
        db.delete_table(u'tango_disco_recordlabel')

        # Deleting model 'Genre'
        db.delete_table(u'tango_disco_genre')

        # Deleting model 'Song'
        db.delete_table(u'tango_disco_song')

        # Removing M2M table for field composer on 'Song'
        db.delete_table(db.shorten_name(u'tango_disco_song_composer'))

        # Removing M2M table for field lyricist on 'Song'
        db.delete_table(db.shorten_name(u'tango_disco_song_lyricist'))

        # Deleting model 'Orchestra'
        db.delete_table(u'tango_disco_orchestra')

        # Deleting model 'Recording'
        db.delete_table(u'tango_disco_recording')

        # Deleting model 'PlayedOn'
        db.delete_table(u'tango_disco_playedon')


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
        u'tango_disco.musicianrole': {
            'Meta': {'object_name': 'MusicianRole'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'tango_disco.orchestra': {
            'Meta': {'object_name': 'Orchestra'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Musician']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ocode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'tango_disco.playedon': {
            'Meta': {'object_name': 'PlayedOn'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'musician': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Musician']"}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.Recording']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tango_disco.MusicianRole']"})
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
        }
    }

    complete_apps = ['tango_disco']