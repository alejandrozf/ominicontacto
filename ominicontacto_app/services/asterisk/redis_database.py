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
from django.utils.translation import ugettext as _

from ominicontacto_app.models import AgenteProfile, Pausa, Campana
from ominicontacto_app.utiles import convert_audio_asterisk_path_astdb
from configuracion_telefonia_app.models import (
    RutaSaliente, IVR, DestinoEntrante, ValidacionFechaHora, GrupoHorario, IdentificadorCliente,
    TroncalSIP, RutaEntrante, DestinoPersonalizado
)

import logging as _logging
import redis
from redis.exceptions import RedisError

logger = _logging.getLogger(__name__)


class AbstractRedisFamily(object):
    redis_connection = None

    def get_redis_connection(self):
        if not self.redis_connection:
            self.redis_connection = redis.Redis(
                host=settings.REDIS_HOSTNAME,
                port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                decode_responses=True)
        return self.redis_connection

    def _create_family(self, family_member):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(family_member)
        variables = self._create_dict(family_member)
        try:
            redis_crea_family = redis_connection.hset(family, mapping=variables)
            return redis_crea_family
        except (RedisError) as e:
            raise e

    def _create_families(self, modelo=None, modelos=None):
        """ Crea familys en Redis """
        if modelos:
            pass
        elif modelo:
            modelos = [modelo]
        else:
            modelos = self._obtener_todos()

        for familia_member in modelos:
            self._create_family(familia_member)

    def delete_family(self, family_member):
        redis_connection = self.get_redis_connection()
        try:
            family = self._get_nombre_family(family_member)
            redis_connection.delete(family)
        except (RedisError) as e:
            raise e

    def _delete_tree_family(self):
        """Elimina todos los objetos de la family """

        nombre_families = self.get_nombre_families() + ':*'
        finalizado = False
        index = 0
        while not finalizado:
            redis_connection = self.get_redis_connection()
            try:
                result = redis_connection.scan(index, nombre_families)
                index = result[0]
                keys = result[1]
                for key in keys:
                    redis_connection.delete(key)
                if index == 0:
                    finalizado = True
            except RedisError as e:
                logger.exception(_("Error al intentar Eliminar families de {0}. Error: {1}".format(
                    nombre_families, e)))

    def _create_dict(self, family_member):
        raise (NotImplementedError())

    def _obtener_todos(self):
        raise (NotImplementedError())

    def _get_nombre_family(self, family_member):
        raise (NotImplementedError())

    def get_nombre_families(self):
        raise (NotImplementedError())

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)


class CampanaFamily(AbstractRedisFamily):

    def _create_dict(self, campana):

        dict_campana = {
            'QNAME': "{0}_{1}".format(campana.id, campana.nombre),
            'TYPE': campana.type,
            'REC': str(campana.queue_campana.auto_grabacion),
            'AMD': str(campana.queue_campana.detectar_contestadores),
            'CALLAGENTACTION': campana.tipo_interaccion,
            'RINGTIME': "",
            'QUEUETIME': campana.queue_campana.wait,
            'MAXQCALLS': campana.queue_campana.maxlen,
            'SL': campana.queue_campana.servicelevel,
            'OUTR': "",
            'OUTCID': "",
            'TC': "",  # a partir de esta variable no se usan las siguientes variables:
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
        }

        if campana.queue_campana.timeout:
            ring_time = campana.queue_campana.timeout
            dict_campana.update({'RINGTIME': ring_time})

        if campana.outr_id:
            outr = campana.outr_id
            dict_campana.update({'OUTR': outr})

        if campana.outcid:
            outcid = campana.outcid
            dict_campana.update({'OUTCID': outcid})

        if campana.queue_campana.audio_para_contestadores:
            dict_campana.update({'AMDPLAY': "{0}{1}".format(
                settings.OML_AUDIO_FOLDER,
                campana.queue_campana.audio_para_contestadores.get_filename_audio_asterisk())})

        if campana.queue_campana.audio_de_ingreso:
            dict_campana.update({'WELCOMEPLAY': "{0}{1}".format(
                settings.OML_AUDIO_FOLDER,
                campana.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())})

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

        if campana.queue_campana.ivr_breakdown:
            dict_campana.update(
                {'IVRBREAKOUTID': campana.queue_campana.ivr_breakdown.object_id})

        if campana.queue_campana.musiconhold:
            dict_campana.update({'MOH': campana.queue_campana.musiconhold.nombre})

        return dict_campana

    def _obtener_todos(self):
        """Devuelve las campanas para generar .
        """
        return Campana.objects.obtener_all_dialplan_asterisk()

    def _get_nombre_family(self, campana):
        return "{0}:{1}".format(self.get_nombre_families(), campana.id)

    def get_nombre_families(self):
        return "OML:CAMP"


