# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-18 22:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0011_userchemical_sds_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.PositiveIntegerField(blank=True, help_text='Channel on Interlock Card connecting to sensor (starting with 0)', null=True)),
                ('name', models.CharField(help_text='Name of Sensor', max_length=100)),
                ('sensor_type', models.IntegerField(choices=[(1, 'Digital'), (2, 'Analog')], default=1)),
                ('conversion_factor', models.FloatField(default=1.0, help_text='Conversion factor to output response in desired units. Default is 1')),
                ('email', models.EmailField(blank=True, help_text='Email address to alert when sensor has a certain reading', max_length=254, null=True, verbose_name='email address')),
                ('high_alert_value', models.FloatField(blank=True, help_text='Threshold value for sending alert (for analog sensors)', null=True)),
                ('low_alert_value', models.FloatField(blank=True, help_text='Threshold value for sending alert (for analog sensors)', null=True)),
                ('digital_sensor_alert', models.BooleanField(default=False, help_text='Turn alerts on or off for digital sensor')),
                ('digital_alert_value', models.BooleanField(default=True, help_text='Choose to alert when the sensor reads true or false')),
                ('last_value', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.ForeignKey(blank=True, help_text='Interlock Card (IP Address) associated with this sensor', null=True, on_delete=django.db.models.deletion.SET_NULL, to='NEMO.InterlockCard')),
            ],
            options={
                'ordering': ['address', 'name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='sensor',
            unique_together=set([('address', 'channel', 'sensor_type')]),
        ),
    ]
