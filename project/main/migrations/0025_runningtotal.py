# Generated by Django 2.0.5 on 2018-08-19 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20180819_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunningTotal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar_event_id', models.CharField(blank=True, max_length=255, null=True)),
                ('target', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Account')),
            ],
        ),
    ]
