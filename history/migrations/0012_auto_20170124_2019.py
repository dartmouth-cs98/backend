# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-24 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0011_page_blacklisted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='favicon',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.TextField(),
        ),
    ]