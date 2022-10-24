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
Servicio para generar reporte csv de las reportes de los agentes
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json
import time

import redis

from django.conf import settings
from django.utils.encoding import force_text
from django.core.paginator import Paginator

from django.utils.translation import gettext as _
from django.utils.timezone import localtime, timedelta

from ominicontacto_app.utiles import crear_archivo_en_media_root

from ominicontacto_app.models import (
    BaseDatosContacto, Campana, Contacto, OpcionCalificacion, HistoricalCalificacionCliente)
from ominicontacto_app.services.estadisticas_campana import EstadisticasBaseCampana

from reportes_app.models import LlamadaLog

logger = logging.getLogger(__name__)

NO_CONECTADO_DESCRIPCION = {
    'NOANSWER': _('Cliente no atiende'),
    'CANCEL': _('Se corta antes que atienda el cliente'),
    'BUSY': _('Ocupado'),
    'CHANUNAVAIL': _('Canales Saturados'),
    'OTHER': _('Motivo no especificado'),
    'FAIL': _('Fallo'),
    'AMD': _('Contestador'),
    'BLACKLIST': _('Blacklist'),
    'ABANDON': _('Abandonada por cliente'),
    'EXITWITHTIMEOUT': _('Expirada'),
    'CONGESTION': _('Canal congestionado'),
    'NONDIALPLAN': _('Problema de enrutamiento'),
    'ABANDONWEL': _('Abandonadas durante anuncio'),
}


class ReporteCSV:

    redis_connection = redis.Redis(
        host=settings.REDIS_HOSTNAME,
        # FIXME: debería existir un setting para REDIS_PORT
        port=settings.CONSTANCE_REDIS_CONNECTION['port'],
        decode_responses=True)

    def _obtener_datos_contacto(self, contacto_id, campos_contacto, contactos_dict):
        contacto = contactos_dict.get(contacto_id, -1)
        if contacto != -1:
            return contacto.lista_de_datos_completa()
        return [""] * len(campos_contacto)


