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

from __future__ import unicode_literals

from django.conf import settings
from ominicontacto_app.utiles import elimina_espacios, convert_audio_asterisk_path_astdb
from ominicontacto_app.models import Campana, AgenteProfile, Pausa
from ominicontacto_app.services.asterisk_ami_http import AsteriskHttpClient,\
    AsteriskHttpAsteriskDBError
from configuracion_telefonia_app.models import (
    RutaSaliente, TroncalSIP, IVR, RutaEntrante, DestinoEntrante, ValidacionFechaHora, GrupoHorario
)
import logging as _logging

logger = _logging.getLogger(__name__)


class AbstractFamily(object):
    """class abstract de family de asterisk"""

    def _create_dict(self, family_member):
        raise (NotImplementedError())

    def _create_family(self, family_member):
        """Crea family en database de asterisk
        """

        client = AsteriskHttpClient()
        client.login()
        family = self._get_nombre_family(family_member)
        logger.info("Creando familys para la family  %s", family)
        variables = self._create_dict(family_member)
        for key, val in variables.items():
            try:
                client.asterisk_db("DBPut", family, key, val=val)
            except AsteriskHttpAsteriskDBError:
                logger.exception("Error al intentar DBPut al insertar"
                                 " en la family {0} la siguiente key={1}"
                                 " y val={2}".format(family, key, val))

    def _obtener_todos(self):
        raise (NotImplementedError())

    def _create_families(self, modelo=None, modelos=None):
        """Crea familys en database de asterisk
        """

        if modelos:
            pass
        elif modelo:
            modelos = [modelo]
        else:
            modelos = self._obtener_todos()

        for familia_member in modelos:
            self._create_family(familia_member)

    def _get_nombre_family(self, family_member):
        raise (NotImplementedError())

    def _delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def _obtener_una_key(self):
        """ Método sólo necesario para testear que existe el Family """
        raise (NotImplementedError())

    def delete_family(self, family_member):
        """Elimina una la family de astdb"""
        # primero chequeo si existe la family
        family = self._get_nombre_family(family_member)
        key = self._obtener_una_key()
        existe_family = self._existe_family_key(family, key)
        if existe_family:
            self._delete_tree_family(family)

    def _existe_family_key(self, family, key):
        """Consulta en la base de datos si existe la family y clave"""

        try:
            client = AsteriskHttpClient()
            client.login()
            db_get = client.asterisk_db("DBGet", family, key=key)
        except AsteriskHttpAsteriskDBError:
            return False
        if db_get.response_value == 'success':
            return True

    def get_nombre_families(self):
        raise (NotImplementedError())

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family(self.get_nombre_families())
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_families(modelo=family_member)


class CampanaFamily(AbstractFamily):

    def _create_dict(self, campana):

        dict_campana = {
            'QNAME': "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),
            'TYPE': campana.type,
            'REC': campana.queue_campana.auto_grabacion,
            'AMD': campana.queue_campana.detectar_contestadores,
            'CALLAGENTACTION': campana.tipo_interaccion,
            'RINGTIME': campana.queue_campana.timeout,
            'QUEUETIME': campana.queue_campana.wait,
            'MAXQCALLS': campana.queue_campana.maxlen,
            'SL': campana.queue_campana.servicelevel,
            'TC': "",  # a partir de esta variable no se usan
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
        }

        if campana.queue_campana.audio_para_contestadores:
            dict_campana.update({'AMDPLAY': "{0}{1}".format(
                settings.OML_AUDIO_FOLDER,
                campana.queue_campana.audio_para_contestadores.get_filename_audio_asterisk())})

        if campana.queue_campana.audio_de_ingreso:
            dict_campana.update({'WELCOMEPLAY': "{0}{1}".format(
                settings.OML_AUDIO_FOLDER,
                campana.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())})

        if campana.formulario:
            dict_campana.update({'IDFORM': campana.formulario.pk})
        else:
            dict_campana.update({'IDFORM': ""})

        if campana.sitio_externo:
            dict_campana.update({'IDEXTERNALURL': campana.sitio_externo.pk})
        else:
            dict_campana.update({'IDEXTERNALURL': ""})

        if campana.queue_campana.destino:
            dst = "{0},{1}".format(campana.queue_campana.destino.tipo,
                                   campana.queue_campana.destino.object_id)
            dict_campana.update({'FAILOVER': 1, 'FAILOVERDST': dst})
        else:
            dict_campana.update({'FAILOVER': str(0)})

        return dict_campana

    def _obtener_todos(self):
        """Devuelve las campanas para generar .
        """
        return Campana.objects.obtener_all_dialplan_asterisk()

    def _get_nombre_family(self, campana):
        return "OML/CAMP/{0}".format(campana.id)

    def get_nombre_families(self):
        return "OML/CAMP"

    def _obtener_una_key(self):
        return "QNAME"


