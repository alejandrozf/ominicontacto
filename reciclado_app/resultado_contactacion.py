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

"""
En este modulo se van obtener las estadisticas, de los registros que no fueron
contactados(RS_BUSY, RS_NOANSWER, etc)

contactados(hoy en dia por las calificaciones(calificacioncliente))
"""

from django.utils.translation import gettext as _
from django.db import connection
from django.db.models import Count
from ominicontacto_app.models import Campana, CalificacionCliente
from reportes_app.models import LlamadaLog


class EstadisticasContactacion():

    MAP_ESTADO_ID = {
        'NOANSWER': 0,
        'CANCEL': 1,
        'BUSY': 2,
        'CHANUNAVAIL': 3,
        'OTHER': 4,
        'FAIL': 5,
        'AMD': 6,
        'BLACKLIST': 7,
        'EXITWITHTIMEOUT': 8,
        'ABANDON': 9,
        'CONGESTION': 10,
        'NONDIALPLAN': 11,
    }
    MAP_ID_ESTADO = dict(zip(MAP_ESTADO_ID.values(), MAP_ESTADO_ID.keys()))
    TXT_ESTADO = {
        0: _('No Contesta'),
        1: _('Cancelado'),
        2: _('Ocupado'),
        3: _('Canal no disponible'),
        4: _('Otro'),
        5: _('Falla'),
        6: _('Contestador'),
        7: _('Blacklist'),
        8: _('Expiradas'),
        9: _('Abandono'),
        10: _('Congestion'),
        11: _('Problema de enrutamiento')
    }
    AGENTE_NO_CALIFICO = 20

    def _contabilizar_llamados_no_calificados(self, count_estados, campana, contactados):
        # Calculo cantidad de Llamados Contactados No Calificados
        id_calificados = CalificacionCliente.objects.filter(
            opcion_calificacion__campana_id=campana.id,
            contacto__bd_contacto=campana.bd_contacto).values_list('contacto_id', flat=True)
        no_calificados = contactados.exclude(contacto_id__in=id_calificados).count()
        if no_calificados > 0:
            estado = _(u"Agente no califico")
            id_estado = EstadisticasContactacion.AGENTE_NO_CALIFICO
            cantidad_contactacion = CantidadContactacion(id_estado, estado, no_calificados)
            count_estados.update({id_estado: cantidad_contactacion})

    def _contabilizar_llamados_no_contactados(self, count_estados, campana, contactados,
                                              ids_contactos_base_actual):
        # Cantidades de llamados no contactados por EVENTO FINAL
        # Asumo que Los logs con mayor id son los mas nuevos
        # Solo filtrar logs de contactos de la base actual no contactados
        # Los logs son posteriores a la fecha de alta de la base de datos de contactos
        contactos_ids = set(ids_contactos_base_actual).difference(set(contactados))
        if len(contactos_ids) == 0:
            return
        filtro_contactos = "AND contacto_id in ('"
        filtro_contactos += "','".join([str(x) for x in contactos_ids])
        filtro_contactos += "')"
        if campana.type == Campana.TYPE_DIALER:
            campana_tipo = Campana.TYPE_DIALER
        if campana.type == Campana.TYPE_PREVIEW:
            campana_tipo = Campana.TYPE_PREVIEW

        params = {'campana_id': campana.id,
                  'fecha_alta': campana.bd_contacto.fecha_alta,
                  'tipo_campana': campana_tipo,
                  'filtro_contactos': filtro_contactos, }
        sql = """
        SELECT r1.event, COUNT(r1.event)
            FROM "reportes_app_llamadalog" r1
            INNER JOIN (
                SELECT contacto_id, MAX(id) AS id__max
                FROM "reportes_app_llamadalog"
                WHERE campana_id = {campana_id} AND
                      time >= '{fecha_alta}' AND
                      tipo_llamada = {tipo_campana} AND
                      tipo_campana = {tipo_campana} {filtro_contactos}
                GROUP BY contacto_id
            ) r2
            ON r1.id = r2.id__max
            GROUP BY r1.event
        """.format(**params)

        cursor = connection.cursor()
        cursor.execute(sql)
        values = cursor.fetchall()
        for evento, cantidad in values:
            # Me interesan solo los contactos cuya ultima conexion ha fallado.
            if evento in EstadisticasContactacion.MAP_ESTADO_ID:
                id_estado = EstadisticasContactacion.MAP_ESTADO_ID[evento]
                estado = EstadisticasContactacion.TXT_ESTADO[id_estado]
                cantidad_contactacion = CantidadContactacion(id_estado, estado, cantidad)
                count_estados.update({id_estado: cantidad_contactacion})

    def obtener_cantidad_no_contactados(self, campana):
        """
        Obtiene los llamados no contactados por campana de contactos de la base actual
        :param campana: campana a la cual se van obtener los llamados no contactados
        :return: un dicionario con la cantidad por eventos de no contactados
        """
        # llamados no calificados  Tienen CONNECT pero no tienen Calificacion
        # no llamados     No tienen ni DIAL

        count_estados = {}

        if campana.type == Campana.TYPE_DIALER:
            campana_tipo = Campana.TYPE_DIALER
        if campana.type == Campana.TYPE_PREVIEW:
            campana_tipo = Campana.TYPE_PREVIEW

        ids_contactos_base_actual = campana.bd_contacto.contactos.values_list('id', flat=True)
        contactados = LlamadaLog.objects.filter(campana_id=campana.id,
                                                tipo_campana=campana_tipo,
                                                tipo_llamada=campana_tipo,
                                                contacto_id__in=ids_contactos_base_actual,
                                                event='CONNECT').values_list('contacto_id',
                                                                             flat=True)

        self._contabilizar_llamados_no_calificados(count_estados, campana, contactados)
        self._contabilizar_llamados_no_contactados(
            count_estados, campana, contactados, ids_contactos_base_actual)

        return count_estados

    def obtener_cantidad_calificacion(self, campana):
        """
        Obtiene las cantidad de llamadas por calificacion de la campana de
        contactos de la base actual
        :param campana: campana la cual se van obtiene las calificaciones
        :return: cantidad por calificacion
        """

        calificaciones_query = campana.obtener_calificaciones().filter(
            contacto__bd_contacto=campana.bd_contacto).values(
            'opcion_calificacion__nombre', 'opcion_calificacion__id').annotate(
                Count('opcion_calificacion')).filter(opcion_calificacion__count__gt=0).order_by()

        calificaciones = []
        for calificacion in calificaciones_query:
            cantidad_contactacion = CantidadContactacion(
                calificacion['opcion_calificacion__id'],
                calificacion['opcion_calificacion__nombre'],
                calificacion['opcion_calificacion__count']
            )
            calificaciones.append(cantidad_contactacion)

        return calificaciones


