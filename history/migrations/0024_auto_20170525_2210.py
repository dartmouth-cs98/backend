# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-25 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0023_page_keywords'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='keywords',
        ),
        migrations.AddField(
            model_name='page',
            name='topwords',
            field=models.TextField(default='{}'),
        ),
    ]
