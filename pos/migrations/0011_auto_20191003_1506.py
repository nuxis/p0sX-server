# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-10-03 13:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0010_creditupdate_geekevents_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('update_credit', 'Can update the credit limit on a user'), ('import_credit', 'Can import credit from GeekEvents'))},
        ),
    ]