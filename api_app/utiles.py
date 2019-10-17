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

import re
import logging as _logging

from time import time

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from django.conf import settings

logger = _logging.getLogger(__name__)


class EstadoAgentesService:
    """Encapsula todos las acciones destinadas a obtener datos sobre los agentes
    del sistema en forma legible usando AMI
    """

    headers_agente_regex = re.compile(r'.*(NAME|SIP|STATUS).*')
    id_agente = re.compile(r'[1-9][0-9]*')

    def _ami_obtener_agentes(self, manager):
        return manager.command("database show OML/AGENT").data

    def _parsear_datos_agentes_pasada_1(self, datos):
        # para filtrar entradas que no nos interesan, como ids de pausas
        lineas = datos.split('\r\n')
        lineas_result = []
        for linea_raw in lineas:
            linea = linea_raw.replace('Output: ', '')
            try:
                clave, valor = linea.split(': ')
            except ValueError:
                pass
            else:
                if self.headers_agente_regex.match(clave) is not None:
                    lineas_result.append((clave.strip(), valor.strip()))
        return lineas_result

    def _parsear_datos_agentes_pasada_2(self, datos):
        # para obtener las entradas de los agentes agrupados en una lista de diccionarios
        agentes_activos = []
        tiempo_actual = int(time())
        for i in xrange(0, len(datos), 3):
            sip_agente = datos[i + 1][1]
            status_agente = datos[i + 2][1]
            try:
                nombre_status, timestamp = status_agente.split(':')
            except ValueError:
                pass
            else:
                nombre_agente = datos[i][1]
                id_agente = self.id_agente.search(datos[i][0]).group(0)
                tiempo_estado = tiempo_actual - int(timestamp)
                agente = {
                    'nombre': nombre_agente,
                    'id': id_agente,
                    'status': nombre_status,
                    'tiempo': tiempo_estado,
                    'sip': sip_agente,
                }
                agentes_activos.append(agente)
        return agentes_activos

    def _obtener_agentes_activos_ami(self):
        manager = Manager()
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.ASTERISK_HOSTNAME)
        agentes_activos = []
        try:
            manager.connect(ami_manager_host)
            manager.login(ami_manager_user, ami_manager_pass)
            agentes_activos_raw = self._parsear_datos_agentes_pasada_1(
                self._ami_obtener_agentes(manager))
            agentes_activos = self._parsear_datos_agentes_pasada_2(agentes_activos_raw)
        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e.message))
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e.message))
        except ManagerException as e:
            logger.exception("Error {0}".format(e.message))
        finally:
            manager.close()
            return agentes_activos

    def obtener_agentes_activos(self):
        return self._obtener_agentes_ami()