class AgenteFamily(AbstractRedisFamily):

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
        return "{0}:{1}".format(self.get_nombre_families(), agente.id)

    def get_nombre_families(self):
        return "OML:AGENT"


class RutaSalienteFamily(AbstractRedisFamily):

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
                len_prefix = len(str(patron.prefix))
            else:
                len_prefix = ''
            clave_prefix = "PREFIX-{0}".format(orden)
            clave_prepend = "PREPEND-{0}".format(orden)
            prepend = patron.prepend if patron.prepend is not None else ''
            dict_ruta.update({clave_prefix: len_prefix, clave_prepend: prepend})

        troncales = self._obtener_troncales_ordenados(ruta)
        for orden, troncal in troncales:
            dict_ruta.update({"TRUNK-{0}".format(orden): troncal.troncal.id})

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
        return "{0}:{1}".format(self.get_nombre_families(), ruta.id)

    def get_nombre_families(self):
        return "OML:OUTR"


class IVRFamily(AbstractRedisFamily):

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
            'TIMEOUT': ivr.time_out,
            'TORETRY': ivr.time_out_retries,
            'TOAUDIO': timeout_audio,
            'INVRETRY': ivr.invalid_retries,
            'INVAUDIO': invalid_audio,
            'OPTIONS': len(destinos_siguientes) - 2
        }

        contador_orden = 0
        for opcion in destinos_siguientes:
            # cambiar por contante de la clase ivr
            dst = "{0},{1}".format(
                opcion.destino_siguiente.tipo, opcion.destino_siguiente.object_id)
            if opcion.valor == IVR.VALOR_TIME_OUT:
                dict_ivr.update({'DEFAULTTODST': dst})
            elif opcion.valor == IVR.VALOR_DESTINO_INVALIDO:
                dict_ivr.update({'DEFAULTINVDST': dst})
            else:
                contador_orden += 1
                clave_dst = "OPTIONDST-{0}".format(contador_orden)
                clave_dmtf = "OPTIONDTMF-{0}".format(contador_orden)
                dict_ivr.update({clave_dst: dst})
                dict_ivr.update({clave_dmtf: opcion.valor})

        return dict_ivr

    def _obtener_todos(self):
        """Obtengo todos los ivr para generar family"""
        return IVR.objects.all()

    def _obtener_destinos_siguientes(self, ivr):
        return DestinoEntrante.get_nodo_ruta_entrante(ivr).destinos_siguientes.all()

    def _get_nombre_family(self, ivr):
        return "{0}:{1}".format(self.get_nombre_families(), ivr.id)

    def get_nombre_families(self):
        return "OML:IVR"


class ValidacionFechaHoraFamily(AbstractRedisFamily):

    def _create_dict(self, family_member):
        nodo = DestinoEntrante.get_nodo_ruta_entrante(family_member)
        dict_tc = {
            'NAME': family_member.nombre,
            'TGID': family_member.grupo_horario.id,
        }

        for opcion in nodo.destinos_siguientes.all():
            dst = "{0},{1}".format(
                opcion.destino_siguiente.tipo, opcion.destino_siguiente.object_id)
            if opcion.valor == ValidacionFechaHora.DESTINO_MATCH:
                dict_tc.update({'TRUEDST': dst})
            elif opcion.valor == ValidacionFechaHora.DESTINO_NO_MATCH:
                dict_tc.update({'FALSEDST': dst})

        return dict_tc

    def _obtener_todos(self):
        """Obtengo todas las ValidacionFechaHora para generar family"""
        return ValidacionFechaHora.objects.all()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:TC"


class GrupoHorarioFamily(AbstractRedisFamily):

    def _create_dict(self, grupo):

        validaciones_tiempo = grupo.validaciones_tiempo.all()
        dict_grupo = {
            'NAME': grupo.nombre,
            'ENTRIES': len(validaciones_tiempo)
        }

        contador_orden = 0
        for validacion in validaciones_tiempo:
            contador_orden += 1
            entry = "-{0}".format(contador_orden)
            dict_validacion = {
                'ENTRYHOURF' + entry: validacion.tiempo_inicial.strftime('%H:%M'),
                'ENTRYHOURT' + entry: validacion.tiempo_final.strftime('%H:%M'),
                'ENTRYDAYF' + entry: validacion.dia_semana_inicial_str,
                'ENTRYDAYT' + entry: validacion.dia_semana_final_str,
                'ENTRYDAYNUMF' + entry: validacion.dia_mes_inicio_str,
                'ENTRYDAYNUMT' + entry: validacion.dia_mes_final_str,
                'ENTRYMONTHF' + entry: validacion.mes_inicio_str,
                'ENTRYMONTHT' + entry: validacion.mes_final_str,
            }
            dict_grupo.update(dict_validacion)

        return dict_grupo

    def _obtener_todos(self):
        """Obtengo todos los grupos horarios para generar family"""
        return GrupoHorario.objects.all()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:TG"


