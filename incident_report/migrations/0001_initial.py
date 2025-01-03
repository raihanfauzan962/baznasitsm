# Generated by Django 5.1.1 on 2024-10-10 10:23

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='incident_report.building')),
            ],
        ),
        migrations.CreateModel(
            name='AffectedDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to='incident_report.issue')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='incident_report.category')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='incident_report.subcategory'),
        ),
        migrations.CreateModel(
            name='IncidentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_for', models.EmailField(blank=True, max_length=254, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=20, null=True)),
                ('subject', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='attachments/')),
                ('ticket_code', models.CharField(max_length=20, unique=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Pending', 'Pending'), ('Resolved', 'Resolved'), ('Closed', 'Closed')], default='Open', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('assigned_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('affected_device', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.affecteddevice')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.building')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.category')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.floor')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.issue')),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='incident_report.subcategory')),
            ],
        ),
    ]
