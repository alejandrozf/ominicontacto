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
import re

from time import time

from django.utils.translation import ugettext as _


logger = logging.getLogger(__name__)


class AgentesParsing(object):
    """Encapsula todos las acciones destinadas a obtener datos sobre los agentes
    del sistema en forma legible
    """

    headers_agente_regex = re.compile(r'.*(NAME|SIP|STATUS).*')
    headers_agente_regex_group = re.compile(r'(NAME|SIP|STATUS)')
    id_agente = re.compile(r'[1-9][0-9]*')

    def _chequear_procesar_entrada(self, linea):
        # para filtrar entradas que no nos interesan, como ids de pausas
        # si la entrada brinda los datos que necesitamos del agente
        # se procesa y se devuelve, en caso contrario se retorna 'False'
        linea_procesada = linea.replace('Output: ', '')
        try:
            clave, valor = linea_procesada.split(': ')
        except ValueError:
            return False
        else:
            if self.headers_agente_regex.match(clave) is not None:
                return (clave.strip(), valor.strip())
        return False

    def _parsear_entrada_agente(self, valor_linea_procesada):
        # convierte una entrada con formato (/OML/AGENT/1/NAME, 'agente nombre')
        # en un dict como {'id': '1', 'nombre': 'agente_nombre'}
        entrada_agente = {}
        map_keys = {
            'NAME': 'nombre',
            'SIP': 'sip'
        }
        key_part, value_part = valor_linea_procesada
        id_agente = self.id_agente.search(key_part).group(0)
        header = self.headers_agente_regex_group.search(key_part).group(0)
        entrada_agente['id'] = id_agente
        if header == 'STATUS':
            # obtener timestamp desde value
            status, timestamp = value_part.split(':')
            entrada_agente['status'] = status
            tiempo_actual = int(time())
            tiempo_estado = tiempo_actual - int(timestamp)
            entrada_agente['tiempo'] = tiempo_estado
        else:
            entrada_agente[map_keys[header]] = value_part
        if value_part == '':
            logger.warning(_('Esta entrada tiene datos incompletos: {0}'.format(
                valor_linea_procesada)))
        return entrada_agente

    def _pertenece_grupo_actual_agente(self, entrada_agente, grupo_datos_agente):
        if grupo_datos_agente == {}:
            return True
        else:
            id_grupo = grupo_datos_agente['id']
            id_entrada_agente = entrada_agente['id']
            return id_grupo == id_entrada_agente

    def _parsear_datos_agentes(self, datos):
        # para obtener las entradas de los agentes agrupados en una lista de diccionarios
        lineas = datos.split('\r\n')
        grupo_datos_agente = {}
        agentes_activos = []
        for i, linea in enumerate(lineas):
            valor_linea_procesada = self._chequear_procesar_entrada(linea)
            if valor_linea_procesada:
                entrada_agente = self._parsear_entrada_agente(valor_linea_procesada)
                if self._pertenece_grupo_actual_agente(
                        entrada_agente, grupo_datos_agente):
                    grupo_datos_agente.update(entrada_agente)
                else:
                    if len(grupo_datos_agente) != 5:
                        logger.warning(
                            _("Inconsistencias en datos de agente: {0}".format(grupo_datos_agente)))
                    else:
                        agentes_activos.append(grupo_datos_agente)
                    grupo_datos_agente = entrada_agente
            if i == len(lineas) - 1 and len(grupo_datos_agente) == 5:
                agentes_activos.append(grupo_datos_agente)
                grupo_datos_agente = {}
            elif i == len(lineas) - 1 and len(grupo_datos_agente) != 5:
                logger.warning(
                    _("Inconsistencias en datos de agente: {0}".format(grupo_datos_agente)))
        return agentes_activos
