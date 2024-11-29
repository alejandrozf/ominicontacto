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

class AbstractPhoneDialerService(object):

    def crear_campana(self, campana, evitar_duplicados, evitar_sin_telefono, prefijo_discador):
        raise NotImplementedError()

    def eliminar_campana(self, campana) -> bool:
        raise NotImplementedError()

    def editar_campana(self, campana):
        raise NotImplementedError()

    def iniciar_campana(self, campana):
        raise NotImplementedError()

    def pausar_campana(self, campana):
        raise NotImplementedError()

    def reanudar_campana(self, campana):
        raise NotImplementedError()

    def terminar_campana(self, campana):
        raise NotImplementedError()

    def agendar_llamada(self, campana, agenda):
        raise NotImplementedError()

    def notificar_incidencia_por_calificacion(self, dialer_call_id=None, contact_id=None):
        """
        Notifica que se califico una llamada con una opcion con regla de incidencia
        Setea el extStatus correspondiente a la opcion elegida en la llamada de Wombat
        """
        raise NotImplementedError()

    def crear_regla_de_incidencia(self, regla, es_de_calificacion=False):
        raise NotImplementedError()

    def eliminar_regla_de_incidencia(self, regla, es_de_calificacion=False) -> bool:
        raise NotImplementedError()

    def editar_regla_de_incidencia(self, regla, campana, id_anterior, estado_anterior=None,
                                   es_de_calificacion=False) -> bool:
        raise NotImplementedError()

    def cambiar_bd_contactos(self, campana, params=None):
        raise NotImplementedError()

    def obtener_estado_campana(self, campana):
        raise NotImplementedError()

    def obtener_llamadas_pendientes(self, campana) -> int:
        raise NotImplementedError()

    def obtener_llamadas_pendientes_por_id(self, campanas_por_id) -> int:
        raise NotImplementedError()

    def finalizar_campanas_sin_llamadas_pendientes(self, campanas):
        raise NotImplementedError()
