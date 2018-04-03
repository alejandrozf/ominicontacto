# -*- coding: utf-8 -*-

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

    def crear_generador_para_agente_global(self, parametros):
        return GeneradorParaAgenteGlobal(parametros)


# Factory para las Pausas

class GeneradorDePedazoDePausaFactory(object):

    def crear_generador_para_pausa_global(self, parametros):
        return GeneradorParaPausaGlobal(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailed(parametros)


# Factory para las Queue.

class GeneradorDePedazoDeCampanaDialerFactory(object):

    def crear_generador_para_campana_dialer_start(self, parametros):
        return GeneradorParaCampanaDialerStart(parametros)

    def crear_generador_para_campana_dialer_contestadores(self, parametros):
        return GeneradorParaCampanaDialerContestadores(parametros)

    def crear_generador_para_campana_dialer_grabacion(self, parametros):
        return GeneradorParaCampanaDialerGrabacion(parametros)

    def crear_generador_para_campana_dialer_formulario(self, parametros):
        return GeneradorParaCampanaDialerFormulario(parametros)

    def crear_generador_para_campana_dialer_sitio_externo(self, parametros):
        return GeneradorParaCampanaDialerSitioExterno(parametros)

    def crear_generador_para_parametro_extra_para_webform(self, parametros):
        return GeneradorParaParametroExtraParaWebform(parametros)

    def crear_generador_para_campana_dialer_contestadores_end(self, parametros):
        return GeneradorParaCampanaDialerContestadoresEnd(parametros)

    def crear_generador_para_campana_dialer_contestadores_end_con_audio(self, parametros):
        return GeneradorParaCampanaDialerContestadoresEndConAudio(parametros)

    def crear_generador_para_failed(self, parametros):
        return GeneradorParaFailed(parametros)

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
        same => n,Set(__MONITOR_FILENAME=/var/spool/asterisk/monitor/q-${{EXTEN}}-${{STRFTIME(${{EPOCH}},,%Y%m%d-%H%M%S)}}-${{UNIQUEID}})
        same => n,MixMonitor(${{MONITOR_FILENAME}}.wav,b,/usr/local/parselog/update_mix_mixmonitor.pl ${{UNIQUEID}}${{MONITOR_FILENAME}}.wav)
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


class GeneradorParaAgenteGlobal(GeneradorDePedazoDeAgenteSip):

    def get_template(self):
        return """
        SIP/{oml_agente_sip} = {oml_agente_pk}
        """

    def get_parametros(self):
        return self._parametros

# ==============================================================================
# Pausa
# ==============================================================================

class GeneradorParaPausaGlobal(GeneradorDePedazo):

    def __init__(self, parametros):
        self._parametros = parametros

    def get_template(self):
        return """
        PAUSA{oml_pausa_pk} = {oml_pausa_nombre}
        """

    def get_parametros(self):
        return self._parametros


# ==============================================================================
# Campana Dialer
# ==============================================================================


class GeneradorParaParametroExtraParaWebform(GeneradorDePedazo):

    def __init__(self, parametros):
        self._parametros = parametros

    def get_template(self):
        return """
        same => n,SIPAddHeader({parametro}:${{{columna}}})
        """

    def get_parametros(self):
        return self._parametros


# ==============================================================================
# Campana Dialer
# ==============================================================================


class GeneradorDePedazoDeCampanaDialer(GeneradorDePedazo):
    """Interfaz / Clase abstracta para generar el pedazo de queue para una
    cola.
    """

    def __init__(self, parametros):
        self._parametros = parametros


class GeneradorParaCampanaDialerStart(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """

        ;----------------------------------------------------------------------
        ; TEMPLATE_DIALPLAN_START_CAMPANA_DIALER-{oml_queue_name}
        ;   Autogenerado {date}
        ;----------------------------------------------------------------------

        exten => {oml_queue_id_asterisk},1,NoOp(cola {oml_queue_name})
        same => n,Gosub(callstatusSub,s,1)
        same => n,Set(CHANNEL(hangup_handler_push)=canal-llamado,s,1)
        same => n,Set(CAMPANA={oml_queue_name})
        same => n,Set(AUX=${{CUT(CHANNEL,@,1)}})
        same => n,Set(NUMMARCADO=${{CUT(AUX,/,2)}})
        same => n,Set(__TIPOLLAMADA=DIALER)
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerContestadores(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n,Background(silence/1)
        same => n,AMD()
        same => n,NoOp(AMDSTATUS=${{AMDSTATUS}})
        same => n,GotoIf($["${{AMDSTATUS}}" == "MACHINE"]?amd_machine)
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerGrabacion(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n,Set(__MONITOR_FILENAME=q-${{STRFTIME(${{EPOCH}},,%Y%m%d%H%M%S)}}-${{ID_CAMPANA}}-${{NUMMARCADO}}-${{UNIQUEID}})
        same => n,Set(__MONITOR_EXEC=/usr/local/parselog/update_mix_mixmonitor.pl ^{{UNIQUEID}} ^{{MIXMONITOR_FILENAME}})
        same => n,MixMonitor(${{MONITOR_FILENAME}}.wav,b,/usr/local/parselog/update_mix_mixmonitor.pl ${{UNIQUEID}}${{MONITOR_FILENAME}}.wav)
        same => n,SIPAddHeader(uidGrabacion:${{UNIQUEID}})
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerFormulario(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n,SIPAddHeader(WombatID:${{WOMBAT_HOPPER_ID}})
        same => n,SIPAddHeader(Origin:DIALER-FORM)
        same => n,SIPAddHeader(IDCliente:${{ID_CLIENTE}})
        same => n,SIPAddHeader(IDCamp:${{ID_CAMPANA}})
        same => n,Set(CALLERID(num)=${{NUMMARCADO}})
        same => n,QueueLog({oml_queue_name},${{UNIQUEID}},NONE,ENTERQUEUE,|${{NUMMARCADO}}||${{TIPOLLAMADA}}|{oml_queue_type})
        same => n,Queue({oml_queue_name},tTc,,,120,,,queuelogSub)
        same => n,Hangup()
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerSitioExterno(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n,SIPAddHeader(WombatID:${{WOMBAT_HOPPER_ID}})
        same => n,SIPAddHeader(Origin:DIALER-SITIOEXTERNO)
        same => n,SIPAddHeader(SITIOEXTERNO: {oml_sitio_externo_url})
        same => n,SIPAddHeader(IDCliente:${{ID_CLIENTE}})
        same => n,SIPAddHeader(IDCamp:${{ID_CAMPANA}})
        same => n,Set(CALLERID(num)=${{NUMMARCADO}})
        same => n,QueueLog({oml_queue_name},${{UNIQUEID}},NONE,ENTERQUEUE,|${{NUMMARCADO}}||${{TIPOLLAMADA}}|{oml_queue_type})
        same => n,Queue({oml_queue_name},tTc,,,120,,,queuelogSub)
        same => n,Hangup()
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerContestadoresEnd(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n(amd_machine),NoOp(es una maquina)
        same => n,UserEvent(CALLSTATUS,Uniqueid:${{UNIQUEID}},V:CONTESTADOR)
        same => n,SET(CDR(userfield)=CONTESTADOR)
        same => n,Hangup()
        """

    def get_parametros(self):
        return self._parametros


class GeneradorParaCampanaDialerContestadoresEndConAudio(GeneradorDePedazoDeCampanaDialer):

    def get_template(self):
        return """
        same => n(amd_machine),NoOp(es una maquina)
        same => n,UserEvent(CALLSTATUS,Uniqueid:${{UNIQUEID}},V:CONTESTADOR)
        same => n,SET(CDR(userfield)=CONTESTADOR)
        same => n,Playback(oml/{filename_audio_contestadores})
        same => n,Playback(oml/{filename_audio_contestadores})
        same => n,Hangup()
        """

    def get_parametros(self):
        return self._parametros
