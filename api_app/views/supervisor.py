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

from json.decoder import JSONDecodeError

import logging as _logging

import datetime
import json
import threading

from collections import OrderedDict
from django.views.generic import View
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework import status

from simple_history.utils import update_change_reason

from easyaudit.models import CRUDEvent, RequestEvent, LoginEvent

from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.base import (
    CampanaSerializer, AuditSupervisorCRUDEventSerializer, AuditSupervisorLoginEventSerializer,
    AuditSupervisorRequestEventSerializer)
from ominicontacto_app.models import (
    Campana, CalificacionCliente, AgenteProfile, AgendaContacto, AgenteEnContacto, Grupo)
from ominicontacto_app.services.asterisk.supervisor_activity import (
    SupervisorActivityAmiManager)
from reportes_app.models import LlamadaLog
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, )
from reportes_app.reportes.reporte_llamadas import ReporteTipoDeLlamadasDeCampana
from reportes_app.reportes.reporte_llamados_contactados_csv import (
    ExportacionCampanaCSV, ReporteCalificadosCSV, ReporteContactadosCSV, ReporteNoAtendidosCSV)
from ominicontacto_app.services.reporte_resultados_de_base_csv import (
    ExportacionReporteCSV
)
from ominicontacto_app.services.reporte_resultados_de_base import (
    ReporteContactacionesCSV
)
from reportes_app.reportes.reporte_llamadas_salientes import ReporteLlamadasSalienteFamily
from ominicontacto_app.services.reporte_respuestas_formulario import (
    ReporteFormularioGestionCampanaCSV)
from ominicontacto_app.services.reporte_campana_calificacion import ReporteCalificacionesCampanaCSV
from ominicontacto_app.services.reporte_campana_csv import ExportacionArchivoCampanaCSV
from ominicontacto_app.services.redis.connection import create_redis_connection

from ominicontacto_app.utiles import (
    datetime_hora_minima_dia, datetime_hora_maxima_dia, convert_fecha_datetime)
from notification_app.notification import RedisStreamNotifier, AgentNotifier


logger = _logging.getLogger(__name__)


class SupervisorCampanasActivasViewSet(APIView):
    """Servicio que devuelve las campañas activas relacionadas a un supervisor
    si este no es admin y todas las campañas activas en el caso de sí lo sea
    """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    serializer_class = CampanaSerializer
    http_method_names = ['get']
    renderer_classes = (JSONRenderer, )
    TIPOS_VALIDOS = [x[0] for x in Campana.TYPES_CAMPANA]
    ESTADOS_VALIDOS = [x[0] for x in Campana.ESTADOS]

    def procesar_filtros(self):
        self.filtro_tipo = None
        self.filtro_tipo_lista = None
        self.filtro_nombre = None
        self.filtro_campanas_agente = None
        self.filtro_estado = Campana.ESTADO_ACTIVA
        self.filtro_estado_lista = None

        if 'type' in self.request.GET:
            try:
                tipo = json.loads(self.request.GET.get('type'))
                if isinstance(tipo, list):
                    for x in tipo:
                        if x not in self.TIPOS_VALIDOS:
                            return _('Filtro "type" inválido')
                    self.filtro_tipo_lista = tipo
                else:
                    if tipo not in self.TIPOS_VALIDOS:
                        return _('Filtro "type" inválido')
                    self.filtro_tipo = tipo
            except JSONDecodeError:
                return _('Filtro "type" inválido')

        if 'name' in self.request.GET:
            self.filtro_nombre = self.request.GET.get('name')
        if 'agent' in self.request.GET:
            agente_id = self.request.GET.get('agent')
            try:
                agente_id = int(agente_id)
            except ValueError:
                return _('Filtro "agent" inválido')
            try:
                agente = AgenteProfile.objects.get(id=agente_id)
            except AgenteProfile.DoesNotExist:
                return _('Agente inexistente')
            # TODO: Verificar que el supervisor sea responsable del agente.
            self.filtro_campanas_agente = agente.campana_member.values_list(
                'queue_name__campana_id', flat=True)

        if 'status' in self.request.GET:
            try:
                estado = json.loads(self.request.GET.get('status'))
                if isinstance(estado, list):
                    for x in estado:
                        if x not in self.ESTADOS_VALIDOS:
                            return _('Filtro "status" inválido')
                    self.filtro_estado_lista = estado
                    self.filtro_estado = None
                else:
                    if estado not in self.ESTADOS_VALIDOS:
                        return _('Filtro "status" inválido')
                    self.filtro_estado = estado
            except JSONDecodeError:
                return _('Filtro "status" inválido')

        return None

    def get(self, request):
        error = self.procesar_filtros()
        if error:
            return Response(data={'status': 'ERROR', 'message': error})

        superv_profile = self.request.user.get_supervisor_profile()
        if superv_profile.is_administrador:
            campanas = Campana.objects.all()
        else:
            campanas = self.request.user.campanasupervisors.all()

        if self.filtro_estado:
            campanas = campanas.filter(estado=self.filtro_estado)
        if self.filtro_estado_lista:
            campanas = campanas.filter(estado__in=self.filtro_estado_lista)
        if self.filtro_tipo:
            campanas = campanas.filter(type=self.filtro_tipo)
        if self.filtro_tipo_lista:
            campanas = campanas.filter(type__in=self.filtro_tipo_lista)
        if self.filtro_nombre:
            campanas = campanas.filter(nombre__contains=self.filtro_nombre)
        if self.filtro_campanas_agente is not None:
            if self.filtro_campanas_agente == []:
                return Response([])
            campanas = campanas.filter(id__in=self.filtro_campanas_agente)
        return Response([CampanaSerializer(campana).data for campana in campanas])


