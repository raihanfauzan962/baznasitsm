# Generated by Django 5.1.1 on 2024-12-04 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident_report', '0008_incidentreport_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentreport',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='open_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='pending_assignment_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='pending_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='pending_customer_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='pending_procurement_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='pending_third_party_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='rejected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='remark',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='waiting_approval_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incidentreport',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('pending', 'Pending'), ('pending_customer', 'Pending - Customer'), ('pending_assignment', 'Pending - Assignment'), ('pending_third_party', 'Pending - Third Party'), ('pending_procurement', 'Pending - Procurement'), ('assigned', 'Assigned'), ('resolved', 'Resolved'), ('cancelled', 'Cancelled'), ('waiting_approval', 'Waiting on Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('closed', 'Closed')], default='Open', max_length=20),
        ),
    ]