# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import connection

import logging


logger = logging.getLogger(__name__)


class AgenteTiemposReporte(object):
    """Encapsula los datos de los tiempos de sesion, pausa y llamada del agente.
    """

    def __init__(self, agente, tiempo_sesion, tiempo_pausa, tiempo_llamada):

        self._agente = agente
        self._tiempo_sesion = tiempo_sesion
        self._tiempo_pausa = tiempo_pausa
        self._tiempo_llamada = tiempo_llamada

    @property
    def agente(self):
        return self._agente

    @property
    def tiempo_sesion(self):
        return self._tiempo_sesion

    @property
    def tiempo_pausa(self):
        return self._tiempo_pausa

    @property
    def tiempo_llamada(self):
        return self._tiempo_llamada
