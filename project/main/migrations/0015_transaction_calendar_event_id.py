# Generated by Django 2.0.5 on 2018-05-20 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20180520_0534'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='calendar_event_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]