class ReporteContactadosCSV(EstadisticasBaseCampana, ReporteCSV):

    def get_es_ultima_calificacion_historica(self, calificacion_historica, calificacion_final):
        """ Si tienen practicamente la misma fecha asumo que corresponden a la misma """
        diff = calificacion_historica.history_date - calificacion_final.modified
        if calificacion_historica.history_date < calificacion_final.modified:
            diff = calificacion_final.modified - calificacion_historica.history_date
        if diff < timedelta(microseconds=100000):
            return True
        return False

    def __init__(self, campana, key_task, fecha_desde, fecha_hasta):
        self.campana = campana
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self._inicializar_valores_estadisticas()
        self._inicializar_respuestas_formulario_gestion_historicas()
        self.contactos_dict = {contacto.pk: contacto
                               for contacto in self.campana.bd_contacto.contactos.all()}
        self.campos_contacto_datos = self.bd_metadata.nombres_de_columnas
        self.datos = []
        self.campos_formulario_opciones = {}
        self.posiciones_opciones = {}
        self._escribir_encabezado()

        logs_llamadas = self._obtener_logs_de_llamadas() \
                            .filter(event__in=LlamadaLog.EVENTOS_FIN_CONEXION) \
                            .exclude(agente_id=-1)

        numero_logs_llamadas = logs_llamadas.count()
        if numero_logs_llamadas == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        self.redis_connection.publish(key_task, porcentaje_inicial)  # percentage of task completed

        callids_analizados = set()
        i = 0
        last_percentage = porcentaje_inicial
        paginator = Paginator(logs_llamadas, 2000)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            for log_llamada in page:
                i += 1
                percentage = int((i / numero_logs_llamadas) * 100)
                if (percentage - last_percentage) >= 10:
                    self.redis_connection.publish(key_task, percentage)
                    last_percentage = percentage

                callid = log_llamada.callid
                try:
                    if callid not in callids_analizados:
                        calificacion_historica = self \
                            .calificaciones_historicas_dict.get(callid, False)
                        if not calificacion_historica:
                            datos_calificacion = [_("Llamada Atendida sin calificacion"),
                                                  '',
                                                  self.agentes_dict.get(log_llamada.agente_id, -1)]
                        else:
                            datos_calificacion = [calificacion_historica.opcion_calificacion.nombre,
                                                  calificacion_historica.observaciones
                                                  .replace('\r\n', ' '),
                                                  calificacion_historica.agente]
                        self._escribir_linea_log(
                            log_llamada, datos_calificacion, calificacion_historica)
                        callids_analizados.add(callid)
                except Exception as e:
                    logger.error("Error generando fila csv: " + e.__str__())
        # Forzar el cierre de la conexión del WS
        time.sleep(1)
        self.redis_connection.publish(key_task, 100)

    def _obtener_datos_contacto_contactados(self, llamada_log, calificacion, datos_contacto):
        tel_status = _('Fuera de base')
        bd_contacto = _('Fuera de base')
        contacto = calificacion.contacto if calificacion else None
        if contacto is None:
            contacto = self.contactos_dict.get(llamada_log.contacto_id)
        if contacto is not None:
            tel_status = _('Contactado')
            datos_contacto = contacto.lista_de_datos_completa()
            if contacto.es_originario:
                bd_contacto = contacto.bd_contacto
        return tel_status, bd_contacto, datos_contacto

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Telefono contactado"))
        campos_contacto = self.bd_metadata.nombres_de_columnas
        # TODO: hacer más prolija esta parte, para evitar futuros desfasajes
        encabezado.extend(campos_contacto)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Agente"))
        encabezado.append(_("Callid"))
        encabezado.append(_("Tipo llamada"))
        encabezado.append(_("id base de datos"))
        encabezado.append(_("base de datos"))
        encabezado.append(_("Duración"))
        encabezado.append(_("Calificado"))
        encabezado.append(_("Observaciones"))

        # agrego el encabezado para los campos de los formularios
        if self.campana.tiene_formulario:
            for opcion in self.campana.opciones_calificacion.filter(
                    tipo=OpcionCalificacion.GESTION).select_related(
                        'formulario').prefetch_related('formulario__campos'):
                if opcion.nombre not in self.posiciones_opciones:
                    self.posiciones_opciones[opcion.id] = len(encabezado)
                    campos = opcion.formulario.campos.all()
                    self.campos_formulario_opciones[opcion.id] = campos
                    encabezado.append(opcion.nombre)
                    for campo in campos:
                        nombre = campo.nombre_campo
                        encabezado.append(nombre)

        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_log(self, llamada_log, datos_calificacion, calificacion):
        datos_contacto = [''] * len(self.campos_contacto_datos)
        respuesta_formulario_gestion = None

        tel_status, bd_contacto, datos_contacto = self.\
            _obtener_datos_contacto_contactados(llamada_log, calificacion, datos_contacto)

        fecha_local_llamada = localtime(llamada_log.time)
        duracion_llamada = llamada_log.duracion_llamada
        if duracion_llamada > 0:
            duracion_llamada = timedelta(0, duracion_llamada)
        else:
            duracion_llamada = 'N/A'
        registro = []
        registro.append(llamada_log.numero_marcado)
        registro.extend(datos_contacto)
        registro.append(fecha_local_llamada.strftime("%Y/%m/%d %H:%M:%S"))
        registro.append(tel_status)
        registro.append(datos_calificacion[2])
        registro.append(llamada_log.callid)
        registro.append(llamada_log.tipo_llamada)
        registro.append(self.campana.bd_contacto_id)
        registro.append(self.campana.bd_contacto)
        registro.append(str(duracion_llamada))
        registro.append(datos_calificacion[0])
        registro.append(datos_calificacion[1])

        if calificacion:
            es_gestion = calificacion.opcion_calificacion.es_gestion()
            if es_gestion:
                respuesta_formulario_gestion = self.respuestas_historicas_por_calificacion.get(
                    calificacion.history_id, None)
            if respuesta_formulario_gestion:
                datos = json.loads(respuesta_formulario_gestion.metadata)
                if respuesta_formulario_gestion.history_change_reason is not None:
                    id_opcion = calificacion.opcion_calificacion_id
                else:
                    logger.warn('Sin datos de gestion para calificacion_id:{}'.format(
                        calificacion.history_id))
                    return
                try:
                    posicion = self.posiciones_opciones[id_opcion]
                except Exception:
                    return
                # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
                posiciones_vacias = posicion - len(registro)
                registro = registro + [''] * posiciones_vacias
                # Columna vacia correspondiente al nombre de la Opcion de calificacion
                registro.append('')
                campos = self.campos_formulario_opciones[id_opcion]
                for campo in campos:
                    registro.append(datos.get(campo.nombre_campo, '').replace('\r\n', ' '))

        lista_datos_utf8 = [force_text(item) for item in registro]
        self.datos.append(lista_datos_utf8)


