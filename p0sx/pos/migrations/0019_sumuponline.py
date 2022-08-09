# Generated by Django 3.2.6 on 2022-08-08 01:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0018_auto_20211011_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='SumUpOnline',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('status', models.SmallIntegerField(choices=[(0, 'CREATED'), (1, 'PROCESSING'), (2, 'SUCCESS'), (3, 'FAILED'), (4, 'COMPLETE')], default=0)),
                ('transaction_id', models.CharField(blank=True, max_length=64, null=True)),
                ('transaction_comment', models.CharField(blank=True, max_length=256, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pos.user')),
            ],
        ),
    ]