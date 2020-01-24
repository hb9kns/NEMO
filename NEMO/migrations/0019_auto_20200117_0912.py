# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-17 08:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0018_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_contact',
            field=models.ForeignKey(blank=True, default='', help_text='for technical and budgetary discussions', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='project_description',
            field=models.TextField(blank=True, help_text='project description, remarks'),
        ),
    ]