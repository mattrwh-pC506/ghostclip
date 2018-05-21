# Generated by Django 2.0.5 on 2018-05-20 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_account_track'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendar',
            name='user',
        ),
        migrations.AlterField(
            model_name='account',
            name='limit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='official_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Calendar',
        ),
    ]