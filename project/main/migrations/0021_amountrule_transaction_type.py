# Generated by Django 2.0.5 on 2018-06-09 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20180604_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='amountrule',
            name='transaction_type',
            field=models.CharField(choices=[('LOAD', 'load'), ('DEBIT', 'debit')], default='DEBIT', max_length=20),
        ),
    ]
