# -*- coding: utf-8 -*-

"""
En este modulo se van obtener las estadisticas, de los registros que no fueron
contactados(RS_BUSY, RS_NOANSWER, etc)

contactados(hoy en dia por las calificaciones(calificacioncliente))
"""

from django.db.models import Count


class EstadisticasContactacion():

    AGENTE_NO_DISPONIBLE = 0
    OCUPADO = 1
    NO_CONTESTA = 2
    NUMERO_ERRONEO = 3
    ERROR_DE_SISTEMA = 4
    CONGESTION = 5
    CONTESTADOR = 6
    AGENTE_NO_CALIFICO = 7
    MAP_LOG_WOMBAT = {
        AGENTE_NO_DISPONIBLE: "RS_LOST",
        OCUPADO: "RS_BUSY",
        NO_CONTESTA: "RS_NOANSWER",
        NUMERO_ERRONEO: "RS_NUMBER",
        ERROR_DE_SISTEMA: "RS_ERROR",
        CONGESTION: "RS_REJECTED",
        CONTESTADOR: "CONTESTADOR",
        AGENTE_NO_CALIFICO: AGENTE_NO_CALIFICO,
    }

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
                id_estado = EstadisticasContactacion.AGENTE_NO_DISPONIBLE
            elif estado == "RS_BUSY":
                estado = "Ocupado"
                id_estado = EstadisticasContactacion.OCUPADO
            elif estado == "RS_NOANSWER":
                estado = "No contesta"
                id_estado = EstadisticasContactacion.NO_CONTESTA
            elif estado == "RS_NUMBER":
                estado = "Numero erroneo"
                id_estado = EstadisticasContactacion.NUMERO_ERRONEO
            elif estado == "RS_ERROR":
                estado = "Error de sistema"
                id_estado = EstadisticasContactacion.ERROR_DE_SISTEMA
            elif estado == "RS_REJECTED":
                estado = "Congestion"
                id_estado = EstadisticasContactacion.CONGESTION
            else:
                estado = None
                id_estado = None
            # se ignoran los demas estados no antes mappeados
            if id_estado in count_estados.keys() and id_estado:
                cantidad_contactacion = count_estados[id_estado]
                cantidad_contactacion.cantidad = resultado['estado__count']
                count_estados[id_estado] = cantidad_contactacion
            elif id_estado:
                cantidad_contactacion = CantidadContactacion(
                    id_estado, estado, resultado['estado__count']
                )
                count_estados.update({id_estado: cantidad_contactacion})
        if campana_log_terminated.count() > 0:
            cantidad_contactacion = CantidadContactacion(
                EstadisticasContactacion.CONTESTADOR,
                "Contestador Detectado", campana_log_terminated.count()
            )
            count_estados.update(
                {EstadisticasContactacion.CONTESTADOR: cantidad_contactacion})
        # por cuestion de obtencion de datos se colo agente no califico como no contactado
        cantidad_contactacion = CantidadContactacion(
            EstadisticasContactacion.AGENTE_NO_CALIFICO,
            "Agente no califico", campana.logswombat.filter(
                estado='TERMINATED', calificacion='').count()
        )
        count_estados.update(
            {EstadisticasContactacion.AGENTE_NO_CALIFICO: cantidad_contactacion})
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

        return calificaciones

    def obtener_resultado_contactacion(self, campana):
        """
        obtiene el resultado de los contactados con el contacto y los no contactos
        :param campana: campana de la cual se desea obtener
        :return: un dicionario con las contactaciones
        """
        # FIXME: Borra este metodo o refactorizar, no se usa
        no_contactados = self.obtener_cantidad_no_contactados(campana)
        contactados = self.obtener_cantidad_calificacion(campana)

        resultados = {}
        resultados.update(no_contactados)
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

    def _obtener_contactos_calificados(self, campana, reciclado_calificacion):
        """
            Este metodo se encarga obtener los contactos calificados por las
            calificaciones seleccionada

        """
        calificaciones_query = campana.calificaconcliente.filter(
            calificacion__in=reciclado_calificacion).distinct()

        contactos = [calificacion.contacto for calificacion in calificaciones_query]
        return contactos

    def _obtener_contactos_no_contactados(self, campana, reciclado_no_contactacion):
        """
            Este metodo se encarga obtener los contactos no contactados de
             acuerdo a los estados seleccionados

        """
        reciclado_no_contactacion = map(int, reciclado_no_contactacion)
        no_contactados = set()
        if EstadisticasContactacion.CONTESTADOR in reciclado_no_contactacion:
            reciclado_no_contactacion.remove(EstadisticasContactacion.CONTESTADOR)
            no_contactados.update(campana.logswombat.filter(
                estado="TERMINATED", calificacion='CONTESTADOR'))
        if EstadisticasContactacion.AGENTE_NO_CALIFICO in reciclado_no_contactacion:
            reciclado_no_contactacion.remove(EstadisticasContactacion.AGENTE_NO_CALIFICO)
            no_contactados.update(campana.logswombat.filter(
                estado='TERMINATED', calificacion=''))
        if EstadisticasContactacion.AGENTE_NO_DISPONIBLE in reciclado_no_contactacion:
            reciclado_no_contactacion.remove(EstadisticasContactacion.AGENTE_NO_DISPONIBLE)
            no_contactados.update(campana.logswombat.filter(
                estado=EstadisticasContactacion.AGENTE_NO_DISPONIBLE, calificacion=''))

        estados = [EstadisticasContactacion.MAP_LOG_WOMBAT[estado]
                   for estado in reciclado_no_contactacion]
        no_contactados.update(campana.logswombat.filter(estado__in=estados))
        contactos = [wombat_log.contacto for wombat_log in no_contactados]
        return contactos

    def reciclar(self, campana, reciclado_calificacion, reciclado_no_contactacion):

        # Obtener los contactos reciclados
        contactos_reciclados = self.obtener_contactos_reciclados(
            campana, reciclado_calificacion, reciclado_no_contactacion)

        # Creamos la instancia de BaseDatosContacto para el reciclado.
        bd_contacto_reciclada = campana.bd_contacto.copia_para_reciclar()
        bd_contacto_reciclada.genera_contactos(contactos_reciclados)
        bd_contacto_reciclada.define()
        return bd_contacto_reciclada
