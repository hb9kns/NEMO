# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-04 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0023_user_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='position',
            field=models.CharField(blank=True, default='', help_text='semester/master/postdoc/..', max_length=100, null=True),
        ),
    ]