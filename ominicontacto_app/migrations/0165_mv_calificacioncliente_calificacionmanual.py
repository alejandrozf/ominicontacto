# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def mover_CalificacionManual_a_CalificacionCliente(apps, schema_editor):
    """
    Mover informacion de CalificacionManual a CalificacionCliente
    Mover informacion de AgendaManual a AgendaContacto
    """
    CalificacionManual = apps.get_model('ominicontacto_app', 'calificacionmanual')
    CalificacionCliente = apps.get_model('ominicontacto_app', 'calificacioncliente')
    AgendaManual = apps.get_model('ominicontacto_app', 'agendamanual')
    AgendaContacto = apps.get_model('ominicontacto_app', 'agendacontacto')

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

        # Ver si tiene AgendaManual para pasar a AgendaContacto
        agendas = AgendaManual.objects.filter(
            campana=manual.opcion_calificacion.campana,
            telefono=manual.contacto.telefono,
            agente=manual.agente)
        for agenda_manual in agendas:
            agenda_contacto = AgendaContacto(
                agente=agenda_manual.agente,
                contacto=manual.contacto,
                fecha=agenda_manual.fecha,
                hora=agenda_manual.hora,
                tipo_agenda=agenda_manual.tipo_agenda,
                observaciones=agenda_manual.observaciones,
                campana=agenda_manual.campana)
            agenda_contacto.save()
            agenda_manual.delete()
        manual.delete()


def rollback(apps, schema_editor):
    """
    Mover informacion de CalificacionCliente a CalificacionManual
    """
    CalificacionManual = apps.get_model('ominicontacto_app', 'calificacionmanual')
    CalificacionCliente = apps.get_model('ominicontacto_app', 'calificacioncliente')
    AgendaManual = apps.get_model('ominicontacto_app', 'agendamanual')
    AgendaContacto = apps.get_model('ominicontacto_app', 'agendacontacto')

    manuales = CalificacionCliente.objects.filter(es_calificacion_manual=True)
    for cliente in manuales:
        # Creo una nueva CalificacionManual
        nueva = CalificacionManual(contacto=cliente.contacto,
                                   es_venta=cliente.es_venta,
                                   opcion_calificacion=cliente.opcion_calificacion,
                                   fecha=cliente.fecha,
                                   agente=cliente.agente,
                                   observaciones=cliente.observaciones,
                                   wombat_id=cliente.wombat_id,
                                   agendado=cliente.agendado)
        nueva.save()

        # Ver si tiene AgendaManual para pasar a AgendaContacto
        agendas = AgendaContacto.objects.filter(
            campana=cliente.opcion_calificacion.campana,
            contacto=cliente.contacto,
            agente=cliente.agente)
        for agenda_contacto in agendas:
            agenda_manual = AgendaManual(
                agente=agenda_contacto.agente,
                telefono=agenda_contacto.contacto.telefono,
                fecha=agenda_contacto.fecha,
                hora=agenda_contacto.hora,
                tipo_agenda=agenda_contacto.tipo_agenda,
                observaciones=agenda_contacto.observaciones,
                campana=agenda_contacto.campana)
            agenda_manual.save()
            agenda_contacto.delete()
        cliente.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0164_calificacioncliente_es_calificacion_manual'),
    ]

    operations = [
        migrations.RunPython(mover_CalificacionManual_a_CalificacionCliente,
                             reverse_code=rollback),
    ]
