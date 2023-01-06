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
from django.utils.timezone import timedelta

from ominicontacto_app.models import Campana

register = Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def format_seconds(seconds):
    return str(timedelta(seconds=seconds))


@register.filter(name='get_class')
def get_class(value):
    return value.__class__.__name__


@register.filter(name='interaccion_crm')
def interaccion_crm(value):
    return value in [Campana.SITIO_EXTERNO, Campana.FORMULARIO_Y_SITIO_EXTERNO]
