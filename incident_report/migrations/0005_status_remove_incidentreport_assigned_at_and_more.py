# Generated by Django 5.1.1 on 2024-11-23 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident_report', '0004_remove_statuschange_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='incidentreport',
            name='assigned_at',
        ),
        migrations.RemoveField(
            model_name='incidentreport',
            name='closed_at',
        ),
        migrations.RemoveField(
            model_name='incidentreport',
            name='resolved_at',
        ),
        migrations.AddField(
            model_name='incidentreport',
            name='status_timestamps',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='incidentreport',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.status'),
        ),
    ]