class AgenteFamily(AbstractFamily):

    def _create_dict(self, agente):

        dict_agente = {
            'NAME': agente.user.get_full_name(),
            'SIP': agente.sip_extension,
            'STATUS': ""
        }
        return dict_agente

    def _obtener_todos(self):
        """Obtengo todos los agentes activos"""
        return AgenteProfile.objects.obtener_activos()

    def _get_nombre_family(self, agente):
        return "OML/AGENT/{0}".format(agente.id)

    def get_nombre_families(self):
        return "OML/AGENT"

    def _obtener_una_key(self):
        return "NAME"


class PausaFamily(AbstractFamily):

    def _create_dict(self, pausa):

        dict_pausa = {
            'NAME': pausa.nombre,
        }
        return dict_pausa

    def _obtener_todos(self):
        """Obtener todas pausas"""
        return Pausa.objects.activas()

    def _get_nombre_family(self, pausa):
        return "OML/PAUSE/{0}".format(pausa.id)

    def get_nombre_families(self):
        return "OML/PAUSE"

    def _obtener_una_key(self):
        return "NAME"


class RutaSalienteFamily(AbstractFamily):

    def _create_dict(self, ruta):

        dict_ruta = {
            'NAME': ruta.nombre,
            'RINGTIME': ruta.ring_time,
            'OPTIONS': ruta.dial_options,
            'TRUNKS': len(ruta.secuencia_troncales.all())
        }

        patrones = self._obtener_patrones_ordenados(ruta)
        for orden, patron in patrones:
            if patron.prefix:
                prefix = len(str(patron.prefix))
            else:
                prefix = None
            clave_prefix = "PREFIX/{0}".format(orden)
            clave_prepend = "PREPEND/{0}".format(orden)
            dict_ruta.update({clave_prefix: prefix, clave_prepend: patron.prepend})

        troncales = self._obtener_troncales_ordenados(ruta)
        for orden, troncal in troncales:
            dict_ruta.update({"TRUNK/{0}".format(orden): troncal.troncal.nombre})

        return dict_ruta

    def _obtener_todos(self):
        """Obtengo todos las rutas salientes para generar family"""
        return RutaSaliente.objects.all()

    def _obtener_patrones_ordenados(self, ruta):
        """ devuelve patrones ordenados con enumerate"""
        return list(enumerate(ruta.patrones_de_discado.all(), start=1))

    def _obtener_troncales_ordenados(self, ruta):
        """ devuelve troncales ordenados con enumerate"""
        return list(enumerate(ruta.secuencia_troncales.all().order_by("orden"), start=1))

    def _get_nombre_family(self, ruta):
        return "OML/OUTR/{0}".format(ruta.id)

    def get_nombre_families(self):
        return "OML/OUTR"

    def _obtener_una_key(self):
        return "NAME"

    def _regenero_trunks_ruta(self, ruta):
        """
        Regenero las entradas para los trunks en la ruta
            /OML/OUTR/XX/TRUNK/N donde xx es la id de la ruta y N el numero de troncal
        """

        # regenero lo datos de los troncales
        troncales = self._obtener_troncales_ordenados(ruta)
        for orden, troncal in troncales:
            logger.info("Creando familys para troncales %s", troncal.troncal.id)

            try:
                client = AsteriskHttpClient()
                client.login()
                family = self._get_nombre_family(ruta)
                key = "TRUNK/{0}".format(orden)
                val = troncal.troncal.nombre
                client.asterisk_db("DBPut", family, key=key, val=val)
            except AsteriskHttpAsteriskDBError:
                logger.exception("Error al intentar DBPut al insertar"
                                 " en la family {0} la siguiente key={1}"
                                 " y val={2}".format(family, key, val))

    def regenerar_family_trunk_ruta(self, ruta):
        """regeneros lso troncales de la ruta"""
        family = self._get_nombre_family(ruta)
        key = self._obtener_una_key()
        existe_family = self._existe_family_key(family, key)
        if existe_family:
            self._regenero_trunks_ruta(ruta)


