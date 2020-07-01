# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-07-01 08:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0031_user_equiresp_trained'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='reservation_physical_access_level',
            field=models.ForeignKey(blank=True, help_text='If set, only users with this physical access level may reserve the tool.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='physical_access_for_reservation', to='NEMO.PhysicalAccessLevel'),
        ),
    ]