class ReporteCalificadosCSV(EstadisticasBaseCampana, ReporteCSV):

    def __init__(
            self, campana, key_task, fecha_desde, fecha_hasta):
        self.campana = campana
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self._inicializar_valores_estadisticas()
        self.contactos_dict = {contacto.pk: contacto
                               for contacto in self.campana.bd_contacto.contactos.all()}
        self.campos_contacto_datos = self.bd_metadata.nombres_de_columnas
        self.datos = []
        self.campos_formularios_opciones = {}
        self.posiciones_opciones = {}
        self._escribir_encabezado()

        logs_llamadas = self._obtener_logs_de_llamadas()

        numero_logs_llamadas = logs_llamadas.count()
        if numero_logs_llamadas == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        calificaciones_analizadas = set()
        self.redis_connection.publish(key_task, porcentaje_inicial)  # percentage of task completed
        for i, log_llamada in enumerate(logs_llamadas, start=1):
            percentage = int((i / numero_logs_llamadas) * 100)
            self.redis_connection.publish(key_task, percentage)
            callid = log_llamada.callid
            calificacion_historica = self.calificaciones_historicas_dict.get(callid, False)
            calificacion_final = self.calificaciones_finales_dict.get(callid, False)
            if campana.es_entrante:
                calificacion = calificacion_historica
            else:
                calificacion = calificacion_final
            if calificacion and (calificacion.pk not in calificaciones_analizadas):
                self._escribir_linea_calificacion(calificacion, log_llamada)
                calificaciones_analizadas.add(calificacion.pk)

    def _escribir_encabezado(self):
        # Creamos encabezado
        encabezado = []
        campos_contacto = self.bd_metadata.nombres_de_columnas
        encabezado.extend(campos_contacto)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Tel contactado"))
        encabezado.append(_("Calificado"))
        encabezado.append(_("Observaciones"))
        encabezado.append(_("Agente"))
        encabezado.append(_("base de datos"))
        encabezado.append(_("Callid"))
        encabezado.append(_("Tipo llamada"))
        # agrego el encabezado para los campos de los formularios
        if self.campana.tiene_formulario:
            for opcion in self.opciones_calificacion_campana.values():
                if opcion.id not in self.posiciones_opciones and \
                   opcion.tipo == OpcionCalificacion.GESTION:
                    self.posiciones_opciones[opcion.id] = len(encabezado)
                    campos = opcion.formulario.campos.all()
                    self.campos_formularios_opciones[opcion.id] = campos
                    encabezado.append(opcion.nombre)
                    for campo in campos:
                        nombre = campo.nombre_campo
                        encabezado.append(nombre)
        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_calificacion(self, calificacion_val, log_llamada):
        lista_opciones = []
        # --- Buscamos datos
        if self.campana.es_entrante:
            calificacion = calificacion_val
            calificacion_fecha_local = localtime(calificacion_val.history_date)
        else:
            calificacion = calificacion_val
            calificacion_fecha_local = localtime(calificacion.fecha)
        datos = calificacion.contacto.lista_de_datos_completa()
        lista_opciones.extend(datos)
        lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        # analizamos el log para ver si se muestra como contactado o no
        # mas alla de que se haya calificado, ya que deberíamos estar analizando el
        # ultimo evento disponible
        if log_llamada.event in LlamadaLog.EVENTOS_NO_CONEXION:
            lista_opciones.append(NO_CONECTADO_DESCRIPCION[log_llamada.event])
        else:
            lista_opciones.append(_("Contactado"))
        numero_marcado = log_llamada.numero_marcado
        lista_opciones.append(numero_marcado)
        lista_opciones.append(calificacion.opcion_calificacion.nombre)
        lista_opciones.append(calificacion.observaciones.replace('\r\n', ' '))
        lista_opciones.append(calificacion.agente)
        if calificacion.contacto.es_originario:
            lista_opciones.append(calificacion.contacto.bd_contacto)
        else:
            lista_opciones.append(_("Fuera de base"))
        lista_opciones.append(log_llamada.callid)
        lista_opciones.append(log_llamada.tipo_llamada)

        if isinstance(calificacion_val, HistoricalCalificacionCliente) and \
           calificacion_val.history_date == calificacion.modified:
            # Es una calificacion historica que no es la ultima sobre el contacto
            # (campaña entrante)
            respuesta_formulario_gestion = None
        else:
            calificacion_id = calificacion.pk
            if isinstance(calificacion, HistoricalCalificacionCliente):
                calificacion_id = calificacion.history_object.pk
            respuesta_formulario_gestion = self.respuestas_formulario_gestion_dict.get(
                calificacion_id)
        if (calificacion.opcion_calificacion.es_gestion() and
            self.campana.tiene_formulario and
                respuesta_formulario_gestion is not None):
            datos = json.loads(respuesta_formulario_gestion.metadata)

            # Agrego Datos de la respuesta del formulario
            datos = json.loads(respuesta_formulario_gestion.metadata)
            id_opcion = respuesta_formulario_gestion.calificacion.opcion_calificacion_id
            posicion = self.posiciones_opciones[id_opcion]
            # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
            posiciones_vacias = posicion - len(lista_opciones)
            lista_opciones = lista_opciones + [''] * posiciones_vacias
            # Columna vacia correspondiente al nombre de la Opcion de calificacion
            lista_opciones.append('')
            campos = self.campos_formularios_opciones[id_opcion]
            for campo in campos:
                lista_opciones.append(
                    datos.get(campo.nombre_campo, '').replace('\r\n', ' '))

        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)