class IdentificadorClienteFamily(AbstractRedisFamily):
    def _create_dict(self, family_member):
        nodo = DestinoEntrante.get_nodo_ruta_entrante(family_member)
        externalurl = family_member.url if family_member.url is not None else ''
        longitud_id_esperado = ''
        if family_member.longitud_id_esperado is not None:
            longitud_id_esperado = family_member.longitud_id_esperado
        dict_identificador_cliente = {
            'NAME': family_member.nombre,
            'TYPE': family_member.tipo_interaccion,
            'EXTERNALURL': externalurl,
            'AUDIO': convert_audio_asterisk_path_astdb(family_member.audio.audio_asterisk),
            'LENGTH': longitud_id_esperado,
            'TIMEOUT': family_member.timeout,
            'RETRIES': family_member.intentos,
        }
        for opcion in nodo.destinos_siguientes.all():
            dst = "{0},{1}".format(
                opcion.destino_siguiente.tipo, opcion.destino_siguiente.object_id)
            if opcion.valor == IdentificadorCliente.DESTINO_MATCH:
                dict_identificador_cliente.update({'TRUEDST': dst})
            elif opcion.valor == IdentificadorCliente.DESTINO_NO_MATCH:
                dict_identificador_cliente.update({'FALSEDST': dst})
        return dict_identificador_cliente

    def _obtener_todos(self):
        """Obtengo todas las ValidacionFechaHora para generar family"""
        return IdentificadorCliente.objects.all()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:CUSTOMERID"


class PausaFamily(AbstractRedisFamily):

    def _create_dict(self, pausa):

        dict_pausa = {
            'NAME': pausa.nombre,
        }
        return dict_pausa

    def _obtener_todos(self):
        """Obtener todas pausas"""
        return Pausa.objects.activas()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:PAUSE"


class TrunkFamily(AbstractRedisFamily):

    def _create_dict(self, trunk):

        dict_trunk = {
            'TECH': trunk.tecnologia_astdb,
            'NAME': trunk.nombre,
            'CHANNELS': trunk.canales_maximos,
            'CALLERID': trunk.caller_id if trunk.caller_id is not None else '',
        }

        return dict_trunk

    def _obtener_todos(self):
        """Obtengo todos los troncales sip para generar family"""
        return TroncalSIP.objects.all()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:TRUNK"


class RutaEntranteFamily(AbstractRedisFamily):

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

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.telefono)

    def get_nombre_families(self):
        return "OML:INR"


class DestinoPersonalizadoFamily(AbstractRedisFamily):
    def _create_dict(self, family_member):
        nodo = DestinoEntrante.get_nodo_ruta_entrante(family_member)
        dict_destino_personalizado = {
            'NAME': family_member.nombre,
            'DST': family_member.custom_destination,
        }
        # sólo tendría un destino siguiente (FAILOVER)
        opcion_destino_failover = nodo.destinos_siguientes.first()
        dst = "{0},{1}".format(
            opcion_destino_failover.destino_siguiente.tipo,
            opcion_destino_failover.destino_siguiente.object_id)
        dict_destino_personalizado.update({'FAILOVER': dst})
        return dict_destino_personalizado

    def _obtener_todos(self):
        """Obtengo todas las ValidacionFechaHora para generar family"""
        return DestinoPersonalizado.objects.all()

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member.id)

    def get_nombre_families(self):
        return "OML:CUSTOMDST"


class RegenerarAsteriskFamilysOML(object):
    """
    Regenera las Families en Asterisk para los objetos que no tienen un Sincronizador como los de
    configuracion_telefonia_app.regeneracion_configuracion_telefonia.AbstractConfiguracionAsterisk
    """

    def __init__(self):
        self.campana_family = CampanaFamily()
        self.agente_family = AgenteFamily()
        self.pausa_family = PausaFamily()

    def regenerar_asterisk(self):
        self.campana_family.regenerar_families()
        self.agente_family.regenerar_families()
        self.pausa_family.regenerar_families()
