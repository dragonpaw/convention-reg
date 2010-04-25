# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'MembershipType.numbered'
        db.add_column('reg_membershiptype', 'numbered', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True), keep_default=False)

        # Adding field 'MembershipType.approval_needed'
        db.add_column('reg_membershiptype', 'approval_needed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'MembershipType.in_quantity'
        db.add_column('reg_membershiptype', 'in_quantity', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding M2M table for field requires on 'MembershipType'
        db.create_table('reg_membershiptype_requires', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_membershiptype', models.ForeignKey(orm['reg.membershiptype'], null=False)),
            ('to_membershiptype', models.ForeignKey(orm['reg.membershiptype'], null=False))
        ))
        db.create_unique('reg_membershiptype_requires', ['from_membershiptype_id', 'to_membershiptype_id'])

        # Adding field 'MembershipSold.state'
        db.add_column('reg_membershipsold', 'state', self.gf('django.db.models.fields.CharField')(default='pending', max_length=20), keep_default=False)

        # Adding field 'MembershipSold.quantity'
        db.add_column('reg_membershipsold', 'quantity', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Changing field 'MembershipSold.payment_method'
        db.alter_column('reg_membershipsold', 'payment_method_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reg.PaymentMethod'], null=True, blank=True))

        # Removing unique constraint on 'MembershipSold', fields ['member', 'type']
        db.delete_unique('reg_membershipsold', ['member_id', 'type_id'])


    def backwards(self, orm):

        # Deleting field 'MembershipType.numbered'
        db.delete_column('reg_membershiptype', 'numbered')

        # Deleting field 'MembershipType.approval_needed'
        db.delete_column('reg_membershiptype', 'approval_needed')

        # Deleting field 'MembershipType.in_quantity'
        db.delete_column('reg_membershiptype', 'in_quantity')

        # Removing M2M table for field requires on 'MembershipType'
        db.delete_table('reg_membershiptype_requires')

        # Deleting field 'MembershipSold.state'
        db.delete_column('reg_membershipsold', 'state')

        # Deleting field 'MembershipSold.quantity'
        db.delete_column('reg_membershipsold', 'quantity')

        # Changing field 'MembershipSold.payment_method'
        db.alter_column('reg_membershipsold', 'payment_method_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reg.PaymentMethod']))

        # Adding unique constraint on 'MembershipSold', fields ['member', 'type']
        db.create_unique('reg_membershipsold', ['member_id', 'type_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'reg.affiliation': {
            'Meta': {'object_name': 'Affiliation'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'text_color': ('django.db.models.fields.CharField', [], {'default': "'black'", 'max_length': '40'})
        },
        'reg.event': {
            'Meta': {'object_name': 'Event'},
            'badge_number': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'to_print': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'reg.membershipsold': {
            'Meta': {'object_name': 'MembershipSold'},
            'badge_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': "orm['reg.Person']"}),
            'needs_printed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reg.PaymentMethod']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'print_timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sold_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['reg.MembershipType']"})
        },
        'reg.membershiptype': {
            'Meta': {'object_name': 'MembershipType'},
            'approval_needed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reg.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_quantity': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'numbered': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'requires': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'allows'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['reg.MembershipType']"}),
            'sale_end': ('django.db.models.fields.DateTimeField', [], {}),
            'sale_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'reg.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'reg.person': {
            'Meta': {'object_name': 'Person'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'affiliation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reg.Affiliation']", 'null': 'True', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'con_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'USA'", 'max_length': '20'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['reg']
