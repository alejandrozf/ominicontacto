# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import elimina_coma
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import (
    CampanaCreator, TrunkCreator, RescheduleRuleCreator, EndPointCreator,
    CampanaEndPointCreator, CampanaListCreator
)

import logging


class CampanaService():

    def validar_modificacion_bd_contacto(self, campana, base_datos_modificar):
        error = None
        base_datos_actual = campana.bd_contacto
        metadata_actual = base_datos_actual.get_metadata()
        metadata_modidicar = base_datos_modificar.get_metadata()

        for columna_base, columna_modificar in zip(
                metadata_actual.nombres_de_columnas,
                metadata_modidicar.nombres_de_columnas):
            if columna_base != columna_modificar:
                error = "Los nombres de las columnas no coinciden"

        return error

    def obtener_campana_id_wombat(self, salida_comando):
        lista = salida_comando.split()

        index = None
        for item in lista:
            if item == '"campaignId"':
                index = lista.index(item)
                break

        if index:
            return elimina_coma(lista[index+2])
        return None

    def obtener_ep_ip_wombat(self, salida_comando):
        lista = salida_comando.split()

        index = None
        for item in lista:
            if item == '"epId"':
                index = lista.index(item)
                break

        if index:
            return elimina_coma(lista[index+2])
        return None

    def obtener_list_id_wombat(self, salida_comando, campana):
        lista = salida_comando.split()
        nombre_campana = '"' + campana.nombre + '"'
        index = None
        indice = None
        for item in lista:
            if item == '"name"':
                index = lista.index(item)
                nombre = elimina_coma(lista[index + 2])
                if nombre_campana == nombre:
                    indice = lista.index(item)
                    break

        if indice:
            return elimina_coma(lista[index-1])
        return None

    def crear_campana_wombat(self, campana):
        service_wombat = WombatService()
        service_wombat_config = CampanaCreator()
        service_wombat_config.create_json(campana)
        salida = service_wombat.update_config_wombat(
            "newcampaign.json", 'api/edit/campaign/?mode=E')
        campaign_id = self.obtener_campana_id_wombat(salida)
        if campaign_id:
            campana.guardar_campaign_id_wombat(campaign_id)
            return True
        return False

    def crear_trunk_campana_wombat(self, campana):
        service_wombat = WombatService()
        service_wombat_config = TrunkCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/trunk/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newcampaign_trunk.json", url_edit)

    def crear_reschedule_campana_wombat(self, campana):
        service_wombat = WombatService()
        service_wombat_config = RescheduleRuleCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/reschedule/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newcampaign_reschedule.json", url_edit)

    def crear_endpoint_campana_wombat(self, queue):
        service_wombat = WombatService()
        service_wombat_config = EndPointCreator()
        service_wombat_config.create_json(queue)
        url_edit = "api/edit/ep/?mode=E&parent={0}".format(
            queue.campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newep.json", url_edit)
        ep_id = self.obtener_ep_ip_wombat(salida)
        if ep_id:
            queue.guardar_ep_id_wombat(ep_id)
            return True
        return False

    def crear_endpoint_asociacion_campana_wombat(self, queue):
        service_wombat = WombatService()
        service_wombat_config = CampanaEndPointCreator()
        service_wombat_config.create_json(queue)
        url_edit = "api/edit/campaign/ep/?mode=E&parent={0}".format(
            queue.campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newcampaign_ep.json", url_edit)

    def crear_lista_wombat(self, lista, campana):
        service_wombat = WombatService()
        url_edit = "api/lists/?op=addToList&list={0}".format(
            campana.nombre)
        salida = service_wombat.update_lista_wombat(lista, url_edit)

    def crear_lista_asociacion_campana_wombat(self, campana):
        service_wombat = WombatService()
        url_edit = "api/edit/list/?mode=L"
        salida = service_wombat.list_config_wombat(url_edit)
        list_id = self.obtener_list_id_wombat(salida, campana)
        if not list_id:
            list_id = 1
        service_wombat_config = CampanaListCreator()
        service_wombat_config.create_json(list_id)
        url_edit = "api/edit/campaign/list/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newcampaign_list.json", url_edit)
