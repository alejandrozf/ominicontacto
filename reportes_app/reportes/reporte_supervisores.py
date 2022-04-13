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

import json

from ominicontacto_app.models import Campana, AgenteProfile, SupervisorProfile, QueueMember
from ominicontacto_app.services.asterisk.redis_database import AbstractRedisFamily


class ReporteSupervisores(object):

    def __init__(self):
        self.estadisticas = {}
        self.calcular_datos_de_agentes_asignados_por_supervisor()

    def calcular_datos_de_agentes_asignados_por_supervisor(self):

        nombres_campanas = dict(Campana.objects.obtener_all_dialplan_asterisk().values_list(
            'id', 'nombre'))
        agentes_por_campana = {}
        for id_campana in nombres_campanas.keys():
            agentes_por_campana[id_campana] = set()

        # Obtengo los datos de cada agente
        datos_por_agente = {}
        # Grupo
        grupos_de_agentes = AgenteProfile.objects.obtener_activos().values('id', 'grupo__nombre')
        for grupo_de_agente in grupos_de_agentes:
            datos_por_agente[grupo_de_agente['id']] = {
                'grupo': grupo_de_agente['grupo__nombre'],
                'campana': []
            }
        # Nombres de campañas a la que esta asignado
        asignaciones_agentes = QueueMember.objects.values('member_id', 'queue_name__campana_id')
        for asignacion in asignaciones_agentes:
            id_campana = asignacion['queue_name__campana_id']
            id_agente = asignacion['member_id']
            if id_campana in nombres_campanas and id_agente in datos_por_agente:
                datos_por_agente[id_agente]['campana'].append(nombres_campanas[id_campana])
                agentes_por_campana[id_campana].add(id_agente)

        # Los administradores tendran asignados a todos los agentes
        administradores = []
        agentes_por_supervisor = {}
        supervisores = SupervisorProfile.objects.using('replica').filter(
            borrado=False, user__is_active=True, user__borrado=False)
        for supervisor in supervisores:
            if supervisor.is_administrador:
                administradores.append(supervisor.id)
            else:
                agentes_por_supervisor[supervisor.id] = set()

        # Calculo ids de agentes asociados a supervisores a traves de campañas
        asignaciones_campanas = Campana.objects.obtener_all_dialplan_asterisk().values(
            'id', 'supervisors__supervisorprofile')
        for asignacion in asignaciones_campanas:
            id_campana = asignacion['id']
            id_supervisor = asignacion['supervisors__supervisorprofile']
            if id_supervisor in agentes_por_supervisor:
                agentes_por_supervisor[id_supervisor].update(agentes_por_campana[id_campana])

        # Para cada supervisor asigno los datos completos de sus agentes asignados
        for id_supervisor, ids_agentes in agentes_por_supervisor.items():
            if ids_agentes:
                self.estadisticas[id_supervisor] = {}
                for id_agente in ids_agentes:
                    self.estadisticas[id_supervisor][id_agente] = datos_por_agente[id_agente]

        # Completo los datos de todos los agentes para todos los administradores
        for id_administrador in administradores:
            self.estadisticas[id_administrador] = datos_por_agente


class ReporteSupervisoresFamily(AbstractRedisFamily):

    def _create_dict(self, family_member):
        return family_member[1]

    def _obtener_todos(self):
        return self.reporte_resultado

    def _obtener_resultado(self):
        reporte_resultado = []
        reporte = ReporteSupervisores()
        for (supervisor_id, datos) in reporte.estadisticas.items():
            datos_json = {}
            for agente_id, dato in datos.items():
                datos_json[agente_id] = json.dumps(dato)
            reporte_resultado.append((supervisor_id, datos_json))
        return reporte_resultado

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member[0])

    def get_nombre_families(self):
        return "OML:SUPERVISOR"

    def regenerar_families(self):
        """regenera la family"""
        # Precalculo el resultado para que no quede vacio redis mientras calcula
        self.reporte_resultado = self._obtener_resultado()
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
