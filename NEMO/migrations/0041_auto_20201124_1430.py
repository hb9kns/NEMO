# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-11-24 13:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0040_tool_usage_warning'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='allow_pending_usage',
            field=models.BooleanField(default=False, help_text='Allow registering of automatic start of usage event as soon as tool becomes free.'),
        ),
        migrations.AddField(
            model_name='tool',
            name='pending_operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_tool_operator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tool',
            name='pending_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_tool_project', to='NEMO.Project'),
        ),
        migrations.AddField(
            model_name='tool',
            name='pending_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pending_tool_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
