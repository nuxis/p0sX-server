# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-01 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]