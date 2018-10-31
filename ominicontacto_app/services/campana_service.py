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

""" Servicio para generar una campana en wombat """

from __future__ import unicode_literals

import requests
import time

from django.utils.translation import ugettext as _

from django.conf import settings
from ominicontacto_app.utiles import elimina_comillas, elimina_espacios
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import (
    CampanaCreator, TrunkCreator, RescheduleRuleCreator, EndPointCreator,
    CampanaEndPointCreator, CampanaListCreator, CampanaDeleteListCreator,
    CampanaEndPointDelete
)
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService
from ominicontacto_app.errors import OmlError


class WombatDialerError(OmlError):
    """Indica que se produjo un error al interactuar con Wombat Dialer."""
    pass


class CampanaService():

    def validar_modificacion_bd_contacto(self, campana, base_datos_modificar):
        """

        :param campana: campana la cual se le va cambiar la base de datos
        :param base_datos_modificar: base de datos a la cual se desea cambiar
        :return: error=None lo cual el nombre de sus columnas coinciden.
        Si es distinto de None lo cual te devuelve el error, no se puede realizar la
        modificacion de la base de datos en esta campana
        """
        error = None
        base_datos_actual = campana.bd_contacto
        if base_datos_actual is None:
            return error

        metadata_actual = base_datos_actual.get_metadata()
        metadata_modificar = base_datos_modificar.get_metadata()

        for columna_base, columna_modificar in zip(
                metadata_actual.nombres_de_columnas,
                metadata_modificar.nombres_de_columnas):
            if columna_base != columna_modificar:
                error = "Los nombres de las columnas no coinciden"

        return error

    def obtener_list_id_wombat(self, salida_comando, campana):
        """
        Retorna el id de la lista para la campana pasada por parametro
        :param salida_comando: listado de listas de wombat
        :param campana: campana la cual deseo encontrar el id de su lista
        :return: id_lista - el id de la lista en wombat
        """
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 elimina_espacios(campana.bd_contacto.nombre)])
        id_lista = None
        results = salida_comando['results']
        for lista in results:
            if lista["name"] == nombre_lista:
                id_lista = lista["listId"]
                break

        return id_lista

    def obtener_datos_campana_json_de_wombat(self, salida, campana):
        """
        Obtiene los datos del json obtenido en wombat formateando los datos que me interesan
        para la campana pasada por parametro
        :param salida: salida del comando de la campanas corriendo en wombat
        :param campana: campana a la cual desea obtener sus datos
        :return: los datos de la campana
        """
        results = salida['result']
        campanas = results['campaigns']
        dato_campana = None
        for campaing in campanas:
            if campaing['campaignId'] == campana.campaign_id_wombat:
                if campana.ESTADO_ACTIVA and campaing['state'] == 'RUNNING':
                    dato_campana = campaing
                    break
                elif campana.ESTADO_PAUSADA and campaing['state'] == 'PAUSED':
                    dato_campana = campaing
                    break
                elif campaing['state'] == 'COMPLETED':
                    dato_campana = campaing
                    break
                elif campaing['state'] == 'WRONG_TIME':
                    dato_campana = campaing
                    break
                elif campaing['state'] == 'IDLE':
                    dato_campana = campaing
                    break
        return dato_campana

    def obtener_datos_calls(self, salida):
        results = salida['result']
        llamadas = results['hopperState']
        return llamadas

    def crear_campana_wombat(self, campana):
        """
        Crear una campana en wombat a travez de curl
        :param campana: campana lo cual se desea una campaign en wombat
        :return: True si se realizo la creacion o False si no se pudo realizar la
        creacion de la campaign
        """
        service_wombat = WombatService()
        # crea json de campaign para crear campaign en wombat
        service_wombat_config = CampanaCreator()
        service_wombat_config.create_json(campana)
        # crear campaing en wombat
        salida = service_wombat.update_config_wombat(
            "newcampaign.json", 'api/edit/campaign/?mode=E')
        results = salida['results']
        # obtengo el campaign_id generado por wombat
        campaign_id = results[0]['campaignId']
        if campaign_id:
            # guardo en la campana el campaign_id generado por wombat
            campana.guardar_campaign_id_wombat(campaign_id)
            return True
        return False

    def crear_trunk_campana_wombat(self, campana):
        """
        Crea trunk para una campaign en wombat via curl
        :param campana: campana a la cual se le creara un trunk en wombat
        """
        service_wombat = WombatService()
        # crea json de trunk para crear trunk en una campana de wombat
        service_wombat_config = TrunkCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/trunk/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # crea trunk en la campana en wombat
        service_wombat.update_config_wombat("newcampaign_trunk.json", url_edit)

    def crear_reschedule_campana_wombat(self, campana, parametros):
        """
        Crear reschedule(reglas de incidencia) para una campaign wn wombat via curl
        :param campana: campana a la cual se le creara reschudule
        :param parametros: parametros de la reschudule en wombat
        """
        service_wombat = WombatService()
        # crea json para reschedule
        service_wombat_config = RescheduleRuleCreator()
        service_wombat_config.create_json(campana, parametros)
        url_edit = "api/edit/campaign/reschedule/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # crea reschedule wn wombat
        service_wombat.update_config_wombat("newcampaign_reschedule.json", url_edit)

    def crear_endpoint_campana_wombat(self, campana):
        """
        Crea endpoint para campaign en wombat via curl
        :param campana: campana para la cual se le creara endpoint
        :return: True si se guardo el ep_id en la queue_campana
        False si no lo guardo
        """
        service_wombat = WombatService()
        # crea json de endpoint para crear endpoint en wombat
        service_wombat_config = EndPointCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/ep/?mode=E".format(
            campana.campaign_id_wombat)
        # crea endpoint en wombat
        salida = service_wombat.update_config_wombat(
            "newep.json", url_edit)
        results = salida['results']
        # obtengo ep_id del endpoint recientemente creado
        ep_id = results[0]['epId']
        if ep_id:
            # guardo el ep_id en la queue_campana
            campana.queue_campana.guardar_ep_id_wombat(ep_id)
            return True
        return False

    def crear_endpoint_asociacion_campana_wombat(self, campana):
        """
        Asociacion endpoint con campaign en wombat
        :param campana: campana a la cual se le desea asociar endpoint
        """
        service_wombat = WombatService()
        # crear json de asociacion campana endpoint
        service_wombat_config = CampanaEndPointCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/ep/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # crea asociacion de enpoint con campaign en wombat
        service_wombat.update_config_wombat("newcampaign_ep.json", url_edit)

    def crear_lista_contactos_wombat(self, campana):
        """
        Crea lista de contactos en wombat, se crear una lista tomando los contactos de la base de
        datos de contactos de la campana
        :param campana: campana de la cual se creara la lista
        """
        service_wombat = WombatService()
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 elimina_espacios(campana.bd_contacto.nombre)])
        url_edit = "api/lists/?op=addToList&list={0}".format(
            nombre_lista)
        # crea lista de contactos en wombat
        service_wombat.update_lista_wombat("newcampaign_list_contacto.txt", url_edit)

    def crear_lista_asociacion_campana_wombat(self, campana):
        """
        crea asociacion de lista de contactos con campaign en wombat via curl
        :param campana: campana a la cual se le asociara la lista
        """
        service_wombat = WombatService()
        url_edit = "api/edit/list/?mode=L"
        # Busco el listado de la lista de contactos de wombat
        salida = service_wombat.list_config_wombat(url_edit)
        # obtiene el list_id para la campana
        list_id = self.obtener_list_id_wombat(salida, campana)
        if not list_id:
            list_id = 1
        # crea json de asociacion campana con el id de lista de contactos
        service_wombat_config = CampanaListCreator()
        service_wombat_config.create_json(list_id)
        url_edit = "api/edit/campaign/list/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # asocia lista de contactos con campaign en wombat
        salida = service_wombat.update_config_wombat(
            "newcampaign_list.json", url_edit)

    def _requests_post_wombat(self, url):
        """Realiza el post a wombat por requests"""
        r = requests.post(url)
        if r.status_code == requests.codes.ok:
            if 'OK' not in r.text:
                raise WombatDialerError(r.text)
        else:
            raise WombatDialerError(r.raise_for_status())

    def start_campana_wombat(self, campana):
        """
        Da inicio a una campana en wombat via post
        Lanza error si no se hizo correctamente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=start&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL, url_edit])
        self._requests_post_wombat(url)

    def pausar_campana_wombat(self, campana):
        """
        Pausa a una campana en wombat via post
        Lanza error si no se hizo correctamente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=pause&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL, url_edit])
        self._requests_post_wombat(url)

    def despausar_campana_wombat(self, campana):
        """
        DesPausa a una campana en wombat via post
        Lanza error si no se hizo correctamente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=unpause&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL, url_edit])
        self._requests_post_wombat(url)

    def desasociacion_campana_wombat(self, campana):
        """
        Desasocia lista campana wombat
        :param campana: campana a la caul se desaciociara la lista
        """
        service_wombat = WombatService()
        url_edit = "api/edit/campaign/list/?mode=L&parent={0}".format(
            campana.campaign_id_wombat)
        # obtiene listado de lista de contactos de wombat
        salida = service_wombat.list_config_wombat(url_edit)
        results = salida['results']
        cclId = results[0]['cclId']
        cclId = elimina_comillas(cclId)
        if not cclId:
            cclId = 0
        # crear json para eliminar lista de contactos de la campana en wombat
        service_wombat_config = CampanaDeleteListCreator()
        service_wombat_config.create_json(cclId)
        url_edit = "api/edit/campaign/list/?mode=D&parent={0}".format(
            campana.campaign_id_wombat)
        # elimina lista de contactos de la campana en wombat
        salida = service_wombat.update_config_wombat(
            "deletecampaign_list.json", url_edit)

    def remove_campana_wombat(self, campana):
        """
        remueve a una campana en wombat via post
        :param campana: campana a la cual desea remover
        :return: True si accion se ejecuto correctamente, False si tuvo algun
        inconveniente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=remove&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL, url_edit])

        try:
            r = requests.post(url)

        except requests.exceptions.RequestException:
            return False

        if r.status_code == 200:
            return True
        return False

    def obtener_dato_campana_run(self, campana):
        """
        obtiene los datos de la campana pasada por parametro
        :param campana: campana a la cual deseo obtener sus datos
        :return: los datos de la campana
        """
        service_wombat = WombatService()
        url_edit = "api/live/runs/"
        salida = service_wombat.list_config_wombat(url_edit)
        if salida:
            return self.obtener_datos_campana_json_de_wombat(salida, campana)
        else:
            return None

    def cambiar_base(self, campana, telefonos, evitar_duplicados, evitar_sin_telefono,
                     prefijo_discador):
        """
        Cambiar base de datos de una campana, lista de contactos en wombat para la campana
        :param campana: campana a la cual desea cambiar la base de datos
        :param telefonos: listado de columnas con telefonos
        :param evitar_duplicados: si se desea evitar duplicados
        :param evitar_sin_telefono: si se desea evitar los contactos sin telefono
        :param prefijo_discador: el prefijo del discador

        Deuda Tecnica mover a otro servico la creacion del archivo con  la lista
        """
        service_base = SincronizarBaseDatosContactosService()
        # crea archivo con lista de contactos para crear lista de contactos en wombat
        service_base.crear_lista(campana, telefonos, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)

        # remueve la campana de las campanas corriendo en wombat
        resultado = self.remove_campana_wombat(campana)
        if resultado:
            campana.remover()
        else:
            pass  # TODO: Verificar si se debe seguir con estos pasos o no!
        time.sleep(30)
        # elimina la lista de contactos de la campana en wombat
        self.desasociacion_campana_wombat(campana)
        # crea la lista de contactos en wombat
        self.crear_lista_contactos_wombat(campana)
        # asocio la lista de contactos a la campana en wombat
        self.crear_lista_asociacion_campana_wombat(campana)

    def obtener_calls_live(self):
        """ retorna las llamada e en vivo en este momento"""
        service_wombat = WombatService()
        url_edit = "api/live/calls/"
        salida = service_wombat.list_config_wombat(url_edit)
        return self.obtener_datos_calls(salida)

    def obtener_status_campana_running(self, hopper_camp_id):
        """ retorona el status de la campana en wombat"""
        service_wombat = WombatService()
        url_edit = "api/reports/stats/?id={0}".format(hopper_camp_id)
        salida = service_wombat.list_config_wombat(url_edit)
        result = salida['result']
        status = self.translate_state_wombat(result['statsOut'])
        return status

    def chequear_campanas_finalizada_eliminarlas(self, campanas):
        """ chequea las campanas pasada por parametros si le quedan llamdas pendientes
        por realizar, si no le quedan las elimino de las campanas corriendo y le cambio
        el estado a eliminadas
        """
        error_msg = _(u"No se pudo consultar el estado actual de la campaña. "
                      "Consulte con su administrador.")
        error = False
        for campana in campanas:
            detalle = self.obtener_dato_campana_run(campana)
            if detalle:
                restantes = int(detalle['n_est_remaining_calls'])
                if restantes == 0 and not campana.es_manual:
                    if self.remove_campana_wombat(campana):
                        campana.finalizar()
                    else:
                        error = error_msg
            else:
                error = error_msg
        return error

    def desasociacion_endpoint_campana_wombat(self, campana):
        """
        Desasocia endpoint de campana wombat
        :param campana: campana a la caul se desaciociara el endpoint
        """
        service_wombat = WombatService()

        # crear json para eliminar lista de la campana en wombat
        service_wombat_config = CampanaEndPointDelete()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/ep/?mode=D&parent={0}".format(
            campana.campaign_id_wombat)
        # elimina lista de la campana en wombat
        service_wombat.update_config_wombat("deletecampaign_ep.json", url_edit)

    def update_endpoint(self, campana):
        """
        Cambiar endpoint cuando se actualiza una queue
        :param campana: campana a la cual desea cambiar el endpoint

        """

        # elimina el end point de la campana en wombat
        self.desasociacion_endpoint_campana_wombat(campana)
        # crea endpoint en wombat
        self.crear_endpoint_campana_wombat(campana)
        # asocio endpoint a la campana en wombat
        self.crear_endpoint_asociacion_campana_wombat(campana)

    def translate_state_wombat(self, status):
        """
        traduce salida de status del wombat
        :param status: dicionarios con todos los counts los estado de la
        llamada
        :return: devuelve status
        """
        for resultado in status:
            estado = resultado['gbState']
            if resultado['gbState'] == "RS_LOST":
                resultado['gbState'] = "Agente no disponible"
            elif estado == "RS_BUSY":
                resultado['gbState'] = "Ocupado"
            elif resultado['gbState'] == "RS_NOANSWER":
                resultado['gbState'] = "No contesta"
            elif resultado['gbState'] == "RS_NUMBER":
                resultado['gbState'] = "Numero erroneo"
            elif resultado['gbState'] == "RS_ERROR":
                resultado['gbState'] = "Error de sistema"
            elif resultado['gbState'] == "RS_REJECTED":
                resultado['gbState'] = "Congestion"
            elif resultado['gbState'] == "TERMINATED":
                resultado['gbState'] = "Finalizada"
        return status
