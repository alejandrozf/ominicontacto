# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import FormularioDemo, Campana
from ominicontacto_app.utiles import elimina_coma
from ominicontacto_app.services.wombat_service import WombatService
from ominicontacto_app.services.wombat_config import CampanaCreator

import logging


class CampanaService():

    def crear_formulario(self, campana):
        assert isinstance(campana, Campana)
        for contacto in campana.bd_contacto.contactos.all():
            FormularioDemo.objects.create(campana=campana, contacto=contacto)

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

    def crear_campana_wombat(self, campana):
        service_wombat = WombatService()
        service_wombat_config = CampanaCreator()
        service_wombat_config.create_json(campana)
        salida = service_wombat.update_config_wombat()
        campaign_id = self.obtener_campana_id_wombat(salida)
        if campaign_id:
            campana.guardar_campaign_id_wombat(campaign_id)
            return True
        return False
