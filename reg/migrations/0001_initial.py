
from south.db import db
from django.db import models
from reg.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'Member'
        db.create_table('reg_member', (
            ('id', orm['reg.Member:id']),
            ('name', orm['reg.Member:name']),
            ('con_name', orm['reg.Member:con_name']),
            ('address', orm['reg.Member:address']),
            ('city', orm['reg.Member:city']),
            ('state', orm['reg.Member:state']),
            ('zip', orm['reg.Member:zip']),
            ('country', orm['reg.Member:country']),
            ('phone', orm['reg.Member:phone']),
            ('birth_date', orm['reg.Member:birth_date']),
            ('affiliation', orm['reg.Member:affiliation']),
            ('email', orm['reg.Member:email']),
        ))
        db.send_create_signal('reg', ['Member'])

        # Adding model 'MembershipType'
        db.create_table('reg_membershiptype', (
            ('id', orm['reg.MembershipType:id']),
            ('event', orm['reg.MembershipType:event']),
            ('name', orm['reg.MembershipType:name']),
            ('code', orm['reg.MembershipType:code']),
            ('sale_start', orm['reg.MembershipType:sale_start']),
            ('sale_end', orm['reg.MembershipType:sale_end']),
            ('price', orm['reg.MembershipType:price']),
        ))
        db.send_create_signal('reg', ['MembershipType'])

        # Adding model 'Membership'
        db.create_table('reg_membership', (
            ('id', orm['reg.Membership:id']),
            ('member', orm['reg.Membership:member']),
            ('type', orm['reg.Membership:type']),
            ('needs_printed', orm['reg.Membership:needs_printed']),
            ('sold_by', orm['reg.Membership:sold_by']),
            ('badge_number', orm['reg.Membership:badge_number']),
            ('comment', orm['reg.Membership:comment']),
            ('price', orm['reg.Membership:price']),
            ('payment_method', orm['reg.Membership:payment_method']),
            ('print_timestamp', orm['reg.Membership:print_timestamp']),
        ))
        db.send_create_signal('reg', ['Membership'])

        # Adding model 'PaymentMethod'
        db.create_table('reg_paymentmethod', (
            ('id', orm['reg.PaymentMethod:id']),
            ('name', orm['reg.PaymentMethod:name']),
        ))
        db.send_create_signal('reg', ['PaymentMethod'])

        # Adding model 'Event'
        db.create_table('reg_event', (
            ('id', orm['reg.Event:id']),
            ('name', orm['reg.Event:name']),
            ('badge_number', orm['reg.Event:badge_number']),
            ('to_print', orm['reg.Event:to_print']),
        ))
        db.send_create_signal('reg', ['Event'])

        # Adding model 'Affiliation'
        db.create_table('reg_affiliation', (
            ('id', orm['reg.Affiliation:id']),
            ('name', orm['reg.Affiliation:name']),
            ('tag', orm['reg.Affiliation:tag']),
            ('color', orm['reg.Affiliation:color']),
            ('text_color', orm['reg.Affiliation:text_color']),
        ))
        db.send_create_signal('reg', ['Affiliation'])

        # Creating unique_together for [member, type] on Membership.
        db.create_unique('reg_membership', ['member_id', 'type_id'])



    def backwards(self, orm):

        # Deleting unique_together for [member, type] on Membership.
        db.delete_unique('reg_membership', ['member_id', 'type_id'])

        # Deleting model 'Member'
        db.delete_table('reg_member')

        # Deleting model 'MembershipType'
        db.delete_table('reg_membershiptype')

        # Deleting model 'Membership'
        db.delete_table('reg_membership')

        # Deleting model 'PaymentMethod'
        db.delete_table('reg_paymentmethod')

        # Deleting model 'Event'
        db.delete_table('reg_event')

        # Deleting model 'Affiliation'
        db.delete_table('reg_affiliation')



    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
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
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'reg.affiliation': {
            'color': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'text_color': ('django.db.models.fields.CharField', [], {'default': "'black'", 'max_length': '40'})
        },
        'reg.event': {
            'badge_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_print': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'reg.member': {
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
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'reg.membership': {
            'Meta': {'unique_together': "(('member', 'type'),)"},
            'badge_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': "orm['reg.Member']"}),
            'needs_printed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reg.PaymentMethod']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'print_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sold_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['reg.MembershipType']"})
        },
        'reg.membershiptype': {
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reg.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'sale_end': ('django.db.models.fields.DateTimeField', [], {}),
            'sale_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'reg.paymentmethod': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['reg']