class AgentesStatusAPIView(APIView):
    """Devuelve información de los agentes en el sistema"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def _obtener_datos_agentes(self, supervisor_pk):
        redis_connection = create_redis_connection()
        response = redis_connection.hgetall('OML:SUPERVISOR:{0}'.format(supervisor_pk))
        result = {}
        for agent_id, dato in response.items():
            result[agent_id] = json.loads(dato)
        return result

    def _obtener_ids_agentes_propios(self, request):
        supervisor_pk = request.user.get_supervisor_profile().pk
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


class UsuariosAgentesAPIView(APIView):
    """ Devuelve id, username y full_name de los Agentes asignados """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        supervisor = self.request.user.get_supervisor_profile()
        agentes = AgenteProfile.objects.obtener_agentes_supervisor(supervisor)
        values = agentes.values('id', 'user__username', 'user__first_name', 'user__last_name')
        data = {
            item['id']: {
                'username': item['user__username'],
                'first_name': item['user__first_name'],
                'lastname': item['user__last_name']
            } for item in values
        }
        return Response(data=data)


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

    def _obtener_datos_campanas(self, user):
        redis_saliente = ReporteLlamadasSalienteFamily()
        if not user.is_supervisor:
            campanas = Campana.objects.all()
        else:
            campanas = user.get_supervisor_profile().obtener_campanas_asignadas_activas()
        query_campanas = campanas.filter(
            type__in=[Campana.TYPE_DIALER,
                      Campana.TYPE_PREVIEW,
                      Campana.TYPE_MANUAL])
        data_saliente = []
        for campana in query_campanas:
            estadisticas = redis_saliente.get_value(campana, 'ESTADISTICAS')
            if estadisticas:
                data_saliente.append(json.loads(estadisticas))
        return data_saliente

    def get(self, request):
        supervisor_pk = request.user
        datos_campana = self._obtener_datos_campanas(supervisor_pk)
        return Response(data=datos_campana)


class InteraccionDeSupervisorSobreAgenteView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request, pk):
        # TODO: Verificar que el supervisor sea responsable del agente.
        self.supervisor = self.request.user.get_supervisor_profile()
        if self.supervisor is None:
            return Response(data={'status': 'ERROR', 'message': 'Wrong user profile'},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            agente_profile = AgenteProfile.objects.get(id=pk)
        except AgenteProfile.DoesNotExist:
            return Response(data={'status': 'ERROR', 'message': 'Agent not found'},
                            status=status.HTTP_404_NOT_FOUND)

        accion = request.data.get('accion')
        servicio_acciones = SupervisorActivityAmiManager()
        error = servicio_acciones.ejecutar_accion_sobre_agente(
            self.supervisor, agente_profile, accion)
        if error:
            return Response(data={
                'status': 'ERROR',
                'message': error
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class EnviarMensajeAgentesView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        try:
            self.supervisor = self.request.user.get_supervisor_profile()
            recipient_id = request.POST.get('recipient-id')
            recipient_type = request.POST.get('recipient-type')
            message = request.POST.get('message-text')
            ag_n = AgentNotifier()
            user_list = []
            if recipient_type == 'agent':
                agent = AgenteProfile.objects.get(id=recipient_id)
                user_list.append(agent.user_id)
            elif recipient_type == 'group':
                user_list = Grupo.objects.get(
                    nombre=recipient_id).agentes.values_list('user_id', flat=True)
            elif recipient_type == 'campaign':
                campana = Campana.objects.get(nombre=recipient_id)
                user_list = campana.obtener_agentes().values_list('user_id', flat=True)
            for user in user_list:
                ag_n.notify_supervisor_send_message(
                    user,
                    message,
                    self.supervisor.user.username
                )
            return Response(data={'status': 'OK'})
        except Exception as e:
            print(e)
            return Response(data={'status': 'ERROR'})


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


class ExportarCSVMixin:

    def loguear_inicio_exportacion(
            self, tipo, campana_id, supervisor_nombre, fecha_hasta, fecha_desde):
        cadena_inicio_exportacion_info = (
            "Generating CSV report of {0} campaign {1}  from user {2}. ".format(
                tipo, campana_id, supervisor_nombre)) + \
            "Date filter: from {0} to {1}".format(fecha_hasta, fecha_desde)
        logger.info(cadena_inicio_exportacion_info)


class ExportarCSVResultadosBaseContactados(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv(self, key_task, campana, all_data):
        reporte_csv = ReporteContactacionesCSV(
            campana,
            key_task,
            all_data
        )
        datos_reporte = reporte_csv.datos
        service_csv = ExportacionReporteCSV()
        if all_data:
            service_csv.exportar_reportes_csv(
                campana,
                datos_contactaciones_todos=datos_reporte
            )
        else:
            service_csv.exportar_reportes_csv(
                campana,
                datos_contactaciones=datos_reporte
            )

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        all_data = bool(int(request.data.get('all_data')))
        campana = Campana.objects.get(pk=campana_id)
        sufijo_canal = 'ALL_CONTACTED' if all_data else 'CONTACTED'
        key_task = "OML:BASE_RESULTS_REPORT:{0}:{1}:{2}".format(
            sufijo_canal,
            campana_id,
            task_id
        )

        # Hilo para generación de reporte
        thread_exportacion = threading.Thread(
            target=self.generar_csv,
            args=[
                key_task,
                campana,
                all_data
            ]
        )
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        if all_data:
            log_info = 'resultados_de_base_contactaciones_todos'
        else:
            log_info = 'resultados_de_base_contactaciones'
        self.loguear_inicio_exportacion(
            log_info,
            campana_id,
            request.user.username,
            fecha_desde=None,
            fecha_hasta=None
        )

        return Response(
            data={
                'status': 'OK',
                'msg': _('Exportación de CSV en proceso'),
                'id': task_id,
            }
        )


class ExportarCSVContactados(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv_contactados(self, key_task, campana, desde, hasta):

        reporte_contactados_csv = ReporteContactadosCSV(
            campana, key_task, desde, hasta)
        datos_contactados = reporte_contactados_csv.datos
        service_csv = ExportacionCampanaCSV()
        service_csv.exportar_reportes_csv(campana, datos_contactados=datos_contactados)

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        desde = request.data.get('desde')
        hasta = request.data.get('hasta')
        fecha_desde = convert_fecha_datetime(desde)
        fecha_hasta = convert_fecha_datetime(hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana = Campana.objects.get(pk=campana_id)

        # generar id para la operacion de acuerdo a (timestamp, campana, supervisor)
        # obtener de request

        key_task = 'OML:STATUS_CSV_REPORT:CONTACTED:{0}:{1}'.format(campana_id, task_id)
        # chequear si el supervisor esta asignado a la campaña
        # chequear si la campaña existe

        thread_exportacion = threading.Thread(
            target=self.generar_csv_contactados, args=[key_task, campana, fecha_desde, fecha_hasta])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        self.loguear_inicio_exportacion(
            'contactados', campana_id, request.user.username, fecha_hasta.strftime("%m/%d/%Y"),
            fecha_desde.strftime("%m/%d/%Y"))

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de contactados a .csv en proceso'),
            'id': task_id,
        })


class ExportarCSVCalificados(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv_calificados(self, key_task, campana, desde, hasta):

        reporte_calificados_csv = ReporteCalificadosCSV(
            campana, key_task, desde, hasta)
        datos_calificados = reporte_calificados_csv.datos
        service_csv = ExportacionCampanaCSV()
        service_csv.exportar_reportes_csv(campana, datos_calificados=datos_calificados)

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        desde = request.data.get('desde')
        hasta = request.data.get('hasta')
        fecha_desde = convert_fecha_datetime(desde)
        fecha_hasta = convert_fecha_datetime(hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana = Campana.objects.get(pk=campana_id)
        # generar id para la operacion de acuerdo a (timestamp, campana, supervisor)
        # obtener de request

        key_task = 'OML:STATUS_CSV_REPORT:DISPOSITIONED:{0}:{1}'.format(campana_id, task_id)

        # chequear si el supervisor esta asignado a la campaña
        # chequear si la campaña existe

        thread_exportacion = threading.Thread(
            target=self.generar_csv_calificados, args=[key_task, campana, fecha_desde, fecha_hasta])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        self.loguear_inicio_exportacion(
            'calificados', campana_id, request.user.username, fecha_hasta.strftime("%m/%d/%Y"),
            fecha_desde.strftime("%m/%d/%Y"))

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de calificados a .csv en proceso'),
            'id': task_id,
        })


class ExportarCSVNoAtendidos(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv_no_atendidos(self, key_task, campana, desde, hasta):

        reporte_no_atendidos_csv = ReporteNoAtendidosCSV(
            campana, key_task, desde, hasta)
        datos_no_atendidos = reporte_no_atendidos_csv.datos
        service_csv = ExportacionCampanaCSV()
        service_csv.exportar_reportes_csv(campana, datos_no_atendidos=datos_no_atendidos)

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        desde = request.data.get('desde')
        hasta = request.data.get('hasta')
        fecha_desde = convert_fecha_datetime(desde)
        fecha_hasta = convert_fecha_datetime(hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana = Campana.objects.get(pk=campana_id)
        # generar id para la operacion de acuerdo a (timestamp, campana, supervisor)
        # obtener de request

        key_task = 'OML:STATUS_CSV_REPORT:NOT_ATTENDED:{0}:{1}'.format(campana_id, task_id)

        # chequear si el supervisor esta asignado a la campaña
        # chequear si la campaña existe

        thread_exportacion = threading.Thread(
            target=self.generar_csv_no_atendidos,
            args=[key_task, campana, fecha_desde, fecha_hasta])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()
        self.loguear_inicio_exportacion(
            'no atendidos', campana_id, request.user.username, fecha_hasta.strftime("%m/%d/%Y"),
            fecha_desde.strftime("%m/%d/%Y"))

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de no atendidos a .csv en proceso'),
            'id': task_id,
        })


class ContactosAsignadosCampanaPreviewView(APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get', ]

    def _obtener_estado(self, estado, agente_id):
        if estado == AgenteEnContacto.ESTADO_FINALIZADO:
            return _('Finalizado')
        if estado == AgenteEnContacto.ESTADO_INICIAL and agente_id == -1:
            return _('Liberado')
        else:
            return _('Reservado')

    def _obtener_datos_agente_contacto(self, agentes_contactos, nombres_agentes):
        datos_agente = {}
        for agente_contacto in agentes_contactos:
            datos = {}
            datos['estado'] = self._obtener_estado(agente_contacto.estado,
                                                   agente_contacto.agente_id)
            if not agente_contacto.agente_id == -1:
                datos['agente'] = nombres_agentes[agente_contacto.agente_id]
            else:
                datos['agente'] = ''
            datos_agente[agente_contacto.contacto_id] = datos
        return datos_agente

    def get(self, request, pk_campana):
        campana = Campana.objects.get(id=pk_campana)
        contactos = campana.bd_contacto.contactos.all()
        contactos_ids = [contacto.id for contacto in contactos]
        agentes_contactos = [agente_contacto for agente_contacto in AgenteEnContacto.objects.filter(
            campana_id=pk_campana, contacto_id__in=contactos_ids)]
        agente_ids = [agente_contacto.agente_id for agente_contacto in agentes_contactos]
        nombres_agentes = {agente.id: agente.user.get_full_name()
                           for agente in AgenteProfile.objects.select_related(
                           'user').filter(pk__in=agente_ids)}
        datos_agente = self._obtener_datos_agente_contacto(agentes_contactos, nombres_agentes)

        data_contacto = []
        for contacto in contactos:
            dato_agente = datos_agente.get(contacto.id)
            # Si no hay datos de AgenteEnContacto no es asignable
            if dato_agente is None:
                continue
            datos = {}
            datos['id'] = contacto.id
            datos['telefono'] = contacto.telefono
            datos['id_externo'] = contacto.id_externo
            if dato_agente:
                datos['estado'] = dato_agente['estado']
                datos['agente'] = dato_agente['agente']
            data_contacto.append(datos)

        return Response(data=data_contacto)


class ExportarCSVCalificacionesCampana(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv_calificaciones(sself, key_task, campana, desde, hasta):
        reporte_calificados_csv = ReporteCalificacionesCampanaCSV(
            campana, key_task, desde, hasta)
        datos_calificados = reporte_calificados_csv.datos
        service_csv = ExportacionArchivoCampanaCSV(campana, "calificados")
        service_csv.exportar_reportes_csv(datos=datos_calificados)

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        desde = request.data.get('desde')
        hasta = request.data.get('hasta')
        fecha_desde = convert_fecha_datetime(desde)
        fecha_hasta = convert_fecha_datetime(hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana = Campana.objects.get(pk=campana_id)
        # generar id para la operacion de acuerdo a (timestamp, campana, supervisor)
        # obtener de request

        key_task = 'OML:STATUS_CSV_REPORT:DISPOSITIONED:{0}:{1}'.format(campana_id, task_id)

        # chequear si el supervisor esta asignado a la campaña
        # chequear si la campaña existe

        thread_exportacion = threading.Thread(
            target=self.generar_csv_calificaciones, args=[key_task, campana,
                                                          fecha_desde, fecha_hasta])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        self.loguear_inicio_exportacion(
            'calificaciones', campana_id, request.user.username, fecha_hasta.strftime("%m/%d/%Y"),
            fecha_desde.strftime("%m/%d/%Y"))

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de calificaciones a .csv en proceso'),
            'id': task_id,
        })


class ExportarCSVFormularioGestionCampana(ExportarCSVMixin, APIView):
    permission_classes = (TienePermisoOML, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post', ]

    def generar_csv_gestion(sself, key_task, campana, desde, hasta):
        reporte_gestion_csv = ReporteFormularioGestionCampanaCSV(
            campana, key_task, desde, hasta)
        datos_formulario_gestion = reporte_gestion_csv.datos
        service_csv = ExportacionArchivoCampanaCSV(campana, "formulario_gestion")
        service_csv.exportar_reportes_csv(datos=datos_formulario_gestion)

    def post(self, request):
        campana_id = request.data.get('campana_id')
        task_id = request.data.get('task_id')
        desde = request.data.get('desde')
        hasta = request.data.get('hasta')
        fecha_desde = convert_fecha_datetime(desde)
        fecha_hasta = convert_fecha_datetime(hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana = Campana.objects.get(pk=campana_id)
        # generar id para la operacion de acuerdo a (timestamp, campana, supervisor)
        # obtener de request
        key_task = 'OML:STATUS_CSV_REPORT:ENGAGED_DISPOSITIONS:{0}:{1}'.format(campana_id, task_id)

        # chequear si el supervisor esta asignado a la campaña
        # chequear si la campaña existe

        thread_exportacion = threading.Thread(
            target=self.generar_csv_gestion, args=[key_task, campana, fecha_desde, fecha_hasta])
        thread_exportacion.setDaemon(True)
        thread_exportacion.start()

        self.loguear_inicio_exportacion(
            'gestion_calificaciones', campana_id, request.user.username,
            fecha_hasta.strftime("%m/%d/%Y"), fecha_desde.strftime("%m/%d/%Y"))

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de Formularios de Gestiones a .csv en proceso'),
            'id': task_id,
        })


class DashboardSupervision(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def _cantidad_campanas_activas(self, tipo_campana):
        campana_qs = Campana.objects.filter(type=tipo_campana)
        campana_activas = campana_qs.filter(estado=Campana.ESTADO_ACTIVA).count()
        if tipo_campana == Campana.TYPE_DIALER:
            total = campana_qs.filter(estado__in=[
                Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA, Campana.ESTADO_INACTIVA]
            ).count()
            campana_activas = round(campana_activas / total, 2) if total else 0
        return campana_activas

    def _get_campanas_activas(self):
        data = dict(
            zip(['inbound', 'dialer', 'manual', 'preview'],
                [key[0] for key in Campana.TYPES_CAMPANA])
        )
        for key, value in data.items():
            data[key] = self._cantidad_campanas_activas(value)
        return data

    def _get_agentes_estados(self):
        data = dict.fromkeys(['ready', 'oncall', 'pause'], 0)
        redis_connection = create_redis_connection()
        keys_agentes = redis_connection.keys('OML:AGENT:*')
        cant_agentes_actives = 0
        for key in keys_agentes:
            agente_info = redis_connection.hgetall(key)
            if agente_info['STATUS'].startswith('PAUSE'):
                data['pause'] += 1
                cant_agentes_actives += 1
            if agente_info['STATUS'] == 'ONCALL':
                data['oncall'] += 1
                cant_agentes_actives += 1
            if agente_info['STATUS'] == 'READY':
                data['ready'] += 1
                cant_agentes_actives += 1
            if agente_info['STATUS'] == 'RINGING':
                cant_agentes_actives += 1
        redis_stream_notifier = RedisStreamNotifier()
        redis_stream_notifier.send('auth_event', cant_agentes_actives)
        return data

    def _llamadas_contactadas(self):
        data = dict.fromkeys(['attended', 'failed'], 0)
        hoy = now()
        fecha_inicio = datetime_hora_minima_dia(hoy)
        fecha_fin = datetime_hora_maxima_dia(hoy)
        llamada_qs = LlamadaLog.objects.filter(time__range=(fecha_inicio, fecha_fin))
        data['attended'] = llamada_qs.filter(
            event__in=LlamadaLog.EVENTOS_INICIO_CONEXION_AGENTE).count()
        data['failed'] = llamada_qs.filter(
            event__in=LlamadaLog.EVENTOS_NO_CONEXION).count()
        return data

    def get(self, request):
        data = {}
        data['active_campaigns'] = self._get_campanas_activas()
        data['state_agents'] = self._get_agentes_estados()
        data['contacted_calls'] = self._llamadas_contactadas()
        return Response(data)


class AuditSupervisor(APIView):

    def post(self, request):
        data = request.data
        if 'date_start' in data and data['date_start']:
            filter_kwargs = {'datetime__date': data['date_start']}
        else:
            today = timezone.now().astimezone(timezone.get_current_timezone()).date()
            filter_kwargs = {'datetime__date': today}
        qs_crudevent = CRUDEvent.objects.filter(**filter_kwargs)\
            .exclude(event_type=CRUDEvent.UPDATE, changed_fields='null')
        qs_loginevent = LoginEvent.objects.filter(**filter_kwargs)
        qs_requestevent = RequestEvent.objects.filter(**filter_kwargs)
        crudevent = AuditSupervisorCRUDEventSerializer(qs_crudevent, many=True)
        loginevent = AuditSupervisorLoginEventSerializer(qs_loginevent, many=True)
        requestevent = AuditSupervisorRequestEventSerializer(qs_requestevent, many=True)
        data = crudevent.data + loginevent.data + requestevent.data
        json_list_sorted = sorted(
            data, key=lambda r: datetime.datetime.strptime(r["date"], "%Y-%m-%d %H:%M"))
        return Response(json_list_sorted)

    def get(self, request):
        today = timezone.now().astimezone(timezone.get_current_timezone()).date()
        filter_kwargs = {'datetime__date': today}
        qs_crudevent = CRUDEvent.objects.filter(**filter_kwargs)\
            .exclude(event_type=CRUDEvent.UPDATE, changed_fields='null')
        qs_loginevent = LoginEvent.objects.filter(**filter_kwargs)
        qs_requestevent = RequestEvent.objects.filter(**filter_kwargs)
        crudevent = AuditSupervisorCRUDEventSerializer(qs_crudevent, many=True)
        loginevent = AuditSupervisorLoginEventSerializer(qs_loginevent, many=True)
        requestevent = AuditSupervisorRequestEventSerializer(qs_requestevent, many=True)
        data = crudevent.data + loginevent.data + requestevent.data
        json_list_sorted = sorted(
            data, key=lambda r: datetime.datetime.strptime(r["date"], "%Y-%m-%d %H:%M"))
        return Response(json_list_sorted)
