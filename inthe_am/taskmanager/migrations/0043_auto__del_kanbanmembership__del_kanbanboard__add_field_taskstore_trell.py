# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'KanbanMembership'
        db.delete_table(u'taskmanager_kanbanmembership')

        # Deleting model 'KanbanBoard'
        db.delete_table(u'taskmanager_kanbanboard')

        # Adding field 'TaskStore.trello_auth_token'
        db.add_column(u'taskmanager_taskstore', 'trello_auth_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'TaskStore.trello_board_id'
        db.add_column(u'taskmanager_taskstore', 'trello_board_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'KanbanMembership'
        db.create_table(u'taskmanager_kanbanmembership', (
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('kanban_board', self.gf('django.db.models.fields.related.ForeignKey')(related_name='memberships', to=orm['taskmanager.KanbanBoard'])),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invitee_email', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=254, db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(blank=True, max_length=36, db_index=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_memberships', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='kanban_memberships', null=True, to=orm['auth.User'], blank=True)),
            ('role', self.gf('django.db.models.fields.CharField')(default='member', max_length=255)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('taskmanager', ['KanbanMembership'])

        # Adding model 'KanbanBoard'
        db.create_table(u'taskmanager_kanbanboard', (
            (u'taskstore_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['taskmanager.TaskStore'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('columns', self.gf('django.db.models.fields.TextField')(default='[{"name": "Ready"}, {"name": "Doing"}, {"name": "Done"}]')),
            ('uuid', self.gf('django.db.models.fields.CharField')(blank=True, max_length=36, db_index=True)),
        ))
        db.send_create_signal('taskmanager', ['KanbanBoard'])

        # Deleting field 'TaskStore.trello_auth_token'
        db.delete_column(u'taskmanager_taskstore', 'trello_auth_token')

        # Deleting field 'TaskStore.trello_board_id'
        db.delete_column(u'taskmanager_taskstore', 'trello_board_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taskmanager.announcement': {
            'Meta': {'object_name': 'Announcement'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '300'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'starts': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'taskmanager.taskattachment': {
            'Meta': {'object_name': 'TaskAttachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['taskmanager.TaskStore']"}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        'taskmanager.taskstore': {
            'Meta': {'object_name': 'TaskStore'},
            'configured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_whitelist': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'feed_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'local_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'pebble_cards_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'sms_arguments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sms_replies': ('django.db.models.fields.PositiveIntegerField', [], {'default': '9'}),
            'sms_whitelist': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sync_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sync_permitted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'taskrc_extras': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'trello_auth_token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'trello_board_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'twilio_auth_token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'task_stores'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'taskmanager.taskstoreactivitylog': {
            'Meta': {'unique_together': "(('store', 'md5hash'),)", 'object_name': 'TaskStoreActivityLog'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'md5hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'silent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'to': "orm['taskmanager.TaskStore']"})
        },
        'taskmanager.usermetadata': {
            'Meta': {'object_name': 'UserMetadata'},
            'colorscheme': ('django.db.models.fields.CharField', [], {'default': "'dark-yellow-green.theme'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tos_accepted': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'tos_version': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metadata'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['taskmanager']