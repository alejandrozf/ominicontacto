# -*- coding: utf-8 -*-
# Generated Federico Peker
from __future__ import unicode_literals

from django.db import migrations
from ominicontacto_app.models import ActuacionVigente, ReglasIncidencia


def create_delete_objects_models(apps, schema_editor):
    ActuacionVigente.objects.all().delete()
    ReglasIncidencia.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0099_auto_20170526_1418'),
    ]

    operations = [
        migrations.RunPython(create_delete_objects_models),
    ]