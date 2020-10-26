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

from ominicontacto_app.models import Campana, AgenteProfile, SupervisorProfile
from ominicontacto_app.services.asterisk.redis_database import AbstractRedisFamily


class ReporteSupervisores(object):

    def __init__(self):
        self.estadisticas = {}
        self._obtener_datos_agentes_propios_supervisores()

    def _obtener_datos_agentes_propios_supervisores(self):
        # FIXME: hace un loop mandando queries, hacerlo mas óptimo
        supervisors_dict = {}
        for supervisor_profile in SupervisorProfile.objects.all():
            if supervisor_profile.user.get_is_administrador():
                campanas = Campana.objects.all()
            else:
                campanas = supervisor_profile.campanas_asignadas_actuales()
            ids_agentes = list(campanas.values_list(
                'queue_campana__members__pk', flat=True).distinct())
            ids_campanas = list(campanas.values_list('pk', flat=True))
            agentes_dict = {}
            for agente in AgenteProfile.objects.filter(
                    pk__in=ids_agentes,
                    campana_member__queue_name__campana__pk__in=ids_campanas).select_related(
                        'grupo').prefetch_related('campana_member__queue_name__campana'):
                agentes_dict[agente.pk] = {
                    'grupo': agente.grupo.nombre,
                    'campana': list(agente.queue_set.values_list('campana__nombre', flat=True))
                }
            if agentes_dict != {}:
                supervisors_dict[supervisor_profile.pk] = agentes_dict
        self.estadisticas = supervisors_dict


class ReporteSupervisoresFamily(AbstractRedisFamily):

    def _create_dict(self, family_member):
        return family_member[1]

    def _obtener_todos(self):
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
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
