# -*- coding: utf-8 -*-

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

from ominicontacto_app.models import AgenteProfile, Campana
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
            logger.warn("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                        "reporte para la campana %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._campana.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def _escribir_csv_writer_utf_8(self, csvwriter, datos):
        lista_datos_utf8 = [force_text(item).encode('utf-8')
                            for item in datos]
        csvwriter.writerow(lista_datos_utf8)

    def _obtener_datos_contacto(self, contacto_id, campos_contacto):
        contacto = self.contactos_dict.get(contacto_id, -1)
        if contacto != -1:
            return json.loads(contacto.datos)
        return [""] * len(campos_contacto)

    def escribir_archivo_csv(self, campana, calificados, no_contactados):
        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []
            encabezado.append("Telefono")
            campos_contacto = campana.bd_contacto.get_metadata().nombres_de_columnas[1:]
            encabezado.extend(campos_contacto)
            encabezado.append("Fecha-Hora Contacto")
            encabezado.append("Tel status")
            encabezado.append("Tel contactado")
            encabezado.append("Calificado")
            encabezado.append("Observaciones")
            encabezado.append("Agente")
            encabezado.append("base de datos")
            # agrego el encabezado para los campos del formulario
            if campana.tipo_interaccion is Campana.FORMULARIO:
                campos_formulario = campana.formulario.campos.values_list('nombre_campo', flat=True)
                encabezado.extend(campos_formulario)
            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)
            # guardamos encabezado
            self._escribir_csv_writer_utf_8(csvwiter, encabezado)
            # Iteramos cada uno de las metadata de la gestion del formulario
            for calificacion in calificados:
                lista_opciones = []
                # --- Buscamos datos
                calificacion_fecha_local = localtime(calificacion.fecha)
                lista_opciones.append(calificacion.contacto.telefono)
                datos_contacto = json.loads(calificacion.contacto.datos)
                lista_opciones.extend(datos_contacto)
                lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append("Contactado")
                lista_opciones.append(calificacion.contacto.telefono)
                lista_opciones.append(calificacion.opcion_calificacion.nombre)
                lista_opciones.append(calificacion.observaciones)
                lista_opciones.append(calificacion.agente)
                lista_opciones.append(calificacion.contacto.bd_contacto)
                datos_formulario_gestion = calificacion.get_venta()
                if (calificacion.es_venta and campana.tipo_interaccion is Campana.FORMULARIO and
                        datos_formulario_gestion is not None):
                    datos = json.loads(datos_formulario_gestion.metadata)
                    for campo in campos_formulario:
                        lista_opciones.append(datos[campo])

                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

            for log_no_contactado in no_contactados:
                lista_opciones = []
                # --- Buscamos datos
                estado = NO_CONECTADO_DESCRIPCION.get(log_no_contactado.event, "")
                log_no_contactado_fecha_local = localtime(log_no_contactado.time)
                lista_opciones.append(log_no_contactado.numero_marcado)
                contacto_id = log_no_contactado.contacto_id
                datos_contacto = self._obtener_datos_contacto(contacto_id, campos_contacto)
                lista_opciones.extend(datos_contacto)
                lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append(estado)
                lista_opciones.append("")
                lista_opciones.append("")
                lista_opciones.append("")
                lista_opciones.append(self.agentes_dict.get(log_no_contactado.agente_id, -1))
                lista_opciones.append(campana.bd_contacto)

                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

    def escribir_archivo_no_atendidos_csv(self, campana, no_contactados):
        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []
            encabezado.append("Telefono")
            campos_contacto = campana.bd_contacto.get_metadata().nombres_de_columnas[1:]
            encabezado.extend(campos_contacto)
            encabezado.append("Fecha-Hora Contacto")
            encabezado.append("Tel status")

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
                datos_contacto = self._obtener_datos_contacto(contacto_id, campos_contacto)
                lista_opciones.extend(datos_contacto)
                lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append(estado)
                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

    def escribir_archivo_calificado_csv(self, campana, calificados, no_calificados):
        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []
            encabezado.append("Telefono")
            campos_contacto = campana.bd_contacto.get_metadata().nombres_de_columnas[1:]
            encabezado.extend(campos_contacto)
            encabezado.append("Fecha-Hora Contacto")
            encabezado.append("Tel status")
            encabezado.append("Tel contactado")
            encabezado.append("Calificado")
            encabezado.append("Observaciones")
            encabezado.append("Agente")
            encabezado.append("base de datos")
            # agrego el encabezado para los campos del formulario
            if campana.tipo_interaccion is Campana.FORMULARIO:
                campos_formulario = campana.formulario.campos.values_list('nombre_campo', flat=True)
                encabezado.extend(campos_formulario)

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            self._escribir_csv_writer_utf_8(csvwiter, encabezado)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for calificacion in calificados:
                lista_opciones = []
                # --- Buscamos datos
                calificacion_fecha_local = localtime(calificacion.fecha)
                lista_opciones.append(calificacion.contacto.telefono)
                datos = json.loads(calificacion.contacto.datos)
                lista_opciones.extend(datos)
                lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append("Contactado")
                lista_opciones.append(calificacion.contacto.telefono)
                lista_opciones.append(calificacion.opcion_calificacion.nombre)
                lista_opciones.append(calificacion.observaciones)
                lista_opciones.append(calificacion.agente)
                lista_opciones.append(calificacion.contacto.bd_contacto)
                datos_formulario_gestion = calificacion.get_venta()
                if (calificacion.es_venta and campana.tipo_interaccion is Campana.FORMULARIO and
                        datos_formulario_gestion is not None):
                    datos = json.loads(datos_formulario_gestion.metadata)
                    for campo in campos_formulario:
                        lista_opciones.append(datos[campo])

                # --- Finalmente, escribimos la linea
                self._escribir_csv_writer_utf_8(csvwiter, lista_opciones)

            for log_no_calificado in no_calificados:
                lista_opciones = []
                # --- Buscamos datos
                log_no_contactado_fecha_local = localtime(log_no_calificado.time)
                lista_opciones.append(log_no_calificado.numero_marcado)
                contacto_id = log_no_calificado.contacto_id
                datos_contacto = self._obtener_datos_contacto(contacto_id, campos_contacto)
                lista_opciones.extend(datos_contacto)
                lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append("Contactado")
                lista_opciones.append(log_no_calificado.numero_marcado)
                lista_opciones.append("Llamada Atendida sin calificacion")
                lista_opciones.append("")
                lista_opciones.append(self.agentes_dict.get(log_no_calificado.agente_id, -1))
                lista_opciones.append(campana.bd_contacto)

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
        contactos_dict = {}
        contactos_campana = campana.bd_contacto.contactos.all()
        for contacto in contactos_campana:
            contactos_dict[contacto.pk] = contacto
        return contactos_dict

    def crea_reporte_csv(self, campana, fecha_desde, fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)

        agentes_dict = self._obtener_agentes_dict(campana)
        contactos_dict = self._obtener_contactos_dict(campana)

        calificados = self._obtener_listado_calificados_fecha(
            campana, fecha_desde, fecha_hasta)
        no_contactados = self._obtener_listado_no_contactados_fecha(
            campana, fecha_desde, fecha_hasta)
        no_califico = self._obtener_listado_no_calificados_fecha(
            campana, calificados, fecha_desde, fecha_hasta)
        # Reporte contactados
        archivo_de_reporte = ArchivoDeReporteCsv(
            campana, "contactados", agentes_dict, contactos_dict)
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_csv(campana, calificados, no_contactados)
        # Reporte calificados
        archivo_de_reporte = ArchivoDeReporteCsv(
            campana, "calificados", agentes_dict, contactos_dict)
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_calificado_csv(campana, calificados, no_califico)
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
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la campana %s", campana.nombre)
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def _obtener_listado_calificados_fecha(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene todos las calificaciones en el rango de fechas definidas para la campaña
        especificada
        """
        return campana.obtener_calificaciones().filter(
            fecha__range=(fecha_desde, fecha_hasta))

    def _obtener_listado_no_contactados_fecha(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene los logs de los eventos de los clientes no contactados en el rango de fechas
        definidas para la campaña especificada
        """
        return LlamadaLog.objects.filter(
            event__in=LlamadaLog.EVENTOS_NO_CONEXION,
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk)

    def _obtener_listado_no_calificados_fecha(self, campana, calificados, fecha_desde, fecha_hasta):
        numeros_calificados = calificados.values_list('contacto__telefono', flat=True)
        no_calificados = LlamadaLog.objects.exclude(numero_marcado__in=numeros_calificados).filter(
            event='DIAL', time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk)
        return no_calificados