class ReporteNoAtendidosCSV(EstadisticasBaseCampana, ReporteCSV):
    def __init__(self, campana, key_task, fecha_desde, fecha_hasta):
        self.campana = campana
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.bd_metadata = self.campana.bd_contacto.get_metadata()
        self.campos_contacto = self.bd_metadata.nombres_de_columnas
        self.datos = []
        self.contactos_dict = {contacto.pk: contacto
                               for contacto in self.campana.bd_contacto.contactos.all()}
        self.agentes_dict = {}
        self._inicializar_valores_agentes()
        self._escribir_encabezado()
        logs_llamadas = self._obtener_logs_de_llamadas()

        self.inicializar_datos_contacto_base_anterior(logs_llamadas)

        numero_logs_llamadas = logs_llamadas.count()
        if numero_logs_llamadas == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        self.redis_connection.publish(key_task, porcentaje_inicial)  # percentage of task completed
        for i, log_llamada in enumerate(logs_llamadas, start=1):
            percentage = int((i / numero_logs_llamadas) * 100)
            self.redis_connection.publish(key_task, percentage)
            self._escribir_linea_log(log_llamada, self.contactos_dict, self.agentes_dict)

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Telefono de llamada"))
        encabezado.extend(self.bd_metadata.nombres_de_columnas)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Agente"))
        encabezado.append(_("Callid"))
        encabezado.append(_("Tipo llamada"))
        encabezado.append(_("id base de datos"))
        encabezado.append(_("base de datos"))

        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_log(self, log_no_contactado, contactos_dict, agentes_dict):
        lista_opciones = []
        # --- Buscamos datos
        log_no_contactado_fecha_local = localtime(log_no_contactado.time)
        estado = NO_CONECTADO_DESCRIPCION.get(log_no_contactado.event, False)
        if estado:
            lista_opciones.append(log_no_contactado.numero_marcado)
            contacto_id = log_no_contactado.contacto_id
            if contacto_id in self.contactos_anteriores:
                datos_contacto, bd_contacto_id, bd_contacto = \
                    self._obtener_datos_contacto_anterior(contacto_id)
            else:
                datos_contacto = self._obtener_datos_contacto(
                    contacto_id, self.campos_contacto, contactos_dict)
                bd_contacto_id = self.campana.bd_contacto.id
                bd_contacto = self.campana.bd_contacto

            lista_opciones.extend(datos_contacto)
            lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
            lista_opciones.append(estado)
            tipo_llamada = log_no_contactado.tipo_llamada
            if tipo_llamada == Campana.TYPE_DIALER:
                agente_info = "DIALER"
            elif tipo_llamada == Campana.TYPE_ENTRANTE:
                agente_info = "IN"
            else:
                agente_info = agentes_dict.get(log_no_contactado.agente_id, -1)
            lista_opciones.append(agente_info)
            lista_opciones.append(log_no_contactado.callid)
            lista_opciones.append(log_no_contactado.tipo_llamada)
            lista_opciones.append(bd_contacto_id)
            lista_opciones.append(bd_contacto)

            # --- Finalmente, escribimos la linea
            lista_datos_utf8 = [force_text(item) for item in lista_opciones]
            self.datos.append(lista_datos_utf8)

    def inicializar_datos_contacto_base_anterior(self, logs_llamadas):
        id_contactos_anteriores = set(logs_llamadas.values_list('contacto_id', flat=True))
        id_contactos_anteriores.difference_update(self.contactos_dict.keys())
        contactos_anteriores = Contacto.objects.filter(id__in=id_contactos_anteriores)
        self.contactos_anteriores = {
            contacto.pk: contacto for contacto in contactos_anteriores}

        self.nombres_bases = {base.id: str(base) for base in BaseDatosContacto.objects.all()}

    def _obtener_datos_contacto_anterior(self, contacto_id):
        contacto = self.contactos_anteriores.get(contacto_id, -1)
        return (
            contacto.lista_de_datos_completa(),
            contacto.bd_contacto_id,
            self.nombres_bases[contacto.bd_contacto_id]
        )


