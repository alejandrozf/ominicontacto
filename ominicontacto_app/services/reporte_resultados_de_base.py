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

"""
Servicio para generar reporte csv para todas las calificaciones de una campana
"""

from __future__ import unicode_literals

import logging

from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from ominicontacto_app.services.reporte_resultados_de_base_csv import (
    ReporteCSV
)
from reportes_app.reportes.reporte_resultados import (
    ReporteDeResultadosDeCampana
)

logger = logging.getLogger(__name__)


class ReporteContactacionesCSV(ReporteCSV):

    def __init__(self, campana, key_task, todos_contactos=False):
        self.campana = campana
        self.datos = []
        self.reporte = ReporteDeResultadosDeCampana(
            self.campana,
            todos_contactos=todos_contactos
        )
        self.contactaciones = self.reporte.contactaciones.values()
        cant_contactaciones = len(self.contactaciones)

        if cant_contactaciones == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        self.redis_connection.publish(key_task, porcentaje_inicial)
        self._escribir_encabezado()
        for i, contactacion in enumerate(self.contactaciones, start=1):
            percentage = int((i / cant_contactaciones) * 100)
            self.redis_connection.publish(key_task, percentage)
            self._escribir_linea_contactacion(contactacion)

    def _escribir_encabezado(self):
        encabezado = []
        nombres = self.campana.bd_contacto.get_metadata().nombres_de_columnas
        for nombre in nombres:
            encabezado.append(nombre)
        encabezado.append(_("Calificación"))
        encabezado.append(_("Contactación"))

        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_contactacion(self, contactacion):
        lista_opciones = []
        datos = contactacion['contacto'].lista_de_datos_completa()
        lista_opciones.extend(datos)
        if contactacion['calificacion'] is not None:
            lista_opciones.append(contactacion['calificacion'])
        else:
            lista_opciones.append('')
        if contactacion['contactacion'] is not None:
            lista_opciones.append(contactacion['contactacion'])
        else:
            lista_opciones.append('')

        lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_opciones_utf8)
