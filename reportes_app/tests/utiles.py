# -*- coding: utf-8 -*-

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import LlamadaLogFactory


NOCONNECT = ['NOANSWER', 'CANCEL', 'BUSY', 'CHANUNAVAIL', 'FAIL', 'OTHER', 'AMD', 'BLACKLIST']
CONNECT = ['COMPLETEAGENT', 'COMPLETECALLER']
NO_DIALOG = ['EXITWITHTIMEOUT', 'ABANDON']
FINALIZACIONES = NOCONNECT + CONNECT + NO_DIALOG


class GeneradorDeLlamadaLogs():

    def generar_log(self, campana, es_manual, finalizacion, numero_marcado, agente=None,
                    contacto=None, bridge_wait_time=-1, duracion_llamada=-1, archivo_grabacion=''):

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
                                    archivo_grabacion=archivo_grabacion)

        elif campana.type == Campana.TYPE_DIALER:
            assert finalizacion in FINALIZACIONES, 'Finalizacion incorrecta: %s' % finalizacion
            self._generar_logs_dial(campana, tipo_llamada, finalizacion, numero_marcado,
                                    agente_id=-1, contacto_id=contacto_id,
                                    bridge_wait_time=bridge_wait_time,
                                    duracion_llamada=duracion_llamada,
                                    archivo_grabacion=archivo_grabacion)
            if finalizacion not in NOCONNECT:
                self._generar_logs_queue(campana, tipo_llamada, finalizacion, numero_marcado,
                                         agente_id, contacto_id, bridge_wait_time,
                                         duracion_llamada, archivo_grabacion)
        elif campana.type == Campana.TYPE_ENTRANTE:
            assert finalizacion in CONNECT or finalizacion in NO_DIALOG
            self._generar_logs_queue(campana, tipo_llamada, finalizacion, numero_marcado,
                                     agente_id, contacto_id, bridge_wait_time,
                                     duracion_llamada, archivo_grabacion)

    def _generar_logs_dial(self, campana, tipo_llamada, finalizacion, numero_marcado, agente_id,
                           contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion):
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
                          archivo_grabacion='')

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
                              archivo_grabacion='')
        else:
            LlamadaLogFactory(event='ANSWER',
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=duracion_llamada,
                              archivo_grabacion='')
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
                                  archivo_grabacion=archivo_grabacion)
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
                                      archivo_grabacion='')
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
                                      archivo_grabacion='')

    def _generar_logs_queue(self, campana, tipo_llamada, finalizacion, numero_marcado, agente_id,
                            contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion):

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
                          archivo_grabacion='')
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
                              archivo_grabacion='')
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
                              archivo_grabacion='')
            LlamadaLogFactory(event=finalizacion,
                              campana_id=campana.id,
                              tipo_campana=campana.type,
                              tipo_llamada=tipo_llamada,
                              agente_id=agente_id,
                              numero_marcado=numero_marcado,
                              contacto_id=contacto_id,
                              bridge_wait_time=bridge_wait_time,
                              duracion_llamada=duracion_llamada,
                              archivo_grabacion=archivo_grabacion)
