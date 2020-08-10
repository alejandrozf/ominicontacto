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

from ominicontacto_app.models import Campana
from ominicontacto_app.services.asterisk_ami_http import AsteriskHttpClient,\
    AsteriskHttpAsteriskDBError
from ominicontacto_app.services.asterisk.redis_database import (
    AgenteFamily, PausaFamily)
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
        logger.info(_("Creando familys para la family  {0}".format(family)))
        variables = self._create_dict(family_member)
        for key, val in variables.items():
            try:
                client.asterisk_db("DBPut", family, key, val=val)
            except AsteriskHttpAsteriskDBError:
                logger.exception(_("Error al intentar DBPut al insertar"
                                   " en la family {0} la siguiente key={1}"
                                   " y val={2}".format(family, key, val)))

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

    def _delete_tree_family(self, family, ignorar_error_no_encontrado=False):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError as e:
            if (e.args[0] == 'Database entry not found' and ignorar_error_no_encontrado):
                return
            logger.exception(_("Error al intentar DBDelTree de {0}".format(family)))

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
        self._delete_tree_family(self.get_nombre_families(), True)
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_families(modelo=family_member)


class CampanaFamily(AbstractFamily):

    def _create_dict(self, campana):
        dict_campana = {
            'QNAME': "{0}_{1}".format(campana.id, campana.nombre),
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
            'OUTR': campana.outr_id,
            'OUTCID': campana.outcid,
        }

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
            dict_campana['MOH'] = campana.queue_campana.musiconhold.nombre

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
