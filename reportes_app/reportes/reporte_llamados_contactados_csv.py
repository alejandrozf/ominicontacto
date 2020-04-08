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
import datetime

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _

from ominicontacto_app.models import AgenteProfile, Campana, Contacto, OpcionCalificacion
from ominicontacto_app.utiles import crear_archivo_en_media_root

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


class ArchivoDeReporteCsv(object):
    def __init__(self, campana, nombre_reporte, agentes_dict, contactos_dict):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-{1}".format(self._campana.id, nombre_reporte)

        self.sufijo_nombre_de_archivo = ".csv"
        self.nombre_de_archivo = "{0}{1}".format(
            self.prefijo_nombre_de_archivo, self.sufijo_nombre_de_archivo)
        self.url_descarga = os.path.join(settings.MEDIA_URL,
                                         self.nombre_del_directorio,
                                         self.nombre_de_archivo)
        self.ruta = os.path.join(settings.MEDIA_ROOT,
                                 self.nombre_del_directorio,
                                 self.nombre_de_archivo)
        self.agentes_dict = agentes_dict
        self.contactos_dict = contactos_dict

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

    def _obtener_datos_contacto(self, contacto_id, campos_contacto):
        telefono_contacto = ''
        contacto = self.contactos_dict.get(contacto_id, -1)
        if contacto != -1:
            telefono_contacto = contacto.telefono
            return json.loads(contacto.datos), telefono_contacto
        return [""] * len(campos_contacto), telefono_contacto

    def _obtener_datos_contacto_contactados(self, llamada_log, calificacion, datos_contacto):
        tel_status = _('Fuera de base')
        bd_contacto = _('Fuera de base')
        telefono_contacto = ''
        contacto = calificacion.contacto if calificacion is not None else None
        if contacto is None:
            contacto = self.contactos_dict.get(llamada_log.contacto_id)
        if contacto is not None:
            telefono_contacto = contacto.telefono
            tel_status = _('Contactado')
            datos_contacto = json.loads(contacto.datos)
            if contacto.es_originario:
                bd_contacto = contacto.bd_contacto
        return tel_status, bd_contacto, datos_contacto, telefono_contacto

    def escribir_archivo_contactados_csv(self, campana, llamadas, calificaciones_dict):
        # TODO: Debe listar los llamadas contactados: EVENTOS_FIN_CONEXION
        # Agregarle a los llamadas los datos del (posible) contacto
        with open(self.ruta, 'w', newline='') as csvfile:
            # Creamos encabezado
            bd_metadata = campana.bd_contacto.get_metadata()
            encabezado = []
            encabezado.append(_("Telefono contactado"))
            campos_contacto = bd_metadata.nombres_de_columnas
            # campos sin telefono
            # TODO: hacer más prolija esta parte, para evitar futuros desfasajes
            campos_contacto_datos = bd_metadata.nombres_de_columnas_de_datos
            encabezado.extend(campos_contacto)
            encabezado.append(_("Fecha-Hora Contacto"))
            encabezado.append(_("Tel status"))
            encabezado.append(_("Calificado"))
            encabezado.append(_("Observaciones"))
            encabezado.append(_("Agente"))
            encabezado.append(_("base de datos"))

            # agrego el encabezado para los campos de los formularios
            if campana.tipo_interaccion is Campana.FORMULARIO:
                campos_formulario_opciones = {}
                posicion_opciones = {}
                cant_campos_gestion = 0
                for opcion in campana.opciones_calificacion.filter(
                        tipo=OpcionCalificacion.GESTION):
                    if opcion.id not in posicion_opciones:
                        posicion_opciones[opcion.id] = cant_campos_gestion
                        campos = opcion.formulario.campos.all()
                        campos_formulario_opciones[opcion.id] = campos
                        encabezado.append(opcion.nombre)
                        cant_campos_gestion += 1
                        for campo in campos:
                            nombre = campo.nombre_campo
                            encabezado.append(nombre)
                            cant_campos_gestion += 1

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)
            # guardamos encabezado
            self._escribir_csv_writer_utf_8(csvwiter, encabezado)

            # Iteramos sobre los llamadas
            for llamada_log in llamadas:
                datos_contacto = [''] * len(campos_contacto_datos)
                calificacion = calificaciones_dict.get(llamada_log.callid, None)
                tel_status, bd_contacto, datos_contacto, telefono_contacto = self.\
                    _obtener_datos_contacto_contactados(llamada_log, calificacion, datos_contacto)
                datos_gestion = []
                if calificacion is None:
                    datos_calificacion = [_("Llamada Atendida sin calificacion"),
                                          '',
                                          self.agentes_dict.get(llamada_log.agente_id, -1)]
                else:
                    datos_calificacion = [calificacion.opcion_calificacion.nombre,
                                          calificacion.observaciones,
                                          calificacion.agente]
                    # TODO: ver la forma de relacionar con respuestas vieja.
                    respuesta_formulario_gestion = calificacion.history_object.get_venta()
                    if hasattr(calificacion, 'es_gestion'):
                        es_gestion = calificacion.es_gestion()
                    else:
                        es_gestion = (calificacion.opcion_calificacion.tipo ==
                                      OpcionCalificacion.GESTION)
                    if (es_gestion and
                        campana.tipo_interaccion is Campana.FORMULARIO and
                            respuesta_formulario_gestion is not None):

                        # Agrego Datos de la respuesta del formulario
                        datos = json.loads(respuesta_formulario_gestion.metadata)
                        id_opcion = respuesta_formulario_gestion.calificacion.opcion_calificacion_id
                        posicion = posicion_opciones[id_opcion]
                        # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
                        posiciones_vacias = posicion - len(datos_gestion)
                        datos_gestion = datos_gestion + [''] * posiciones_vacias
                        # Columna vacia correspondiente al nombre de la Opcion de calificacion
                        datos_gestion.append('')
                        campos = campos_formulario_opciones[id_opcion]
                        for campo in campos:
                            datos_gestion.append(datos[campo.nombre_campo])

                fecha_local_llamada = localtime(llamada_log.time)
                registro = []
                registro.append(llamada_log.numero_marcado)
                registro.append(telefono_contacto)
                registro.extend(datos_contacto)
                registro.append(fecha_local_llamada.strftime("%Y/%m/%d %H:%M:%S"))
                registro.append(tel_status)
                registro.extend(datos_calificacion)
                registro.append(bd_contacto)
                registro.extend(datos_gestion)

                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, registro)

    def escribir_archivo_no_atendidos_csv(self, campana, no_contactados):
        with open(self.ruta, 'w', newline='') as csvfile:
            # Creamos encabezado
            bd_metadata = campana.bd_contacto.get_metadata()
            encabezado = []
            encabezado.append(_("Telefono de llamada"))
            encabezado.append(bd_metadata.nombre_campo_telefono)
            campos_contacto = bd_metadata.nombres_de_columnas_de_datos
            encabezado.extend(campos_contacto)
            encabezado.append(_("Fecha-Hora Contacto"))
            encabezado.append(_("Tel status"))
            encabezado.append(_("Agente"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            self._escribir_csv_writer_utf_8(csvwiter, encabezado)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for log_no_contactado in no_contactados:
                lista_opciones = []
                # --- Buscamos datos
                log_no_contactado_fecha_local = localtime(log_no_contactado.time)
                estado = NO_CONECTADO_DESCRIPCION.get(log_no_contactado.event, "")
                lista_opciones.append(log_no_contactado.numero_marcado)
                contacto_id = log_no_contactado.contacto_id
                datos_contacto, telefono_contacto = self._obtener_datos_contacto(
                    contacto_id, campos_contacto)
                lista_opciones.append(telefono_contacto)
                lista_opciones.extend(datos_contacto)
                lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append(estado)
                tipo_llamada = log_no_contactado.tipo_llamada
                if tipo_llamada == Campana.TYPE_DIALER:
                    agente_info = "DIALER"
                elif tipo_llamada == Campana.TYPE_ENTRANTE:
                    agente_info = "IN"
                else:
                    agente_info = self.agentes_dict.get(log_no_contactado.agente_id, -1)
                lista_opciones.append(agente_info)
                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

    def _obtener_numero_marcado(self, calificacion):
        callid = calificacion.callid
        if not callid:
            return ''
        llamada = LlamadaLog.objects.filter(callid=calificacion.callid).first()

        if llamada is None:
            logger.error('CRITICAL! disposition callid={0} not found in phone logs!'.format(callid))
            return calificacion.contacto.telefono
        return llamada.numero_marcado

    def escribir_archivo_calificado_csv(self, campana, calificaciones):
        with open(self.ruta, 'w', newline='') as csvfile:
            # Creamos encabezado
            bd_metadata = campana.bd_contacto.get_metadata()
            encabezado = []
            encabezado.append(bd_metadata.nombre_campo_telefono)
            campos_contacto = bd_metadata.nombres_de_columnas_de_datos
            encabezado.extend(campos_contacto)
            encabezado.append(_("Fecha-Hora Contacto"))
            encabezado.append(_("Tel status"))
            encabezado.append(_("Tel contactado"))
            encabezado.append(_("Calificado"))
            encabezado.append(_("Observaciones"))
            encabezado.append(_("Agente"))
            encabezado.append(_("base de datos"))

            # agrego el encabezado para los campos de los formularios
            if campana.tipo_interaccion is Campana.FORMULARIO:
                campos_formulario_opciones = {}
                posicion_opciones = {}
                for opcion in campana.opciones_calificacion.filter(
                        tipo=OpcionCalificacion.GESTION):
                    if opcion.id not in posicion_opciones:
                        posicion_opciones[opcion.id] = len(encabezado)
                        campos = opcion.formulario.campos.all()
                        campos_formulario_opciones[opcion.id] = campos
                        encabezado.append(opcion.nombre)
                        for campo in campos:
                            nombre = campo.nombre_campo
                            encabezado.append(nombre)

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            self._escribir_csv_writer_utf_8(csvwiter, encabezado)

            # Asumo calificaciones vienen ordenadas por fecha decreciente. Puede ser con historico.
            callids_ya_iteradas = set()
            # Iteramos cada uno de las metadata de la gestion del formulario
            for calificacion_val in calificaciones:
                lista_opciones = []
                # --- Buscamos datos
                if campana.es_entrante:
                    if calificacion_val.callid in callids_ya_iteradas:
                        continue
                    callids_ya_iteradas.add(calificacion_val.callid)
                    calificacion = calificacion_val.history_object
                    calificacion_fecha_local = localtime(calificacion_val.history_date)
                else:
                    calificacion = calificacion_val
                    calificacion_fecha_local = localtime(calificacion.fecha)
                lista_opciones.append(calificacion.contacto.telefono)
                datos = json.loads(calificacion.contacto.datos)
                lista_opciones.extend(datos)
                lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append(_("Contactado"))

                numero_marcado = self._obtener_numero_marcado(calificacion)
                lista_opciones.append(numero_marcado)
                lista_opciones.append(calificacion.opcion_calificacion.nombre)
                lista_opciones.append(calificacion.observaciones)
                lista_opciones.append(calificacion.agente)
                if calificacion.contacto.es_originario:
                    lista_opciones.append(calificacion.contacto.bd_contacto)
                else:
                    lista_opciones.append(_("Fuera de base"))
                respuesta_formulario_gestion = calificacion.get_venta()
                if (calificacion.es_gestion() and
                    campana.tipo_interaccion is Campana.FORMULARIO and
                        respuesta_formulario_gestion is not None):
                    datos = json.loads(respuesta_formulario_gestion.metadata)

                    # Agrego Datos de la respuesta del formulario
                    datos = json.loads(respuesta_formulario_gestion.metadata)
                    id_opcion = respuesta_formulario_gestion.calificacion.opcion_calificacion_id
                    posicion = posicion_opciones[id_opcion]
                    # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
                    posiciones_vacias = posicion - len(lista_opciones)
                    lista_opciones = lista_opciones + [''] * posiciones_vacias
                    # Columna vacia correspondiente al nombre de la Opcion de calificacion
                    lista_opciones.append('')
                    campos = campos_formulario_opciones[id_opcion]
                    for campo in campos:
                        lista_opciones.append(datos[campo.nombre_campo])

                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaContactadosCSV(object):

    def _obtener_agentes_dict(self, campana):
        # se crean un diccionario de los agentes de la campaña
        # para evitar accesos a la BD para recuperarlos desde los logs
        agentes_dict = {}
        agentes_campana = AgenteProfile.objects.obtener_agentes_campana(campana)
        for agente in agentes_campana:
            agentes_dict[agente.pk] = agente
        return agentes_dict

    def _obtener_contactos_dict(self, campana):
        # se crean un diccionario de los contactos de la campaña
        # para evitar accesos a la BD para recuperarlos desde los logs

        # Si la campaña tuviera referencia a todas las bases de datos que tuvo
        # la busqueda seria mas facil
        logs_campana = LlamadaLog.objects.filter(campana_id=campana.id)
        contactos_ids = logs_campana.values_list('contacto_id', flat=True)
        contactos_campana_en_logs = Contacto.objects.filter(id__in=contactos_ids)
        # Traigo con su base de datos asociada.
        contactos_campana_en_logs = contactos_campana_en_logs.select_related('bd_contacto')

        contactos_dict = {}
        contactos_campana = campana.bd_contacto.contactos.all()
        for contacto in contactos_campana:
            contactos_dict[contacto.pk] = contacto
        # TODO: Analizar si es necesario el loop anterior o si estos datos solo se buscaran para
        # contactos que esten en los logs.
        for contacto in contactos_campana_en_logs:
            contactos_dict[contacto.pk] = contacto
        return contactos_dict

    def _obtener_llamadas_conectadas(self, campana, fecha_desde, fecha_hasta):
        return LlamadaLog.objects.filter(
            event__in=LlamadaLog.EVENTOS_FIN_CONEXION,
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk)

    def crea_reporte_csv(self, campana, fecha_desde, fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)

        agentes_dict = self._obtener_agentes_dict(campana)
        contactos_dict = self._obtener_contactos_dict(campana)

        calificaciones_finales, calificaciones_historicas = self._obtener_calificaciones_fecha(
            campana, fecha_desde, fecha_hasta)
        no_contactados = self._obtener_listado_no_contactados_fecha(
            campana, fecha_desde, fecha_hasta)

        llamadas = self._obtener_llamadas_conectadas(campana, fecha_desde, fecha_hasta)
        calificaciones_historicas_dict = {}
        for calificacion in calificaciones_historicas:
            calificaciones_historicas_dict[calificacion.callid] = calificacion

        # Reporte contactados
        archivo_de_reporte = ArchivoDeReporteCsv(
            campana, "contactados", agentes_dict, contactos_dict)
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_contactados_csv(campana,
                                                            llamadas,
                                                            calificaciones_historicas_dict)
        # Reporte calificados
        archivo_de_reporte = ArchivoDeReporteCsv(
            campana, "calificados", agentes_dict, contactos_dict)
        archivo_de_reporte.crear_archivo_en_directorio()
        if campana.es_entrante:
            archivo_de_reporte.escribir_archivo_calificado_csv(campana, calificaciones_historicas)
        else:
            archivo_de_reporte.escribir_archivo_calificado_csv(campana, calificaciones_finales)
        # Reporte no atendidos
        archivo_de_reporte = ArchivoDeReporteCsv(
            campana, "no_atendidos", agentes_dict, contactos_dict)
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_no_atendidos_csv(
            campana, no_contactados)

    def obtener_url_reporte_csv_descargar(self, campana, nombre_reporte):
        archivo_de_reporte = ArchivoDeReporteCsv(campana, nombre_reporte, None, None)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga
        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga para la campana {0}".format(campana.nombre)))
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def _obtener_calificaciones_fecha(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene todos las calificaciones en el rango de fechas definidas para la campaña
        especificada, tanto las calificaciones históricas como las calificaciones finales
        """
        calificaciones_historicas = campana.obtener_historico_calificaciones().filter(
            history_date__range=(fecha_desde, fecha_hasta))
        calificaciones_finales = campana.obtener_calificaciones().filter(
            fecha__range=(fecha_desde, fecha_hasta))
        return calificaciones_finales, calificaciones_historicas

    def _obtener_listado_no_contactados_fecha(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene los logs de los eventos de los clientes no contactados en el rango de fechas
        definidas para la campaña especificada
        """
        return LlamadaLog.objects.filter(
            event__in=LlamadaLog.EVENTOS_NO_CONEXION,
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk)
