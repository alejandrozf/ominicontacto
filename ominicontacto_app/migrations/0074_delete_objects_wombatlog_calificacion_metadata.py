# -*- coding: utf-8 -*-
# Generated Federico Peker

# TODO: Eliminar esta migración y todas las de igual semántica

from __future__ import unicode_literals

from django.db import migrations
from ominicontacto_app.models import WombatLog, MetadataCliente


def create_delete_objects_models(apps, schema_editor):
    WombatLog.objects.all().delete()
    MetadataCliente.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0073_remove_metadatacliente_campana'),
    ]

    operations = [
        migrations.RunPython(create_delete_objects_models),
    ]
