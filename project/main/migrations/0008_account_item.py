# Generated by Django 2.0.5 on 2018-05-15 03:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20180514_0006'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='item',
            field=models.ForeignKey(default='D7kp0A9EBntMzEvVbLq1TZvNyNRE75tZKJXwd', on_delete=django.db.models.deletion.CASCADE, to='main.Item'),
            preserve_default=False,
        ),
    ]
