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

from __future__ import unicode_literals

import logging as _logging

import json
import redis

from collections import OrderedDict
from django.views.generic import View
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Count
from django.conf import settings

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from simple_history.utils import update_change_reason

from api_app.views.permissions import TienePermisoOML
from api_app.serializers import (CampanaSerializer, )
from ominicontacto_app.models import (
    Campana, CalificacionCliente, AgenteProfile, AgendaContacto, )
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)
from reportes_app.reportes.reporte_llamadas import ReporteTipoDeLlamadasDeCampana
from ominicontacto_app.utiles import datetime_hora_minima_dia

logger = _logging.getLogger(__name__)


class SupervisorCampanasActivasViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las campañas activas relacionadas a un supervisor
    si este no es admin y todas las campañas activas en el caso de sí lo sea
    """
    serializer_class = CampanaSerializer
    permission_classes = (TienePermisoOML, )
    queryset = Campana.objects.obtener_activas()
    http_method_names = ['get']

    def get_queryset(self):
        superv_profile = self.request.user.get_supervisor_profile()
        if superv_profile.is_administrador:
            return super(SupervisorCampanasActivasViewSet, self).get_queryset()
        return superv_profile.obtener_campanas_asignadas_activas()


class AgentesStatusAPIView(APIView):
    """Devuelve información de los agentes en el sistema"""
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def _obtener_datos_agentes(self, supervisor_pk):
        redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        response = redis_connection.hgetall('OML:SUPERVISOR:{0}'.format(supervisor_pk))
        result = {}
        for agent_id, dato in response.items():
            result[agent_id] = json.loads(dato)
        return result

    def _obtener_ids_agentes_propios(self, request):
        supervisor_pk = request.user.get_supervisor_profile().user.pk
        agentes_dict = self._obtener_datos_agentes(supervisor_pk)
        return agentes_dict

    def get(self, request):
        online = []
        agentes_parseados = SupervisorActivityAmiManager()
        agentes_dict = self._obtener_ids_agentes_propios(request)
        for data_agente in agentes_parseados.obtener_agentes_activos():
            id_agente = int(data_agente.get('id', -1))
            status_agente = data_agente.get('status', '')
            if status_agente != 'OFFLINE' and str(id_agente) in agentes_dict:
                agente_dict = agentes_dict.get(str(id_agente), '')
                grupo_activo = agente_dict.get('grupo', '')
                campanas_activas = agente_dict.get('campana', [])
                data_agente['grupo'] = grupo_activo
                data_agente['campana'] = campanas_activas
                online.append(data_agente)
        return Response(data=online)


class StatusCampanasEntrantesView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(request.user)
        return Response(data={'errors': None,
                              'data': reporte.estadisticas})


class StatusCampanasSalientesView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        reporte = ReporteDeLLamadasSalientesDeSupervision(request.user)
        return Response(data={'errors': None,
                              'data': reporte.estadisticas})


class InteraccionDeSupervisorSobreAgenteView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        self.supervisor = self.request.user.get_supervisor_profile()
        self.agente_id = kwargs.get('pk')
        # TODO: Verificar que el supervisor sea responsable del agente.
        return super(InteraccionDeSupervisorSobreAgenteView, self).dispatch(
            request, *args, **kwargs)

    def post(self, request, pk):
        accion = request.POST.get('accion')
        servicio_acciones = SupervisorActivityAmiManager()
        error = servicio_acciones.ejecutar_accion_sobre_agente(
            self.supervisor, self.agente_id, accion)
        if error:
            return Response(data={
                'status': 'ERROR',
                'message': error
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class ReasignarAgendaContactoView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def post(self, request):
        agenda_id = request.data.get('agenda_id')
        agente_id = request.data.get('agent_id')

        try:
            agenda = AgendaContacto.objects.get(id=agenda_id,
                                                tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        except AgendaContacto.DoesNotExist:
            return Response(data={
                'status': 'ERROR',
                'message': _('ID Agenda incorrecto')
            })
        try:
            agente = agenda.campana.queue_campana.members.get(id=agente_id)
        except AgenteProfile.DoesNotExist:
            return Response(data={
                'status': 'ERROR',
                'message': _('ID Agente incorrecto')
            })

        supervisor_profile = self.request.user.get_supervisor_profile()
        campanas_asignadas_actuales = supervisor_profile.campanas_asignadas_actuales()
        if not campanas_asignadas_actuales.filter(id=agenda.campana.id).exists():
            return Response(data={
                'status': 'ERROR',
                'message': _('No tiene permiso para editar esta Agenda')
            })

        agenda.agente = agente
        agenda.save()
        calificacion = CalificacionCliente.objects.get(contacto=agenda.contacto,
                                                       opcion_calificacion__campana=agenda.campana)
        calificacion.agente = agente
        calificacion.save()
        update_change_reason(calificacion, 'reasignacion')

        return Response(data={
            'status': 'OK',
            'agenda_id': agenda_id,
            'agent_name': agente.user.get_full_name()
        })


class DataAgendaContactoView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get', ]

    def get(self, request, agenda_id):

        try:
            agenda = AgendaContacto.objects.get(id=agenda_id,
                                                tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        except AgendaContacto.DoesNotExist:
            return Response(data={
                'status': 'ERROR',
                'message': _('ID Agenda incorrecto')
            })
        supervisor_profile = self.request.user.get_supervisor_profile()
        campanas_asignadas_actuales = supervisor_profile.campanas_asignadas_actuales()
        if not campanas_asignadas_actuales.filter(id=agenda.campana.id).exists():
            return Response(data={
                'status': 'ERROR',
                'message': _('No tiene permiso para editar esta Agenda')
            })

        contact_data = agenda.contacto.obtener_datos()
        return Response(data={
            'status': 'OK',
            'agenda_id': agenda_id,
            'observations': agenda.observaciones,
            'contact_data': contact_data
        })


# ########################################################
# TODO: Funcionalidad vieja que podria volver a utilizarse
class LlamadasDeCampanaView(View):
    """
    Devuelve un JSON con cantidades de tipos de llamadas de la campaña para el dia de la fecha
    """
    TIPOS = OrderedDict([
        ("recibidas", _(u'Recibidas')),
        ('efectuadas', _(u'Efectuadas')),
        ("atendidas", _(u'Atendidas')),
        ('conectadas', _(u'Conectadas')),
        ('no_conectadas', _(u'No Conectadas')),
        ("abandonadas", _(u'Abandonadas')),
        ("expiradas", _(u'Expiradas')),
        ("t_espera_conexion", _(u'Tiempo de Espera de Conexión(prom.)')),
        ('t_espera_atencion', _(u'Tiempo de Espera de Atención(prom.)')),
        ("t_abandono", _(u'Tiempo de Abandono(prom.)')),
    ])
    TIPOS_MANUALES = OrderedDict([
        ("efectuadas_manuales", _(u'Efectuadas Manuales')),
        ("conectadas_manuales", _(u'Conectadas Manuales')),
        ("no_conectadas_manuales", _(u'No Conectadas Manuales')),
        ("t_espera_conexion_manuales", _(u'Tiempo de Espera de Conexión Manuales(prom.)')),
    ])

    def get(self, request, pk_campana):
        hoy_ahora = now()
        hoy_inicio = datetime_hora_minima_dia(hoy_ahora)
        try:
            reporte = ReporteTipoDeLlamadasDeCampana(hoy_inicio, hoy_ahora, pk_campana)
            reporte.estadisticas.pop('nombre')
            data = {'status': 'OK', 'llamadas': []}
            for campo, nombre in self.TIPOS.iteritems():
                if campo in reporte.estadisticas:
                    data['llamadas'].append((nombre, reporte.estadisticas[campo]))
            for campo, nombre in self.TIPOS_MANUALES.iteritems():
                if campo in reporte.estadisticas:
                    if 'manuales' not in data:
                        data['manuales'] = []
                    data['manuales'].append((nombre, reporte.estadisticas[campo]))

        except Campana.DoesNotExist:
            data = {'status': 'Error', 'error_message': _(u'No existe la campaña')}

        return JsonResponse(data=data)


class CalificacionesDeCampanaView(View):
    """
    Devuelve un JSON con cantidades de cada tipo de calificación de una campaña del dia de la fecha
    """
    def get(self, request, pk_campana):

        try:
            campana = Campana.objects.get(id=pk_campana)
        except Campana.DoesNotExist:
            return JsonResponse(data={'status': 'Error',
                                      'error_message': _(u'No existe la campaña')})

        data = {'status': 'OK'}
        for opcion in campana.opciones_calificacion.all():
            data[opcion.nombre] = 0
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gt=datetime_hora_minima_dia(now()),
            opcion_calificacion__campana_id=pk_campana)
        cantidades = calificaciones.values('opcion_calificacion__nombre').annotate(
            cantidad=Count('opcion_calificacion__nombre')).order_by()

        for opcion in cantidades:
            data[opcion['opcion_calificacion__nombre']] = opcion['cantidad']

        return JsonResponse(data=data)
