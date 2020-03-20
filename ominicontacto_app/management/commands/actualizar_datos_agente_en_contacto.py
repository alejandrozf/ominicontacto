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
from __future__ import unicode_literals

import logging
import json
from ast import literal_eval

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from ominicontacto_app.models import AgenteEnContacto, Campana

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Actualiza los datos de la 'cache' de AgenteEnContacto con los datos actuales del modelo
    Contacto de todos los contactos de la base de datos indicada
    """

    help = u'Actualiza datos de AgenteEnContacto para la campaña indicada'

    def add_arguments(self, parser):
        parser.add_argument('campaign_id', type=int)

    def _actualizar_datos_agente_en_contacto(self, campaign_id):
        """
        Procedimiento que actualiza los datos en la 'cache' de AgenteEnCampana para la base
        de datos de la campaña indicada
        """
        try:
            campana = Campana.objects.get(id=campaign_id)
        except Campana.DoesNotExist:
            logger.error(_('No existe una campaña con id: {0}').format(campaign_id))
            return

        bd_contacto = campana.bd_contacto
        campos_contacto = bd_contacto.get_metadata().nombres_de_columnas_de_datos

        modificados = 0
        creados = 0
        for contacto in bd_contacto.contactos.all():
            datos_contacto = literal_eval(contacto.datos)
            datos_contacto = dict(zip(campos_contacto, literal_eval(contacto.datos)))
            datos_contacto_json = json.dumps(datos_contacto)
            defaults = {
                'agente_id': -1,
                'datos_contacto': datos_contacto_json,
                'telefono_contacto': contacto.telefono,
                'estado': AgenteEnContacto.ESTADO_INICIAL,
                'es_originario': False
            }
            aec, created = AgenteEnContacto.objects.get_or_create(
                contacto_id=contacto.id, campana_id=campana.id, defaults=defaults)
            if not created:
                aec.telefono_contacto = contacto.telefono
                aec.datos_contacto = datos_contacto_json
                aec.save()
                modificados += 1
            else:
                creados += 1

        msg = _('Actualizando {0}  y creando {1} AgentesEnContacto para la campaña con id:'
                ' {2}').format(modificados, creados, campaign_id)
        print(msg)
        logger.info(msg)

    def handle(self, campaign_id, **options):
        try:
            self._actualizar_datos_agente_en_contacto(campaign_id)
        except Exception as e:
            logger.error(_('Fallo del comando: {0}').format(e))
