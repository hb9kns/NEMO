# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-18 18:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0003_auto_20180816_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockroomCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Stockroom categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StockroomItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(help_text='The number of items currently in stock.')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, help_text='The cost of this item', max_digits=6)),
                ('visible', models.BooleanField(default=True)),
                ('reminder_threshold', models.IntegerField(help_text='More of this item should be ordered when the quantity falls below this threshold.')),
                ('reminder_email', models.EmailField(help_text='An email will be sent to this address when the quantity of this item falls below the reminder threshold.', max_length=254)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NEMO.StockroomCategory')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StockroomWithdraw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time when the user withdrew the consumable.')),
                ('customer', models.ForeignKey(help_text='The user who will use the stockroom item.', on_delete=django.db.models.deletion.CASCADE, related_name='stockroom_user', to=settings.AUTH_USER_MODEL)),
                ('merchant', models.ForeignKey(help_text='The staff member that performed the withdraw.', on_delete=django.db.models.deletion.CASCADE, related_name='stockroom_merchant', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(help_text='The withdraw will be billed to this project.', on_delete=django.db.models.deletion.CASCADE, to='NEMO.Project')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NEMO.StockroomItem')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),

    ]
