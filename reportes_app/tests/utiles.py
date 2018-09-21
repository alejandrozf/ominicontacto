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

from django.utils.timezone import now
from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import LlamadaLogFactory

# LlamadaLog.EVENTOS_NO_CONTACTACION
NOCONNECT = ['NOANSWER', 'CANCEL', 'BUSY', 'CHANUNAVAIL', 'FAIL', 'OTHER', 'AMD', 'BLACKLIST',
             'CONGESTION', 'NONDIALPLAN']
CONNECT = ['COMPLETEAGENT', 'COMPLETECALLER']
# LlamadaLog.EVENTOS_NO_DIALOGO
NO_DIALOG = ['EXITWITHTIMEOUT', 'ABANDON']
FINALIZACIONES = NOCONNECT + CONNECT + NO_DIALOG


class GeneradorDeLlamadaLogs():

    def generar_log(self, campana, es_manual, finalizacion, numero_marcado, agente=None,
                    contacto=None, bridge_wait_time=-1, duracion_llamada=-1, archivo_grabacion='',
                    time=None):
        if time is None:
            time = now()

        tipo_llamada = Campana.TYPE_MANUAL if es_manual else campana.type
        agente_id = -1 if agente is None else agente.id
        contacto_id = -1 if contacto is None else contacto.id

        if es_manual or campana.type in [Campana.TYPE_PREVIEW, Campana.TYPE_MANUAL]:
            assert agente is not None, 'Una llamada manual debe tener un agente'
            assert finalizacion in NOCONNECT or finalizacion in CONNECT, \
                'Finalizacion incorrecta: %s' % finalizacion
            self._generar_logs_dial(campana, tipo_llamada, finalizacion, numero_marcado,
                                    agente_id, contacto_id=contacto_id,
                                    bridge_wait_time=bridge_wait_time,
                                    duracion_llamada=duracion_llamada,
                                    archivo_grabacion=archivo_grabacion,
                                    time=time)

        elif campana.type == Campana.TYPE_DIALER:
            assert finalizacion in FINALIZACIONES, 'Finalizacion incorrecta: %s' % finalizacion
            self._generar_logs_dial(campana, tipo_llamada, finalizacion, numero_marcado,
                                    agente_id=-1, contacto_id=contacto_id,
                                    bridge_wait_time=bridge_wait_time,
                                    duracion_llamada=duracion_llamada,
                                    archivo_grabacion=archivo_grabacion,
                                    time=time)
            if finalizacion not in NOCONNECT:
                self._generar_logs_queue(campana, tipo_llamada, finalizacion, numero_marcado,
                                         agente_id, contacto_id, bridge_wait_time,
                                         duracion_llamada, archivo_grabacion,
                                         time=time)
        elif campana.type == Campana.TYPE_ENTRANTE:
            assert finalizacion in CONNECT or finalizacion in NO_DIALOG
            self._generar_logs_queue(campana, tipo_llamada, finalizacion, numero_marcado,
                                     agente_id, contacto_id, bridge_wait_time,
                                     duracion_llamada, archivo_grabacion, time=time)

    def _generar_logs_dial(self, campana, tipo_llamada, finalizacion, numero_marcado, agente_id,
                           contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion,
                           time):
        """
        Genera logs para la pata de la conexion desde el DIAL
        """
        LlamadaLogFactory(event='DIAL',
                          campana_id=campana.id,
                          tipo_campana=campana.type,
                          tipo_llamada=tipo_llamada,
                          agente_id=agente_id,
                          numero_marcado=numero_marcado,
                          contacto_id=contacto_id,
                          bridge_wait_time=-1,
                          duracion_llamada=-1,
                          archivo_grabacion='',
                          time=time)

        if finalizacion in NOCONNECT:
            LlamadaLogFactory(event=finalizacion,
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=-1,
                              archivo_grabacion='',
                              time=time)
        else:
            LlamadaLogFactory(event='ANSWER',
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=-1,
                              archivo_grabacion='',
                              time=time)
            if tipo_llamada in [Campana.TYPE_MANUAL, Campana.TYPE_PREVIEW]:
                assert finalizacion in CONNECT, \
                    'Una llamada Manual con ANSWER debe terminar en COMPLETEAGENT o COMPLETECALLER'
                LlamadaLogFactory(event=finalizacion,
                                  campana_id=campana.id,
                                  tipo_campana=campana.type,
                                  tipo_llamada=tipo_llamada,
                                  agente_id=agente_id,
                                  numero_marcado=numero_marcado,
                                  contacto_id=contacto_id,
                                  bridge_wait_time=bridge_wait_time,
                                  duracion_llamada=duracion_llamada,
                                  archivo_grabacion=archivo_grabacion,
                                  time=time)
            else:
                # Evento extra de Finalizacion para la pata de dial en el caso DIALER
                assert tipo_llamada == Campana.TYPE_DIALER, \
                    'Sólo Dialers no Manuales pueden tener eventos de la pata DIAL de la conexion'
                if finalizacion in NO_DIALOG:
                    if finalizacion == 'EXITWITHTIMEOUT':
                        finalizacion_pata_dial = 'COMPLETEAGENT'
                    if finalizacion == 'ABANDON':
                        finalizacion_pata_dial = 'COMPLETECALLER'
                    LlamadaLogFactory(event=finalizacion_pata_dial,
                                      campana_id=campana.id,
                                      tipo_campana=campana.type,
                                      tipo_llamada=tipo_llamada,
                                      agente_id=-1,  # 'dialer-dialout'
                                      numero_marcado=numero_marcado,
                                      contacto_id=contacto_id,
                                      bridge_wait_time=bridge_wait_time,
                                      duracion_llamada=duracion_llamada,
                                      archivo_grabacion='',
                                      time=time)
                else:
                    assert finalizacion in CONNECT, \
                        'Finalizacion incorrecta para campaña Dialer:%s' % finalizacion
                    LlamadaLogFactory(event=finalizacion,
                                      campana_id=campana.id,
                                      tipo_campana=campana.type,
                                      tipo_llamada=tipo_llamada,
                                      agente_id=-1,
                                      numero_marcado=numero_marcado,
                                      contacto_id=contacto_id,
                                      bridge_wait_time=bridge_wait_time,
                                      duracion_llamada=duracion_llamada,
                                      archivo_grabacion='',
                                      time=time)

    def _generar_logs_queue(self, campana, tipo_llamada, finalizacion, numero_marcado, agente_id,
                            contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion,
                            time):

        """
        Genera logs para la pata de la conexion desde el ENTERQUEUE
        """
        LlamadaLogFactory(event='ENTERQUEUE',
                          campana_id=campana.id,
                          tipo_campana=campana.type,
                          tipo_llamada=tipo_llamada,
                          agente_id=-1,
                          numero_marcado=numero_marcado,
                          contacto_id=contacto_id,
                          bridge_wait_time=-1,
                          duracion_llamada=-1,
                          archivo_grabacion='',
                          time=time)
        if finalizacion in NO_DIALOG:
            # No se establece el Dialogo con el Agente
            LlamadaLogFactory(event=finalizacion,
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=-1,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=-1,
                              archivo_grabacion='',
                              time=time)
        else:
            # Se establece el Dialogo con el Agente
            assert agente_id is not None and agente_id is not -1, 'Una llamada conectada debe '
            'tener un agente'
            assert finalizacion in CONNECT, 'Finalizacion incorrecta: %s' % finalizacion

            LlamadaLogFactory(event='CONNECT',
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=-1,
                              archivo_grabacion='',
                              time=time)
            LlamadaLogFactory(event=finalizacion,
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=duracion_llamada,
                              archivo_grabacion=archivo_grabacion,
                              time=time)
