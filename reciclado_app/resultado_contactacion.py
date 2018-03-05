# -*- coding: utf-8 -*-

"""
En este modulo se van obtener las estadisticas, de los registros que no fueron
contactados(RS_BUSY, RS_NOANSWER, etc)

contactados(hoy en dia por las calificaciones(calificacioncliente))
"""

from django.db.models import Count


class EstadisticasContactacion():

    def obtener_cantidad_no_contactados(self, campana):
        """
        Obtiene los llamados no contactados por campana
        :param campana: campana a la cual se van obtener los llamados no contactados
        :return: un dicionario con la cantidad por eventos de no contactados
        """

        campana_log_terminated = campana.logswombat.filter(
            estado="TERMINATED", calificacion='CONTESTADOR')
        campana_log_wombat = campana.logswombat.exclude(estado="TERMINATED")
        campana_log_wombat = campana_log_wombat.values(
            'estado', 'calificacion').annotate(Count('estado'))

        count_estados = {}

        for resultado in campana_log_wombat:
            estado = resultado['estado']
            if estado == "RS_LOST" and resultado['calificacion'] == "":
                estado = "Agente no disponible"
            elif estado == "RS_BUSY":
                estado = "Ocupado"
            elif estado == "RS_NOANSWER":
                estado = "No contesta"
            elif estado == "RS_NUMBER":
                estado = "Numero erroneo"
            elif estado == "RS_ERROR":
                estado = "Error de sistema"
            elif estado == "RS_REJECTED":
                estado = "Congestion"
            else:
                estado = None
            # se ignoran los demas estados no antes mappeados
            if estado in count_estados.keys() and estado:
                count_estados[estado] += resultado['estado__count']
            elif estado:
                count_estados.update({estado: resultado['estado__count']})
        if campana_log_terminated.count() > 0:
            count_estados.update({'Contestador Detectado': campana_log_terminated.count()})
        # por cuestion de obtencion de datos se colo agente no califico como no contactado
        count_estados.update(
            {'Agente no califico': campana.logswombat.filter(
                estado='TERMINATED', calificacion='').count()})
        return count_estados

    def obtener_cantidad_calificacion(self, campana):
        """
        Obtiene las cantidad de llamadas por calificacion de la campana
        :param campana: campana la cual se van obtiene las calificaciones
        :return: cantidad por calificacion
        """

        calificaciones_query = campana.calificaconcliente.values(
            'calificacion__nombre', 'calificacion__id').annotate(Count('calificacion')).filter(
            calificacion__count__gt=0)

        calificaciones = []
        for calificacion in calificaciones_query:
            cantidad_contactacion = CantidadContactacion(
                calificacion['calificacion__id'],
                calificacion['calificacion__nombre'],
                calificacion['calificacion__count']
            )
            calificaciones.append(cantidad_contactacion)

        cantidad_contactacion = CantidadContactacion(
            0, campana.gestion, campana.calificaconcliente.filter(es_venta=True).count()
        )
        calificaciones.append(cantidad_contactacion)
        return calificaciones

    def obtener_resultado_contactacion(self, campana):
        """
        obtiene el resultado de los contactados con el contacto y los no contactos
        :param campana: campana de la cual se desea obtener
        :return: un dicionario con las contactaciones
        """
        no_contactados = self.obtener_cantidad_no_contactados(campana)
        contactados = self.obtener_cantidad_calificacion(campana)

        resultados = {}
        resultados.update(no_contactados)
        #resultados.update(contactados)
        return resultados


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

    @property
    def label_checkbox(self):
        return self._nombre + "  " + str(self._cantidad)
