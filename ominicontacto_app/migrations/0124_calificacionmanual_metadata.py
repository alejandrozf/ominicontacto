# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-04 14:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0123_remove_calificacionmanual_wombat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='calificacionmanual',
            name='metadata',
            field=models.TextField(blank=True, null=True),
        ),
    ]