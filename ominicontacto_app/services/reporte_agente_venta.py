# -*- coding: utf-8 -*-

"""
Servicio de reportes de campanas
"""

from __future__ import unicode_literals

import csv
import logging
import os
import datetime

from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text


logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, agente):
        self._agente = agente
        self.nombre_del_directorio = 'reporte_agente'
        self.prefijo_nombre_de_archivo = "{0}-reporte_agente".format(
            self._agente.id)
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
            logger.warn("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                        "reporte para el agente %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._agente.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, formularios):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Telefono")
            encabezado.append("Id Cliente")
            encabezado.append("Nombre")
            encabezado.append("Apellido")
            encabezado.append("DNI")
            encabezado.append("Fecha Nacimiento")
            encabezado.append("Cuil")
            encabezado.append("datos")
            encabezado.append("Calle")
            encabezado.append("Numero")
            encabezado.append("Depto")
            encabezado.append("Localidad")
            encabezado.append("Codigo postal")
            encabezado.append("Empresa celular")
            encabezado.append("Telefono celular")
            encabezado.append("Telefono fijo")
            encabezado.append("email")
            encabezado.append("Nivel de estudio")
            encabezado.append("Vivienda")
            encabezado.append("Gastos mensuales")
            encabezado.append("Nombre y apellido del padre")
            encabezado.append("Nombre y apellido de la madre")
            encabezado.append("Situacion laboral")
            encabezado.append("Nombre de la empresa")
            encabezado.append("tipo de empresa")
            encabezado.append("Domicilio laboral")
            encabezado.append("Cargo")
            encabezado.append("Fecha de la venta")
            encabezado.append("Vendedor")
            encabezado.append("Domicilio de entrega")
            encabezado.append("Numero")
            encabezado.append("Barrio")
            encabezado.append("Referencia")
            encabezado.append("Localidad")
            encabezado.append("Horario")
            encabezado.append("Dia preferencia")
            encabezado.append("Usuario")
            encabezado.append("Limite")
            encabezado.append("Adicional")

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de los contactos, con los eventos de TODOS los intentos
            for formulario in formularios:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(formulario.contacto.telefono)
                lista_opciones.append(formulario.contacto.id_cliente)
                lista_opciones.append(formulario.contacto.nombre)
                lista_opciones.append(formulario.contacto.apellido)
                lista_opciones.append(formulario.contacto.dni)
                lista_opciones.append(formulario.contacto.fecha_nacimiento)
                lista_opciones.append(formulario.contacto.cuil)
                lista_opciones.append(formulario.contacto.datos)
                lista_opciones.append(formulario.calle)
                lista_opciones.append(formulario.numero)
                lista_opciones.append(formulario.depto)
                lista_opciones.append(formulario.localidad)
                lista_opciones.append(formulario.codigo_postal)
                lista_opciones.append(formulario.empresa_celular)
                lista_opciones.append(formulario.telefono_celular)
                lista_opciones.append(formulario.telefono_fijo)
                lista_opciones.append(formulario.email)
                lista_opciones.append(formulario.get_nivel_estudio_display())
                lista_opciones.append(formulario.get_vivienda_display())
                lista_opciones.append(formulario.gastos_mensuales)
                lista_opciones.append(formulario.nombre_padre)
                lista_opciones.append(formulario.nombre_madre)
                lista_opciones.append(formulario.
                                      get_situacion_laboral_display())
                lista_opciones.append(formulario.nombre_empresa)
                lista_opciones.append(formulario.get_tipo_empresa_display())
                lista_opciones.append(formulario.domicilio_laboral)
                lista_opciones.append(formulario.cargo)
                lista_opciones.append(formulario.fecha)
                lista_opciones.append(formulario.vendedor.user.get_full_name())
                lista_opciones.append(formulario.domicilio)
                lista_opciones.append(formulario.numero_domicilio)
                lista_opciones.append(formulario.barrio)
                lista_opciones.append(formulario.referencia)
                lista_opciones.append(formulario.localidad_entrega)
                lista_opciones.append(formulario.horario)
                lista_opciones.append(formulario.get_dia_preferencia_display())
                lista_opciones.append(formulario.usuario)
                lista_opciones.append(formulario.limite)
                lista_opciones.append(formulario.adicional)

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteFormularioVentaService(object):

    def crea_reporte_csv(self, agente, fecha_desde, fecha_hasta):
        #assert campana.estado == Campana.ESTADO_ACTIVA

        archivo_de_reporte = ArchivoDeReporteCsv(agente)

        archivo_de_reporte.crear_archivo_en_directorio()

        formularios = self._obtener_listado_formularios_fecha(agente,
                                                              fecha_desde,
                                                              fecha_hasta)
        print
        archivo_de_reporte.escribir_archivo_csv(formularios)

    def obtener_url_reporte_csv_descargar(self, agente):
        #assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteCsv(agente)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para el agente %s", agente.pk)

    def _obtener_listado_formularios_fecha(self, agente,fecha_desde,
                                           fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        return agente.formulariosagente.filter(fecha__range=(fecha_desde,
                                                             fecha_hasta))
