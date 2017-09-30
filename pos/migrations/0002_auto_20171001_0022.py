# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-09-30 22:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crew',
            name='is_cashier',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='itemingredient',
            name='exclusive',
            field=models.BooleanField(default=False),
        ),
    ]