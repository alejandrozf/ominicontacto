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
        :param fecha_desde: fecha desde la cual se obtener los llamados no contactados
        :param fecha_hasta: fehca hasta la cual se va obtener los llamados no contactados
        :return: nombre del evento no contactados, la cantidad por ese evento y el total
        de  llamados no atendidos
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
