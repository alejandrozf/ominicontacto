# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms import ValidationError
from django.utils.translation import ugettext as _

from ominicontacto_app.models import CalificacionCliente


def validar_extension_archivo_audio(valor):
    if valor is not None and not valor.name.endswith('.wav'):
        raise ValidationError(_('Archivos permitidos: .wav'), code='invalid')


def obtener_cantidad_no_calificados(total_llamadas_qs, fecha_desde, fecha_hasta, campana):
    total_llamadas_campanas = total_llamadas_qs.count()
    total_calificados = CalificacionCliente.history.filter(
        fecha__range=(fecha_desde, fecha_hasta),
        opcion_calificacion__campana=campana, history_change_reason='calificacion').count()
    total_atendidas_sin_calificacion = total_llamadas_campanas - total_calificados
    if total_atendidas_sin_calificacion < 0:
        # significa que el agente calificó llamadas que no conectaron con el usuario
        total_atendidas_sin_calificacion = 0
    return total_atendidas_sin_calificacion