class ArchivoDeReporteCsv(object):
    def __init__(self, campana, nombre_reporte, datos_reporte):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-{1}".format(self._campana.id, nombre_reporte)
        self.datos_reporte = datos_reporte

        self.sufijo_nombre_de_archivo = ".csv"
        self.nombre_de_archivo = "{0}{1}".format(
            self.prefijo_nombre_de_archivo, self.sufijo_nombre_de_archivo)
        self.url_descarga = os.path.join(settings.MEDIA_URL,
                                         self.nombre_del_directorio,
                                         self.nombre_de_archivo)
        self.ruta = os.path.join(settings.MEDIA_ROOT,
                                 self.nombre_del_directorio,
                                 self.nombre_de_archivo)

    def crear_archivo_en_directorio(self):
        if self.ya_existe():
            # Esto puede suceder si en un intento previo de depuracion, el
            # proceso es abortado, y por lo tanto, el archivo puede existir.
            logger.warn(_("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                          "reporte para la campana {0}. Archivo: {1}. "
                          "El archivo sera sobreescrito".format(self._campana.pk, self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def _escribir_csv_writer_utf_8(self, csvwriter, datos):
        lista_datos_utf8 = [force_text(item) for item in datos]
        csvwriter.writerow(lista_datos_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)

    def escribir_archivo_datos_csv(self):
        # TODO: Debe listar los llamadas contactados: EVENTOS_FIN_CONEXION
        # Agregarle a los llamadas los datos del (posible) contacto
        # Creamos csvwriter
        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            csvwiter = csv.writer(csvfile)
            for registro in self.datos_reporte:
                self._escribir_csv_writer_utf_8(csvwiter, registro)


class ExportacionCampanaCSV(object):

    def obtener_url_reporte_csv_descargar(self, campana, nombre_reporte):
        archivo_de_reporte = ArchivoDeReporteCsv(campana, nombre_reporte, None)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga
        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga para la campana {0}".format(campana.nombre)))
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def exportar_reportes_csv(self, campana, datos_contactados=None,
                              datos_calificados=None, datos_no_atendidos=None):

        if datos_contactados is not None:
            # Reporte contactados
            archivo_de_reporte = ArchivoDeReporteCsv(
                campana, "contactados", datos_contactados)
            archivo_de_reporte.crear_archivo_en_directorio()
            archivo_de_reporte.escribir_archivo_datos_csv()

        if datos_calificados is not None:
            # Reporte calificados
            archivo_de_reporte = ArchivoDeReporteCsv(
                campana, "calificados", datos_calificados)
            archivo_de_reporte.crear_archivo_en_directorio()
            archivo_de_reporte.escribir_archivo_datos_csv()

        if datos_no_atendidos is not None:
            # Reporte no atendidos
            archivo_de_reporte = ArchivoDeReporteCsv(
                campana, "no_atendidos", datos_no_atendidos)
            archivo_de_reporte.crear_archivo_en_directorio()
            archivo_de_reporte.escribir_archivo_datos_csv()
