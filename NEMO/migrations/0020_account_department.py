# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-17 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0019_auto_20200117_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='department',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