class TrunkFamily(AbstractFamily):

    def _create_dict(self, trunk):

        dict_trunk = {
            'NAME': trunk.nombre,
            'CHANNELS': trunk.canales_maximos,
            'CALLERID': trunk.caller_id,
        }

        return dict_trunk

    def _obtener_todos(self):
        """Obtengo todos los troncales sip para generar family"""
        return TroncalSIP.objects.all()

    def _get_nombre_family(self, trunk):
        return "OML/TRUNK/{0}".format(trunk.id)

    def _obtener_una_key(self):
        return "NAME"

    def get_nombre_families(self):
        return "OML/TRUNK"


class RegenerarAsteriskFamilysOML(object):
    """
    Regenera las Families en Asterisk para los objetos que no tienen un Sincronizador como los de
    configuracion_telefonia_app.regeneracion_configuracion_telefonia.AbstractConfiguracionAsterisk
    """

    def __init__(self):
        self.campana_family = CampanaFamily()
        self.agente_family = AgenteFamily()
        self.pausa_family = PausaFamily()
        self.globals_family = GlobalsFamily()

    def regenerar_asterisk(self):
        self.campana_family.regenerar_families()
        self.agente_family.regenerar_families()
        self.pausa_family.regenerar_families()
        self.globals_family.regenerar_families()


class GlobalsFamily(AbstractFamily):

    def _create_dict(self, family_member):

        dict_globals = {
            'DEFAULTQUEUETIME': 90,
            'DEFAULTRINGTIME': 45,
            'LANG': 'es',
            'OBJ/1': 'sub-oml-in-check-set,s,1',
            'OBJ/2': 'sub-oml-module-time-conditions,s,1',
            'OBJ/3': 'sub-oml-module-ivr,s,1',
            'OBJ/4': 'sub-oml-module-ext,s,1',
            'OBJ/5': 'sub-oml-hangup,s,1',
            'OBJ/6': 'sub-oml-module-survey,s,1',
            'RECFILEPATH': '/var/spool/asterisk/monitor',
            'TYPECALL/1': 'manualCall',
            'TYPECALL/2': 'dialerCall',
            'TYPECALL/3': 'inboundCall',
            'TYPECALL/4': 'previewCall',
            'TYPECALL/5': 'icsCall',
            'TYPECALL/7': 'internalCall',
            'TYPECALL/8': 'transferCall',
            'TYPECALL/9': 'transferOutNumCall',
        }

        return dict_globals

    def _get_nombre_family(self, globales):
        return "OML/GLOBALS"

    def get_nombre_families(self):
        return "OML/GLOBALS"

    def _create_families(self):
        """Crea familys en database de asterisk
        """
        self._create_family("")

    def _obtener_una_key(self):
        return "DEFAULTQUEUETIME"


class IVRFamily(AbstractFamily):

    def _create_dict(self, ivr):
        destinos_siguientes = self._obtener_destinos_siguientes(ivr)
        ivr_audio = convert_audio_asterisk_path_astdb(ivr.audio_principal.audio_asterisk)

        timeout_audio = 'NONE'
        if ivr.time_out_audio:
            timeout_audio = convert_audio_asterisk_path_astdb(ivr.time_out_audio.audio_asterisk)

        invalid_audio = 'NONE'
        if ivr.invalid_audio:
            invalid_audio = convert_audio_asterisk_path_astdb(ivr.invalid_audio.audio_asterisk)

        dict_ivr = {
            'NAME': ivr.nombre,
            'AUDIO': ivr_audio,
            'TIMEOUT/SECONDS': ivr.time_out,
            'TIMEOUT/RETRIES': ivr.time_out_retries,
            'TIMEOUT/AUDIO': timeout_audio,
            'INVALID/RETRIES': ivr.invalid_retries,
            'INVALID/AUDIO': invalid_audio,
            'OPTION/OPTIONS': len(destinos_siguientes) - 2
        }

        contador_orden = 0
        for opcion in destinos_siguientes:
            # cambiar por contante de la clase ivr
            dst = "{0},{1}".format(
                opcion.destino_siguiente.tipo, opcion.destino_siguiente.object_id)
            if opcion.valor == IVR.VALOR_TIME_OUT:
                dict_ivr.update({'TIMEOUT/DST': dst})
            elif opcion.valor == IVR.VALOR_DESTINO_INVALIDO:
                dict_ivr.update({'INVALID/DST': dst})
            else:
                contador_orden += 1
                clave_dst = "OPTION/{0}/DST".format(contador_orden)
                clave_dmtf = "OPTION/{0}/DTMF".format(contador_orden)
                dict_ivr.update({clave_dst: dst})
                dict_ivr.update({clave_dmtf: opcion.valor})

        return dict_ivr

    def _obtener_todos(self):
        """Obtengo todos los ivr para generar family"""
        return IVR.objects.all()

    def _obtener_destinos_siguientes(self, ivr):
        return DestinoEntrante.get_nodo_ruta_entrante(ivr).destinos_siguientes.all()

    def _get_nombre_family(self, ivr):
        return "OML/IVR/{0}".format(ivr.id)

    def _obtener_una_key(self):
        return "NAME"

    def get_nombre_families(self):
        return "OML/IVR"


