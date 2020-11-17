# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-11-16 16:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0037_auto_20201030_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='private',
            field=models.BooleanField(default=False, help_text='Marking the tool private will restrict visibility to qualified users.'),
        ),
    ]
