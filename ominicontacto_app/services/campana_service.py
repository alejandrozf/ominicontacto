# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from django.conf import settings
from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import elimina_coma, elimina_comillas
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import (
    CampanaCreator, TrunkCreator, RescheduleRuleCreator, EndPointCreator,
    CampanaEndPointCreator, CampanaListCreator, CampanaDeleteListCreator
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
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 campana.bd_contacto.nombre])

        nombre_lista = '"' + nombre_lista + '"'
        index = None
        indice = None
        for item in lista:
            nombre = elimina_coma(item)
            if nombre_lista == nombre:
                indice = lista.index(item)
                break

        if indice:
            return elimina_coma(lista[indice-3])
        return None

    def obtener_ccl_id_wombat(self, salida_comando):
        lista = salida_comando.split()

        index = None
        for item in lista:
            if item == '"cclId"':
                index = lista.index(item)
                break

        if index:
            return elimina_coma(lista[index+2])
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

    def crear_reschedule_campana_wombat(self, campana, parametros):
        service_wombat = WombatService()
        service_wombat_config = RescheduleRuleCreator()
        service_wombat_config.create_json(campana, parametros)
        url_edit = "api/edit/campaign/reschedule/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "newcampaign_reschedule.json", url_edit)

    def crear_endpoint_campana_wombat(self, queue):
        service_wombat = WombatService()
        service_wombat_config = EndPointCreator()
        service_wombat_config.create_json(queue)
        url_edit = "api/edit/ep/?mode=E".format(
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
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 campana.bd_contacto.nombre])
        url_edit = "api/lists/?op=addToList&list={0}".format(
            nombre_lista)
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

    def start_campana_wombat(self, campana):
        url_edit = "api/campaigns/?op=start&campaign={0}".format(campana.nombre)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def pausar_campana_wombat(self, campana):
        url_edit = "api/campaigns/?op=pause&campaign={0}".format(campana.nombre)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def despausar_campana_wombat(self, campana):
        url_edit = "api/campaigns/?op=unpause&campaign={0}".format(
            campana.nombre)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def desasociacion_campana_wombat(self, campana):
        service_wombat = WombatService()
        url_edit = "api/edit/campaign/list/?mode=L&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.list_config_wombat(url_edit)
        cclId = self.obtener_ccl_id_wombat(salida)
        cclId = elimina_comillas(cclId)
        if not cclId:
            cclId = 0
        service_wombat_config = CampanaDeleteListCreator()
        service_wombat_config.create_json(cclId)
        url_edit = "api/edit/campaign/list/?mode=D&parent={0}".format(
            campana.campaign_id_wombat)
        salida = service_wombat.update_config_wombat(
            "deletecampaign_list.json", url_edit)

    def remove_campana_wombat(self, campana):
        url_edit = "api/campaigns/?op=remove&campaign={0}".format(campana.nombre)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False
