# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from django.template import Library
from reportes_app.models import LlamadaLog

register = Library()


@register.simple_tag
def es_calificacion_llamada(grabacion, calificacion):
    """Determina si la calificación es la exacta de la llamada que generó
    la grabación
    """
    if grabacion.callid == calificacion.callid and \
       calificacion.history_change_reason == 'calificacion':
        # no es una recalificacion sin llamada
        return calificacion
    return False


@register.filter(name='select_contacto_id')
def select_contacto_id(grabacion):
    """Devuelve el id del contacto de la grabación"""
    if int(grabacion.contacto_id) == -1:
        return LlamadaLog.objects.filter(callid=grabacion.callid).first().contacto_id
    return grabacion.contacto_id
