# Generated by Django 2.0.5 on 2018-05-21 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_transaction_calendar_event_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='official_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='token',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='family',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='categories',
            field=models.ManyToManyField(to='main.Category'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
