# -*- coding: utf-8 -*-
# Generated Federico Peker
from __future__ import unicode_literals

from django.db import migrations
from ominicontacto_app.models import Campana


def create_delete_objects_models(apps, schema_editor):
    Campana.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0102_auto_20170529_1517'),
    ]

    operations = [
        migrations.RunPython(create_delete_objects_models),
    ]