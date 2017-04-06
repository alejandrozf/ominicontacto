# -*- coding: utf-8 -*-

"""
Genera archivos de configuración para Asterisk: dialplan y queues.
"""

from __future__ import unicode_literals

import os
import pprint

from django.conf import settings
from ominicontacto_app.errors import OmlError
from ominicontacto_app.models import Queue
import logging as _logging


logger = _logging.getLogger(__name__)


class NoSePuedeCrearDialplanError(OmlError):
    """Indica que no se pudo crear el dialplan."""
    pass


class GeneradorDePedazo(object):
    """Generador de pedazo generico"""

    def get_template(self):
        raise(NotImplementedError())

    def get_parametros(self):
        raise(NotImplementedError())

    def _reportar_key_error(self):
        try:
            logger.exception("Clase: %s.\nTemplate:\n%s\n Params: %s",
                             str(self.__class__),
                             self.get_template(),
                             pprint.pformat(self.get_parametros()))
        except:
            pass

    def generar_pedazo(self):
        template = self.get_template()
        template = "\n".join(t.strip() for t in template.splitlines())
        try:
            return template.format(**self.get_parametros())
        except KeyError:
            self._reportar_key_error()
            raise


#==============================================================================
# Failed
#==============================================================================


class GeneradorDePedazoDeDialplanParaFailed(GeneradorDePedazo):
    """Interfaz / Clase abstracta para generar el pedazo de dialplan
    fallido para una campana.
    """

    def __init__(self, parametros):
        self._parametros = parametros


class GeneradorParaFailed(GeneradorDePedazoDeDialplanParaFailed):

    def get_template(self):
        return """

        ;----------------------------------------------------------------------
        ; TEMPLATE_FAILED-{oml_queue_name}
        ;   Autogenerado {date}
        ;
        ; La generacion de configuracion para la queue {oml_queue_name}
        ;   a fallado.
        ;
        ; {traceback_lines}
        ;
        ;----------------------------------------------------------------------


        """

    def get_parametros(self):
        return self._parametros


# ########################################################################### #
# Factory para las Queue.

class GeneradorDePedazoDeQueueFactory(object):

    def crear_generador_para_queue_sin_grabacion(self, parametros):
        return GeneradorParaQueueSinGrabacion(parametros)

    def crear_generador_para_queue_grabacion(self, parametros):
        return GeneradorParaQueueGrabacion(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailed(parametros)

    def crear_generador_para_queue(self, parametros):
        return GeneradorParaQueue(parametros)


# Factory para los Agentes.

class GeneradorDePedazoDeAgenteFactory(object):

    def crear_generador_para_agente(self, parametros):
        return GeneradorParaAgente(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailed(parametros)


#==============================================================================
# Queue
#==============================================================================


class GeneradorDePedazoDeQueue(GeneradorDePedazo):
    """Interfaz / Clase abstracta para generar el pedazo de queue para una
    cola.
    """

    def __init__(self, parametros):
        self._parametros = parametros


class GeneradorParaQueueSinGrabacion(GeneradorDePedazoDeQueue):

    def get_template(self):
        return """

        ;----------------------------------------------------------------------
        ; TEMPLATE_DIALPLAN_START_QUEUE-{oml_queue_name}
        ;   Autogenerado {date}
        ;----------------------------------------------------------------------

        exten => {oml_queue_id_asterisk},1,NoOp(cola {oml_queue_name})
        same => n,Gosub(hangup-fts,llamante_handler,1)
        same => n,SIPAddHeader(Origin:IN)
        same => n,SIPAddHeader(IDCliente:${{IDCliente}})
        same => n,SIPAddHeader(IDCamp:{oml_campana_id})
        same => n,Set(TIPOLLAMADA=IN)
        same => n,Queue({oml_queue_name},tT,,,{oml_queue_wait})
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaQueueGrabacion(GeneradorDePedazoDeQueue):

    def get_template(self):
        return """

        ;----------------------------------------------------------------------
        ; TEMPLATE_DIALPLAN_START_QUEUE_GRABACION-{oml_queue_name}
        ;   Autogenerado {date}
        ;----------------------------------------------------------------------

        exten => {oml_queue_id_asterisk},1,NoOp(cola {oml_queue_name})
        same => n,Gosub(hangup-fts,llamante_handler,1)
        same => n,Set(__MONITOR_FILENAME=/var/spool/asterisk/monitor/q-${{EXTEN}}-${{STRFTIME(${{EPOCH}},,%Y%m%d-%H%M%S)}}-${{UNIQUEID}})
        same => n,MixMonitor(${{MONITOR_FILENAME}}.wav)
        same => n,SIPAddHeader(Origin:IN)
        same => n,SIPAddHeader(IDCliente:${{IDCliente}})
        same => n,SIPAddHeader(IDCamp:{oml_campana_id})
        same => n,Set(TIPOLLAMADA=IN)
        same => n,Queue({oml_queue_name},tT,,,{oml_queue_wait})
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaQueue(GeneradorDePedazoDeQueue):

    def get_template(self):
        return """

        [{oml_queue_name}]
        announce=beep
        announce-frequency=0
        announce-holdtime=no
        announce-position=no
        autofill=yes
        eventmemberstatus=yes
        eventwhencalled=yes
        joinempty=yes
        leavewhenempty=no
        memberdelay=0
        penaltymemberslimit=0
        periodic-announce-frequency=0
        queue-callswaiting=silence/1
        queue-thereare=silence/1
        queue-youarenext=silence/1
        reportholdtime=no
        ringinuse=no
        timeoutpriority=app
        timeoutrestart=no
        setinterfacevar=yes
        setqueueentryvar=yes
        setqueuevar=yes
        updatecdr=yes
        shared_lastcall=yes
        strategy={oml_strategy}
        timeout={oml_timeout}
        servicelevel={oml_servicelevel}
        weight={oml_weight}
        wrapuptime={oml_wrapuptime}
        maxlen={oml_maxlen}
        retry={oml_retry}
        """

    def get_parametros(self):
        return self._parametros


#==============================================================================
# Agente SIP
#==============================================================================


class GeneradorDePedazoDeAgenteSip(GeneradorDePedazo):
    """Interfaz / Clase abstracta para generar el pedazo de queue para un
    agente.
    """

    def __init__(self, parametros):
        self._parametros = parametros


class GeneradorParaAgente(GeneradorDePedazoDeAgenteSip):

    def get_template(self):
        return """
        [{oml_agente_sip}]
        type=friend
        insecure=invite
        context=from-internal
        host=dynamic
        qualify=yes
        notifyringing=yes
        callevents=yes
        callcounter=yes
        callerid={oml_agente_name} <{oml_agente_sip}>
        secret=
        deny=0.0.0.0/0.0.0.0
        permit={oml_kamailio_ip}
        """

    def get_parametros(self):
        return self._parametros
