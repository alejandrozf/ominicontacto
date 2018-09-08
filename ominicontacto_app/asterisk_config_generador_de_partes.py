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

"""
Genera archivos de configuración para Asterisk: dialplan y queues.
"""

from __future__ import unicode_literals

import pprint

from ominicontacto_app.errors import OmlError
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
        logger.exception("Clase: %s.\nTemplate:\n%s\n Params: %s",
                         str(self.__class__),
                         self.get_template(),
                         pprint.pformat(self.get_parametros()))

    def generar_pedazo(self):
        template = self.get_template()
        template = "\n".join(t.strip() for t in template.splitlines())
        try:
            return template.format(**self.get_parametros())
        except KeyError:
            self._reportar_key_error()
            raise


# ==============================================================================
# Failed
# ==============================================================================


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


class GeneradorParaFailedRutaSaliente(GeneradorDePedazoDeDialplanParaFailed):
    def get_template(self):
        return """

        ;----------------------------------------------------------------------
        ; TEMPLATE_FAILED-{oml_ruta_name}
        ;   Autogenerado {date}
        ;
        ; La generacion de configuracion para la ruta {oml_ruta_name}
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

    def crear_generador_para_queue_entrante(self, parametros):
        return GeneradorParaQueueEntrante(parametros)


# Factory para los Agentes.

class GeneradorDePedazoDeAgenteFactory(object):

    def crear_generador_para_agente(self, parametros):
        return GeneradorParaAgente(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailed(parametros)


# Factory para las Rutas Salientes

class GeneradorDePedazoDeRutasSalientesFactory(object):

    def crear_generador_para_patron_ruta_saliente(self, parametros):
        return GeneradorParaPatronRuta(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailedRutaSaliente(parametros)

# ==============================================================================
# Queue
# ==============================================================================


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
        same => n,Set(CHANNEL(hangup_handler_push)=canal-llamado,s,1)
        same => n,Answer()
        same => n,Playback({filepath_audio_ingreso})
        same => n,Gosub(hangup-fts,llamante_handler,1)
        same => n,SIPAddHeader(Origin:IN)
        same => n,SIPAddHeader(IDCliente:${{IDCliente}})
        same => n,SIPAddHeader(IDCamp:{oml_campana_id})
        {parametros_extra}
        same => n,Set(__TIPOLLAMADA=IN)
        same => n,QueueLog({oml_queue_name},${{UNIQUEID}},NONE,ENTERQUEUE,|${{NUMMARCADO}}||${{TIPOLLAMADA}}|{oml_queue_type})
        same => n,Queue({oml_queue_name},tTc,,,{oml_queue_wait},,,queuelogSub)
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
        same => n,Set(CHANNEL(hangup_handler_push)=canal-llamado,s,1)
        same => n,Answer()
        same => n,Playback({filepath_audio_ingreso})
        same => n,Gosub(hangup-fts,llamante_handler,1)
        same => n,Set(__MONITOR_FILENAME=q-${{EXTEN}}-${{STRFTIME(${{EPOCH}},,%Y%m%d-%H%M%S)}}-${{UNIQUEID}})
        same => n,MixMonitor(${{MONITOR_FILENAME}}.wav,b,/usr/local/parselog/update_mix_mixmonitor.pl ${{UNIQUEID}} ${{MONITOR_FILENAME}}.wav)
        same => n,SIPAddHeader(uidGrabacion:${{UNIQUEID}})
        same => n,SIPAddHeader(Origin:IN)
        same => n,SIPAddHeader(IDCliente:${{IDCliente}})
        same => n,SIPAddHeader(IDCamp:{oml_campana_id})
        {parametros_extra}
        same => n,Set(__TIPOLLAMADA=IN)
        same => n,QueueLog({oml_queue_name},${{UNIQUEID}},NONE,ENTERQUEUE,|${{NUMMARCADO}}||${{TIPOLLAMADA}}|{oml_queue_type})
        same => n,Queue({oml_queue_name},tTc,,,{oml_queue_wait},,,queuelogSub)
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


class GeneradorParaQueueEntrante(GeneradorDePedazoDeQueue):

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
        periodic-announce={oml_periodic-announce}
        periodic-announce-frequency={oml_periodic-announce-frequency}
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

# ==============================================================================
# Agente SIP
# ==============================================================================


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
        context=from-oml
        host=dynamic
        qualify=yes
        notifyringing=yes
        callevents=yes
        callcounter=yes
        callerid={oml_agente_name} <{oml_agente_sip}>
        secret=
        deny=0.0.0.0/0.0.0.0
        permit={oml_kamailio_ip}
        rtcp_mux=yes
        """

    def get_parametros(self):
        return self._parametros


# ==============================================================================
# Rutas Salientes
# ==============================================================================


class GeneradorDePedazoDeRutaSaliente(GeneradorDePedazo):
    """Interfaz / Clase abstracta para generar el pedazo de ruta.
    """

    def __init__(self, parametros):
        self._parametros = parametros


class GeneradorParaPatronRuta(GeneradorDePedazoDeRutaSaliente):

    def get_template(self):
        return """

        exten => {oml-ruta-dialpatern},1,Verbose(2, OUT-R ${{DB(OML/OUTR/{oml-ruta-id}/NAME)}})
        same => n,Set(OMLOUTRID={oml-ruta-id})
        same => n,Gosub(sub-oml-dialout,s,1({oml-ruta-id},{oml-ruta-orden-patern}))
        same => n,Gosub(sub-oml-hangup,s,1(OUTR-FAIL))
        """

    def get_parametros(self):
        return self._parametros