class CantidadContactacion(object):

    def __init__(self, id, nombre, cantidad):
        self._id = id
        self._nombre = nombre
        self._cantidad = cantidad

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, cantidad):
        self._cantidad += cantidad
        return self._cantidad

    @property
    def label_checkbox(self):
        return self._nombre + "  " + str(self._cantidad)


class RecicladorContactosCampanaDIALER():
    """
    Este manager se encarga de obtener los contactos según los tipo de
    reciclado de campana de dialer que se realice.
    Únicamente reciclará contactos de la base de datos de contactos actual
    (si fue reciclada sobre la misma campaña no será la original)
    """

    def obtener_contactos_reciclados(self, campana, reciclado_calificacion,
                                     reciclado_no_contactacion):
        """
        Este método se encarga de iterar sobre los tipos de reciclado que
        se indiquen aplicar en el reciclado de campana. Según el tipo de
        reciclado se invoca al método adecuado para llevar a cabo la consulta
        correspondiente, y en caso de que sea mas de uno se sumarizan las
        mismas.
        """
        contactos_reciclados = set()
        if reciclado_calificacion:
            contactos_reciclados.update(self._obtener_contactos_calificados(
                campana, reciclado_calificacion))
        if reciclado_no_contactacion:
            contactos_reciclados.update(self._obtener_contactos_no_contactados(
                campana, reciclado_no_contactacion))
        return contactos_reciclados

    def _obtener_contactos_no_llamados(self, campana):
        llamadas = LlamadaLog.objects.filter(campana_id=campana.id, contacto_id__isnull=False,
                                             time__gte=campana.bd_contacto.fecha_alta)
        contacto_ids = llamadas.values_list('contacto_id', flat=True).distinct()
        queryset_no_llamados = campana.bd_contacto.contactos.exclude(id__in=contacto_ids)
        contactos_no_llamados = [no_llamado for no_llamado in queryset_no_llamados]
        return contactos_no_llamados

    def _obtener_contactos_calificados(self, campana, reciclado_calificacion):
        """
            Este metodo se encarga obtener los contactos calificados por las
            calificaciones seleccionada
            Sólo contactos que pertenecen a la base de datos de contacto actual.
        """
        calificaciones_query = campana.obtener_calificaciones().filter(
            opcion_calificacion__in=reciclado_calificacion,
            contacto__bd_contacto=campana.bd_contacto).distinct()

        contactos = [calificacion.contacto for calificacion in calificaciones_query]
        return contactos

    def _obtener_contactos_no_contactados(self, campana, reciclado_no_contactacion):
        """
            Este metodo se encarga obtener los contactos no contactados de
             acuerdo a los estados seleccionados

        """
        ids_contactos_base_actual = campana.bd_contacto.contactos.values_list('id', flat=True)
        id_contactos = []
        filtrar_no_calificados = False
        filtro_eventos = ''
        for evento_id in reciclado_no_contactacion:
            evento_id = int(evento_id)
            if evento_id == EstadisticasContactacion.AGENTE_NO_CALIFICO:
                filtrar_no_calificados = True
            else:
                evento = EstadisticasContactacion.MAP_ID_ESTADO[evento_id]
                if filtro_eventos:
                    filtro_eventos += ","
                filtro_eventos += "'%s'" % evento

        if campana.type == Campana.TYPE_DIALER:
            campana_tipo = Campana.TYPE_DIALER
        if campana.type == Campana.TYPE_PREVIEW:
            campana_tipo = Campana.TYPE_PREVIEW

        contactados = LlamadaLog.objects.filter(campana_id=campana.id,
                                                tipo_campana=campana_tipo,
                                                tipo_llamada=campana_tipo,
                                                contacto_id__in=ids_contactos_base_actual,
                                                time__gte=campana.bd_contacto.fecha_alta,
                                                event='CONNECT').values_list('contacto_id',
                                                                             flat=True)

        # Filtrar los contactos Llamados no Calificados
        if filtrar_no_calificados:
            id_calificados = CalificacionCliente.objects.filter(
                opcion_calificacion__campana_id=campana.id,
                contacto__bd_contacto=campana.bd_contacto).values_list('contacto_id', flat=True)
            no_calificados = contactados.exclude(contacto_id__in=id_calificados)
            id_contactos += no_calificados

        # Filtrar los llamados no contactados (solo contactos de la base actual)
        if filtro_eventos:
            contactos_no_contactados = set(ids_contactos_base_actual).difference(set(contactados))
            if len(contactos_no_contactados) < 1:
                return []
            filtro_contactos = "AND contacto_id IN ('"
            filtro_contactos += "','".join([str(x) for x in contactos_no_contactados])
            filtro_contactos += "')"

            params = {'campana_id': campana.id,
                      'fecha_alta': campana.bd_contacto.fecha_alta,
                      'tipo_campana': campana_tipo,
                      'filtro_contactos': filtro_contactos,
                      'filtro_eventos': filtro_eventos}
            sql = """
            SELECT r1.contacto_id
                FROM "reportes_app_llamadalog" r1
                INNER JOIN (
                    SELECT contacto_id, MAX(id) AS id__max
                    FROM "reportes_app_llamadalog"
                    WHERE campana_id = {campana_id} AND
                          time > '{fecha_alta}' AND
                          tipo_llamada = {tipo_campana} AND
                          tipo_campana = {tipo_campana} {filtro_contactos}
                    GROUP BY contacto_id
                ) r2
                ON r1.id = r2.id__max
                WHERE event IN ({filtro_eventos})
            """.format(**params)

            cursor = connection.cursor()
            cursor.execute(sql)
            values = cursor.fetchall()
            id_contactos += [x[0] for x in values]

        return campana.bd_contacto.contactos.filter(id__in=id_contactos)

    def reciclar(self, campana, reciclado_calificacion, reciclado_no_contactacion):

        # Obtener los contactos reciclados
        contactos_reciclados = self.obtener_contactos_reciclados(
            campana, reciclado_calificacion, reciclado_no_contactacion)

        # Si quiero reciclar una campana activa puede existir contactos que no fueron llamados
        if campana.estado == Campana.ESTADO_PAUSADA:
            contactos_no_llamados = self._obtener_contactos_no_llamados(campana)
            contactos_reciclados.update(contactos_no_llamados)

        # Creamos la instancia de BaseDatosContacto para el reciclado.
        bd_contacto_reciclada = campana.bd_contacto.copia_para_reciclar()
        bd_contacto_reciclada.genera_contactos(contactos_reciclados)
        bd_contacto_reciclada.define()
        return bd_contacto_reciclada
