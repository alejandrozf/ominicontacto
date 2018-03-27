# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def mover_CalificacionManual_a_CalificacionCliente(apps, schema_editor):
    """
    Mover informacion de CalificacionManual a CalificacionCliente
    """
    CalificacionManual = apps.get_model('ominicontacto_app', 'calificacionmanual')
    CalificacionCliente = apps.get_model('ominicontacto_app', 'calificacioncliente')

    manuales = CalificacionManual.objects.all()
    for manual in manuales:
        # Creo una nueva CalificacionCliente
        cliente = CalificacionCliente(contacto=manual.contacto,
                                      es_venta=manual.es_venta,
                                      opcion_calificacion=manual.opcion_calificacion,
                                      fecha=manual.fecha,
                                      agente=manual.agente,
                                      observaciones=manual.observaciones,
                                      wombat_id=manual.wombat_id,
                                      agendado=manual.agendado,
                                      es_calificacion_manual=True)
        cliente.save()
        manual.delete()

def rollback(apps, schema_editor):
    """
    Mover informacion de CalificacionCliente a CalificacionManual
    """
    CalificacionManual = apps.get_model('ominicontacto_app', 'calificacionmanual')
    CalificacionCliente = apps.get_model('ominicontacto_app', 'calificacioncliente')

    manuales = CalificacionCliente.objects.filter(es_calificacion_manual=True)
    for manual in manuales:
        # Creo una nueva CalificacionManual
        nueva = CalificacionManual(contacto=manual.contacto,
                                   es_venta=manual.es_venta,
                                   opcion_calificacion=manual.opcion_calificacion,
                                   fecha=manual.fecha,
                                   agente=manual.agente,
                                   observaciones=manual.observaciones,
                                   wombat_id=manual.wombat_id,
                                   agendado=manual.agendado)
        nueva.save()
        manual.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0164_calificacioncliente_es_calificacion_manual'),
    ]

    operations = [
        migrations.RunPython(mover_CalificacionManual_a_CalificacionCliente,
                             reverse_code=rollback),
    ]
