# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-15 09:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0014_auto_20200114_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='manager_email',
        ),
        migrations.AddField(
            model_name='account',
            name='manager',
            field=models.ForeignKey(blank=True, default='', help_text='Account Manager, financially responsible', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_manager', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='affiliation',
            field=models.ForeignKey(blank=True, default='', help_text='account (group/company) the user is affiliated to', null=True, on_delete=django.db.models.deletion.CASCADE, to='NEMO.Account'),
        ),
        migrations.AddField(
            model_name='user',
            name='fire_trained',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]