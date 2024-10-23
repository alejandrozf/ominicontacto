# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from ominicontacto_app.services.exportar_base_datos import SincronizarBaseDatosContactosService
from ominicontacto_app.services.dialer.phone_dialer import AbstractPhoneDialerService
from ominicontacto_app.services.dialer.campana_wombat import CampanaService
from ominicontacto_app.services.dialer.wombat_api import WombatAPI
from ominicontacto_app.models import Campana


class WombatService(AbstractPhoneDialerService):

    def __init__(self) -> None:
        self.wombat_api = WombatAPI()
        self.campana_service = CampanaService()

    def crear_campana(self, campana, evitar_duplicados, evitar_sin_telefono, prefijo_discador):
        service_base = SincronizarBaseDatosContactosService()
        # Crea un achivo con la lista de contactos para importar a wombat
        service_base.crear_lista(campana, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)
        # crear campana en wombat
        self.campana_service.crear_campana_wombat(campana)
        # crea trunk en wombat
        self.campana_service.crear_trunk_campana_wombat(campana)
        # crea reglas de incidencia en wombat
        for regla in campana.reglas_incidencia.all():
            parametros = [regla.get_estado_wombat(), regla.estado_personalizado,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            self.campana_service.crear_reschedule_campana_wombat(campana, parametros)
        # crea endpoint en wombat
        self.campana_service.guardar_endpoint_campana_wombat(campana)
        # asocia endpoint en wombat a campana
        self.campana_service.crear_endpoint_asociacion_campana_wombat(
            campana)
        # crea lista en wombat
        self.campana_service.crear_lista_contactos_wombat(campana)
        # asocia lista a campana en wombat
        self.campana_service.crear_lista_asociacion_campana_wombat(campana)

    def eliminar_campana(self, campana) -> bool:
        return self.campana_service.remove_campana_wombat(self.object)

    def editar_campana(self, campana):
        service_ok = self.campana_service.crear_campana_wombat(campana)
        if service_ok:
            service_ok = self.campana_service.update_endpoint(campana)
        if not service_ok:
            raise Exception('No se ha podico crear la campaña en Wombat.')
        # recarga campaña en wombat
        if campana.estado == Campana.ESTADO_ACTIVA:
            self.campana_service.reload_campana_wombat(campana)

    def iniciar_campana(self, campana):
        self.campana_service.start_campana_wombat(campana)

    def pausar_campana(self, campana):
        self.campana_service.pausar_campana_wombat(campana)

    def reanudar_campana(self, campana):
        self.campana_service.despausar_campana_wombat(campana)

    def terminar_campana(self, campana):
        self.campana_service.remove_campana_wombat(campana)

    def agendar_llamada(self, campana, agenda):
        self.wombat_api.agendar_llamada(campana, agenda)

    def notificar_incidencia_por_calificacion(self, regla, dialer_call_id=None, contact_id=None):
        service_wombat = WombatAPI()
        url_notify = '/api/calls/?op=extstatus&wombatid={0}&status={1}'.format(
            dialer_call_id, regla.wombat_id)
        service_wombat.set_call_ext_status(url_notify)

    def crear_regla_de_incidencia(self, regla, es_de_calificacion=False):
        if not es_de_calificacion:
            parametros = [regla.get_estado_wombat(), str(regla.estado_personalizado or ""),
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            campana = regla.campana
        else:
            parametros = [regla.ESTADO_WOMBAT, regla.wombat_id,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            campana = regla.opcion_calificacion.campana

        self.campana_service.crear_reschedule_campana_wombat(campana, parametros)
        if campana.estado == Campana.ESTADO_ACTIVA:
            self.campana_service.reload_campana_wombat(self.campana)

    def eliminar_regla_de_incidencia(self, regla, es_de_calificacion=False) -> bool:
        remover = self.campana_service.eliminar_reschedule_wombat(regla)
        if remover:
            campana = regla.opcion_calificacion.campana
            if campana.estado == Campana.ESTADO_ACTIVA:
                self.campana_service.reload_campana_wombat(campana)
        return remover

    def editar_regla_de_incidencia(self, regla, campana, id_anterior, estado_anterior=None,
                                   es_de_calificacion=False) -> bool:
        editado = self.campana_service.editar_reschedule_wombat(regla, id_anterior, estado_anterior)
        if editado and campana.estado == Campana.ESTADO_ACTIVA:
            self.campana_service.reload_campana_wombat(self.campana)
        return editado

    def obtener_estado_campana(self, campana):
        dato_campana_run = self.campana_service.obtener_dato_campana_run(campana)
        if dato_campana_run:
            hoppercampId = dato_campana_run['hoppercampId']
            status = self.campana_service.obtener_status_campana_running(hoppercampId)
            data = {
                'error_consulta': False,
                'efectuadas': dato_campana_run['n_calls_attempted'],
                'terminadas': dato_campana_run['n_calls_completed'],
                'estimadas': dato_campana_run['n_est_remaining_calls'],
                'reintentos_abiertos': dato_campana_run['n_open_retries'],
                'status': status
            }
            return data

    def obtener_llamadas_pendientes(self, campana) -> int:
        dato_campana = self.campana_service.obtener_dato_campana_run(self.campana)
        if dato_campana:
            return dato_campana.get('n_est_remaining_calls', 0)
        return 0

    def obtener_llamadas_pendientes_por_id(self, campanas_por_id) -> int:
        estados_running_wombat = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                                  Campana.ESTADO_FINALIZADA]
        campanas_por_id_wombat = {}
        for campana_id, campana in campanas_por_id.items():
            if campana.estado in estados_running_wombat:
                campanas_por_id_wombat[campana.campaign_id_wombat] = campana
        dato_campanas = self.campana_service.obtener_datos_campanas_run(campanas_por_id_wombat)
        pendientes_por_id = {}
        for campana_id, datos_campana in dato_campanas.items():
            pendientes_por_id[campana_id] = datos_campana['n_est_remaining_calls']
        return pendientes_por_id
