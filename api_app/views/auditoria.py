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

import logging as _logging
import threading
import json
import redis

from django.conf import settings
from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from django.utils.encoding import force_text
from django.shortcuts import redirect


from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from ominicontacto_app.services.reporte_auditoria_csv import ExportacionArchivoCSV
from ominicontacto_app.models import CalificacionCliente

logger = _logging.getLogger(__name__)


class ReporteCSV:

    redis_connection = redis.Redis(
        host=settings.REDIS_HOSTNAME,
        port=settings.CONSTANCE_REDIS_CONNECTION['port'],
        decode_responses=True)


class ReporteCalificacionesCampanaCSV(ReporteCSV):

    def __init__(self, key_task, calificaciones_id, mostrar_detalles):
        self.datos = []
        self.mostrar_detalles = mostrar_detalles
        calificaciones = CalificacionCliente.objects.all() \
            .select_related(
            'opcion_calificacion', 'contacto').prefetch_related(
                'contacto__bd_contacto', 'agente__user').filter(
            id__in=calificaciones_id)
        cant_calificaciones = calificaciones.count()
        if cant_calificaciones == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        calificaciones_analizadas = set()
        self.redis_connection.publish(key_task, porcentaje_inicial)
        self._escribir_encabezado()
        for i, calificacion in enumerate(calificaciones, start=1):
            percentage = int((i / cant_calificaciones) * 100)
            self.redis_connection.publish(key_task, percentage)
            if calificacion and (calificacion.pk not in calificaciones_analizadas):
                self._escribir_linea_calificacion(calificacion, calificacion)
                calificaciones_analizadas.add(calificacion.pk)

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Fecha-Hora"))
        encabezado.append(_("Agente"))
        encabezado.append(_("Contacto ID"))
        encabezado.append(_("Telefono"))
        encabezado.append(_("Status"))
        if self.mostrar_detalles:
            encabezado.append(_("Calificado"))
            encabezado.append(_("Observaciones"))
        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_calificacion(self, calificacion, log_llamada):
        lista_opciones = []
        calificacion_fecha_local = localtime(calificacion.modified)
        lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        lista_opciones.append(calificacion.agente)
        lista_opciones.append(calificacion.contacto.id)
        lista_opciones.append(calificacion.contacto.telefono)
        auditoria = calificacion.obtener_auditoria()
        if auditoria:
            auditoria = auditoria.get_resultado_display()
        else:
            auditoria = _("Pendiente")
        lista_opciones.append(auditoria)
        if self.mostrar_detalles:
            opcion_calificacion_nombre = calificacion.opcion_calificacion.nombre
            if calificacion.opcion_calificacion.es_agenda():
                opcion_calificacion_nombre = "{} {}".\
                    format(opcion_calificacion_nombre, calificacion.get_tipo_agenda_display())
            lista_opciones.append(opcion_calificacion_nombre)
            lista_opciones.append(calificacion.observaciones.replace('\r\n', ' '))
        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)


class ObtenerArchivoAuditoriaView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    http_method_names = ['post', 'get']

    def generar_csv_calificaciones(
            self, key_task, supervisor_id, calificaciones_id, mostrar_detalles):
        reporte_calificados_csv =\
            ReporteCalificacionesCampanaCSV(key_task, calificaciones_id, mostrar_detalles)
        datos_calificados = reporte_calificados_csv.datos
        nombre_reporte = "auditoria_{}".format(supervisor_id)
        service_csv = ExportacionArchivoCSV(nombre_reporte)
        service_csv.exportar_reportes_csv(datos=datos_calificados)

    def post(self, request):
        params = request.POST
        calificaciones_id = json.loads(params.get('calificaciones_id'))
        mostrar_detalles = json.loads(params.get('mostrar_detalles'))
        supervisor_id = request.user.id
        TASK_ID = 'csv'
        key_task = 'OML:STATUS_DOWNLOAD:DISPOSITIONED:{0}:{1}'.format(supervisor_id, TASK_ID)
        thread_exportacion = threading.Thread(
            target=self.generar_csv_calificaciones,
            args=[key_task, supervisor_id, calificaciones_id, mostrar_detalles])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de auditoria a .csv en proceso'),
            'id': TASK_ID,
        })

    def get(self, request):
        supervisor_id = request.user.id
        nombre_reporte = "auditoria_{}".format(supervisor_id)
        service_csv = ExportacionArchivoCSV(nombre_reporte)
        url = service_csv.obtener_url_reporte_csv_descargar()
        return redirect(url)
