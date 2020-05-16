# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from django.template import Library

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
