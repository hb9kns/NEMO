# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-04-26 21:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0026_tool_usage_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='remarks',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='account',
            name='techcontact',
            field=models.ForeignKey(blank=True, default='', help_text='Contact person for planning', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='technical_contact', to=settings.AUTH_USER_MODEL),
        ),
    ]