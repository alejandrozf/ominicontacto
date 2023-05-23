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

from __future__ import unicode_literals

from collections import OrderedDict
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db import connection
from ominicontacto_app.models import CalificacionCliente, Campana, AgenteEnContacto
from reportes_app.reportes.reporte_llamados_contactados_csv import NO_CONECTADO_DESCRIPCION
from reportes_app.models import LlamadaLog


class ReporteDeResultadosDeCampana(object):
    """
    Reporte sobre los resultados de las contactaciones de los contactos ORIGINIARIOS.
    """

    def __init__(self, campana, todos_contactos=False, page_number=None, page_size=10):
        self.campana = campana

        self.contactaciones = OrderedDict()
        contactos = self.obtener_contactos(todos_contactos)
        if page_number is not None:
            self.paginator = Paginator(contactos, page_size)
            self.page = self.paginator.page(page_number)
            contactos = self.page.object_list
        contactos_ids = self._inicializar_datos_de_contactacion(contactos)
        # Si no hay contactos originarios el reporte quedará vacío.
        if len(contactos_ids) > 0:
            calificados_ids = self._registrar_calificaciones(contactos_ids)
            self._registrar_no_calificados(contactos_ids, calificados_ids)

    def obtener_contactos(self, todos_contactos):
        contactos = self.campana.bd_contacto.contactos.order_by("id")
        if self.campana.type == Campana.TYPE_PREVIEW:
            contactos = contactos.filter(es_originario=True)
            if todos_contactos:
                return contactos
            ids_activos = AgenteEnContacto.objects.activos(self.campana.id).values_list(
                'contacto_id')
            return contactos.filter(id__in=ids_activos)

        if todos_contactos:
            return contactos
        else:
            return contactos.filter(es_originario=True)

    @property
    def is_paginated(self):
        return hasattr(self, "paginator") and hasattr(self, "page")

    def _inicializar_datos_de_contactacion(self, contactos):
        ids = []
        for contacto in contactos:
            ids.append(contacto.id)
            self.contactaciones[contacto.id] = {
                'contacto': contacto,
                'calificacion': None,
                'contactacion': None
            }
        return ids

    def _registrar_calificaciones(self, contactos_ids):
        calificaciones = CalificacionCliente.objects.using('replica').filter(
            opcion_calificacion__campana=self.campana,
            contacto_id__in=contactos_ids)
        calificados_ids = []
        for calificacion in calificaciones:
            contacto_id = calificacion.contacto_id
            calificados_ids.append(contacto_id)
            nombre = calificacion.opcion_calificacion.nombre
            self.contactaciones[contacto_id]['calificacion'] = nombre
        return calificados_ids

    def _registrar_no_calificados(self, contactos_ids, calificados_ids):
        # Ver como fue la contactacion. Si fue o no contactado.
        filtro_contactos = " AND contacto_id IN ('"
        filtro_contactos += "','".join([str(x) for x in contactos_ids])
        filtro_contactos += "')"
        filtro_calificados = ''
        if len(calificados_ids) > 0:
            filtro_calificados = " AND contacto_id NOT IN ('"
            filtro_calificados += "','".join([str(x) for x in calificados_ids])
            filtro_calificados += "')"
        filtro_eventos = " AND event IN ('"
        filtro_eventos += "','".join(LlamadaLog.EVENTOS_NO_CONEXION)
        filtro_eventos += "','"
        filtro_eventos += "','".join(LlamadaLog.EVENTOS_FIN_CONEXION)
        filtro_eventos += "')"
        params = {'campana_id': self.campana.id,
                  'filtro_contactos': filtro_contactos,
                  'filtro_calificados': filtro_calificados,
                  'filtro_eventos': filtro_eventos}
        # TODO: Filtrar eventos de LLamada log q indiquen finalizacion de llamada o intento
        sql = """
            SELECT contacto_id, event
            FROM (
                SELECT id, campana_id, event, numero_marcado, contacto_id, "time",
                       max("time") OVER (PARTITION BY contacto_id) max_my_date
                FROM public.reportes_app_llamadalog
                WHERE campana_id = {campana_id} AND contacto_id != -1
                {filtro_contactos}{filtro_calificados}{filtro_eventos}
            ) sub_query
            WHERE "time" = max_my_date """.format(**params)

        cursor = connection.cursor()
        cursor.execute(sql)
        values = cursor.fetchall()
        for contacto_id, evento in values:
            descripcion = self._get_descripcion_evento(evento)
            self.contactaciones[contacto_id]['contactacion'] = descripcion

    def _get_descripcion_evento(self, evento):
        if evento in LlamadaLog.EVENTOS_NO_CONEXION:
            return NO_CONECTADO_DESCRIPCION[evento]
        if evento in LlamadaLog.EVENTOS_FIN_CONEXION:
            return _("Contactado")
        # No debería ocurrir:
        return _("Sin datos")
