# -*- coding: utf-8 -*-

""" Servicio para generar una campana en wombat """

from __future__ import unicode_literals

import requests
import time

from django.conf import settings
from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import elimina_coma, elimina_comillas, elimina_espacios
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import (
    CampanaCreator, TrunkCreator, RescheduleRuleCreator, EndPointCreator,
    CampanaEndPointCreator, CampanaListCreator, CampanaDeleteListCreator,
    CampanaEndPointDelete
)
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService

import logging


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

    def obtener_datos_campana_run(self, salida, campana):
        """
        Retorno los datos de la campana activa pasado por parametro
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
        # crea json de trunk para crear trunk en wombat
        service_wombat_config = TrunkCreator()
        service_wombat_config.create_json(campana)
        url_edit = "api/edit/campaign/trunk/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # crea trunk en wombat
        salida = service_wombat.update_config_wombat(
            "newcampaign_trunk.json", url_edit)

    def crear_reschedule_campana_wombat(self, campana, parametros):
        """
        Crear reschedule para una campaign wn wombat via curl
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
        salida = service_wombat.update_config_wombat(
            "newcampaign_reschedule.json", url_edit)

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
        salida = service_wombat.update_config_wombat(
            "newcampaign_ep.json", url_edit)

    def crear_lista_wombat(self, campana):
        """
        Crea lista en wombat via curl
        :param campana: campana de la cual se creara la lista
        """
        service_wombat = WombatService()
        nombre_lista = '_'.join([str(campana.id), str(campana.bd_contacto.id),
                                 elimina_espacios(campana.bd_contacto.nombre)])
        url_edit = "api/lists/?op=addToList&list={0}".format(
            nombre_lista)
        # crea lista en wombat
        salida = service_wombat.update_lista_wombat("newcampaign_list_contacto.txt",
                                                    url_edit)

    def crear_lista_asociacion_campana_wombat(self, campana):
        """
        crea asociacion de lista con campaign en wombat via curl
        :param campana: campana a la cual se le asociara la lista
        """
        service_wombat = WombatService()
        url_edit = "api/edit/list/?mode=L"
        # Busco el listado de la lista de wombat
        salida = service_wombat.list_config_wombat(url_edit)
        # obtiene el list_id para la campana
        list_id = self.obtener_list_id_wombat(salida, campana)
        if not list_id:
            list_id = 1
        # crea json de asociacion campana con lista
        service_wombat_config = CampanaListCreator()
        service_wombat_config.create_json(list_id)
        url_edit = "api/edit/campaign/list/?mode=E&parent={0}".format(
            campana.campaign_id_wombat)
        # asocia lista con campaign en wombat
        salida = service_wombat.update_config_wombat(
            "newcampaign_list.json", url_edit)

    def start_campana_wombat(self, campana):
        """
        Da inicio a una campana en wombat via post
        :param campana: campana a la cual desea dar start
        :return: True si accion se ejecuto correctamente, False si tuvo algun
        inconveniente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=start&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def pausar_campana_wombat(self, campana):
        """
        Pausa a una campana en wombat via post
        :param campana: campana a la cual desea pausar
        :return: True si accion se ejecuto correctamente, False si tuvo algun
        inconveniente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=pause&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def despausar_campana_wombat(self, campana):
        """
        DesPausa a una campana en wombat via post
        :param campana: campana a la cual desea despausar
        :return: True si accion se ejecuto correctamente, False si tuvo algun
        inconveniente
        """
        nombre_campana = "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre))
        url_edit = "api/campaigns/?op=unpause&campaign={0}".format(nombre_campana)
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)
        if r.status_code == 200:
            return True
        return False

    def desasociacion_campana_wombat(self, campana):
        """
        Desasocia lista campana wombat
        :param campana: campana a la caul se desaciociara la lista
        """
        service_wombat = WombatService()
        url_edit = "api/edit/campaign/list/?mode=L&parent={0}".format(
            campana.campaign_id_wombat)
        # obtiene listado de lista de wombat
        salida = service_wombat.list_config_wombat(url_edit)
        results = salida['results']
        cclId = results[0]['cclId']
        cclId = elimina_comillas(cclId)
        if not cclId:
            cclId = 0
        # crear json para eliminar lista de la campana en wombat
        service_wombat_config = CampanaDeleteListCreator()
        service_wombat_config.create_json(cclId)
        url_edit = "api/edit/campaign/list/?mode=D&parent={0}".format(
            campana.campaign_id_wombat)
        # elimina lista de la campana en wombat
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
        url = '/'.join([settings.OML_WOMBAT_URL,
                  url_edit])
        r = requests.post(url)

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
        return self.obtener_datos_campana_run(salida, campana)

    def cambiar_base(self, campana, telefonos, evitar_duplicados, evitar_sin_telefono,
                     prefijo_discador):
        """
        Cambiar base de datos de una campana, list en wombat para la campana
        :param campana: campana a la cual desea cambiar la base de datos
        :param telefonos: listado de columnas con telefonos
        :param evitar_duplicados: si se desea evitar duplicados
        :param evitar_sin_telefono: si se desea evitar los contactos sin telefono
        :param prefijo_discador: el prefijo del discador

        Deuda Tecnica mover a otro servico la creacion del archivo con  la lista
        """
        service_base = SincronizarBaseDatosContactosService()
        # crea archivo con lista para crear lista en wombat
        service_base.crear_lista(campana, telefonos, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)

        # remueve la campana de las campanas corriendo en wombat
        resultado = self.remove_campana_wombat(campana)
        if resultado:
            campana.remover()
        time.sleep(30)
        # elimina la lista de la campana en wombat
        print self.desasociacion_campana_wombat(campana)
        # crea la lista en wombat
        print self.crear_lista_wombat(campana)
        # asocio la lista a la campana en wombat
        print self.crear_lista_asociacion_campana_wombat(campana)
        # doy inicio a la campana en wombat
        resultado_2 = self.start_campana_wombat(campana)
        print resultado_2
        # cambio el estado de la campana activa
        if resultado_2:
            campana.play()

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
        for campana in campanas:
            detalle = self.obtener_dato_campana_run(campana)
            if detalle:
                restantes = int(detalle['n_est_remaining_calls'])
                if restantes == 0 and not campana.es_manual:
                    self.remove_campana_wombat(campana)
                    campana.finalizar()

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
        salida = service_wombat.update_config_wombat(
            "deletecampaign_ep.json", url_edit)

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