class RutaEntranteFamily(AbstractFamily):

    def _create_dict(self, ruta):

        dst = "{0},{1}".format(ruta.destino.tipo, ruta.destino.object_id)
        dict_ruta = {
            "NAME": ruta.nombre,
            "DST": dst,
            "ID": ruta.id,
            "LANG": ruta.sigla_idioma,
        }
        return dict_ruta

    def _obtener_todos(self):
        """Obtengo todas las rutas entrantes para generar family"""
        return RutaEntrante.objects.all()

    def _get_nombre_family(self, ruta):
        return "OML/INR/{0}".format(ruta.telefono)

    def _obtener_una_key(self):
        return "NAME"

    def get_nombre_families(self):
        return "OML/INR"


class ValidacionFechaHoraFamily(AbstractFamily):

    def _create_dict(self, family_member):
        nodo = DestinoEntrante.get_nodo_ruta_entrante(family_member)
        dict_ivr = {
            'NAME': family_member.nombre,
            'TGID': family_member.grupo_horario.id,
        }

        for opcion in nodo.destinos_siguientes.all():
            dst = "{0},{1}".format(
                opcion.destino_siguiente.tipo, opcion.destino_siguiente.object_id)
            if opcion.valor == ValidacionFechaHora.DESTINO_MATCH:
                dict_ivr.update({'TRUEDST': dst})
            elif opcion.valor == ValidacionFechaHora.DESTINO_NO_MATCH:
                dict_ivr.update({'FALSEDST': dst})

        return dict_ivr

    def _obtener_todos(self):
        """Obtengo todas las ValidacionFechaHora para generar family"""
        return ValidacionFechaHora.objects.all()

    def _get_nombre_family(self, family_member):
        return "OML/TC/{0}".format(family_member.id)

    def _obtener_una_key(self):
        return "NAME"

    def get_nombre_families(self):
        return "OML/TC"


class GrupoHorarioFamily(AbstractFamily):

    def _create_dict(self, grupo):

        validaciones_tiempo = grupo.validaciones_tiempo.all()
        dict_grupo = {
            'NAME': grupo.nombre,
            'ENTRIES': len(validaciones_tiempo)
        }

        contador_orden = 0
        for validacion in validaciones_tiempo:
            contador_orden += 1
            entry = "ENTRY/{0}/".format(contador_orden)
            dict_validacion = {
                entry + 'HOURF': validacion.tiempo_inicial.strftime('%H:%M'),
                entry + 'HOURT': validacion.tiempo_final.strftime('%H:%M'),
                entry + 'DAYF': validacion.dia_semana_inicial_str,
                entry + 'DAYT': validacion.dia_semana_final_str,
                entry + 'DAYNUMF': validacion.dia_mes_inicio_str,
                entry + 'DAYNUMT': validacion.dia_mes_final_str,
                entry + 'MONTHF': validacion.mes_inicio_str,
                entry + 'MONTHT': validacion.mes_final_str,
            }
            dict_grupo.update(dict_validacion)

        return dict_grupo

    def _obtener_todos(self):
        """Obtengo todos los grupos horarios para generar family"""
        return GrupoHorario.objects.all()

    def _get_nombre_family(self, ruta):
        return "OML/TG/{0}".format(ruta.id)

    def _obtener_una_key(self):
        return "NAME"

    def get_nombre_families(self):
        return "OML/TG"
