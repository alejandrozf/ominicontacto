# -*- coding: utf-8 -*-

""" Servicio para actualizar estados de llamadas/contactos en wombat """

import requests
from django.conf import settings


class WombatCallService(object):
    def calificar(self, wombat_id, nombre_calificacion):
        url_wombat = '/'.join([settings.OML_WOMBAT_URL,
                               'api/calls/?op=extstatus&wombatid={0}&status={1}'
                               ])
        requests.post(url_wombat.format(wombat_id, nombre_calificacion))

    def asignar_agente(self, wombat_id, id_agente):
        url_wombat_agente = '/'.join([settings.OML_WOMBAT_URL,
                                      'api/calls/?op=attr&wombatid={0}&attr=id_agente&val={1}'])
        requests.post(url_wombat_agente.format(wombat_id, id_agente))
