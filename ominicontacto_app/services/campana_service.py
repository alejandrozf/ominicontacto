# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
import time

from django.conf import settings
from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import elimina_coma, elimina_comillas
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import (
    CampanaCreator, TrunkCreator, RescheduleRuleCreator, EndPointCreator,
    CampanaEndPointCreator, CampanaListCreator, CampanaDeleteListCreator
)
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService

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

    def obtener_list_id_wombat(self, salida_comando, campana):
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 campana.bd_contacto.nombre])
        id_lista = None
        results = salida_comando['results']
        for lista in results:
            if lista["name"] == nombre_lista:
                id_lista = lista["listId"]
                break

        return id_lista

    def crear_campana_wombat(self, campana):
        service_wombat = WombatService()
        service_wombat_config = CampanaCreator()
        service_wombat_config.create_json(campana)
        salida = service_wombat.update_config_wombat(
            "newcampaign.json", 'api/edit/campaign/?mode=E')
        results = salida['results']
        campaign_id = results[0]['campaignId']
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
        results = salida['results']
        ep_id = results[0]['epId']
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
        results = salida['results']
        cclId = results[0]['cclId']
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

    def obtener_dato_campana_run(self, campana):
        service_wombat = WombatService()
        url_edit = "api/live/runs/"
        salida = service_wombat.list_config_wombat(url_edit)
        return salida

    def cambiar_base(self, campana, telefonos, usa_contestador,
                     evitar_duplicados, evitar_sin_telefono, prefijo_discador):
        service_base = SincronizarBaseDatosContactosService()
        lista = service_base.crear_lista(campana, telefonos,
                                         usa_contestador, evitar_duplicados,
                                         evitar_sin_telefono, prefijo_discador)

        resultado = self.remove_campana_wombat(campana)
        if resultado:
            campana.remover()
        time.sleep(30)
        print self.desasociacion_campana_wombat(campana)
        print self.crear_lista_wombat(lista, campana)
        print self.crear_lista_asociacion_campana_wombat(campana)

        resultado_2 = self.start_campana_wombat(campana)
        print resultado_2
        if resultado_2:
            campana.play()
