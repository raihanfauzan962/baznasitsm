# Generated by Django 5.1.1 on 2024-11-20 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_request', '0003_asset_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'verbose_name': 'Service Item', 'verbose_name_plural': 'Service Items'},
        ),
        migrations.AlterModelOptions(
            name='assetform',
            options={'verbose_name': 'Service Item Form', 'verbose_name_plural': 'Service Item Forms'},
        ),
    ]