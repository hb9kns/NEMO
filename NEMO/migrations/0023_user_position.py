# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-04 14:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0022_auto_20200124_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='position',
            field=models.CharField(blank=True, default='', help_text='master/bachelor student, postdoc, ...', max_length=100, null=True),
        ),
    ]