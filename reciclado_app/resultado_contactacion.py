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
            if estado in count_estados.keys():
                count_estados[estado] += resultado['estado__count']
            else:
                count_estados.update({estado: resultado['estado__count']})
        if campana_log_terminated.count() > 0:
            count_estados.update({'Contestador Detectado': campana_log_terminated.count()})
        return count_estados

    def obtener_cantidad_calificacion(self, campana):
        """
        Obtiene las cantidad de llamadas por calificacion de la campana
        :param campana: campana la cual se van obtiene las calificaciones
        :return: cantidad por calificacion
        """

        calificaciones_query = campana.calificaconcliente.values(
            'calificacion__nombre').annotate(Count('calificacion')).filter(
            calificacion__count__gt=0)
        count_calificacion = {}
        for calificacion in calificaciones_query:
            count_calificacion.update(
                {calificacion['calificacion__nombre']: calificacion['calificacion__count']})
        return count_calificacion
