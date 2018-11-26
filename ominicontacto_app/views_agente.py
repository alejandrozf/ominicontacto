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

"""
Vista relacionada al Agente
"""

from __future__ import unicode_literals

import datetime
from django.views.generic import FormView, UpdateView, TemplateView, View
from django.views.generic.base import RedirectView
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from ominicontacto_app.models import (
    AgenteProfile, Contacto, CalificacionCliente, Campana, AgenteEnContacto
)
from ominicontacto_app.forms import ReporteForm
from ominicontacto_app.services.reporte_agente_calificacion import ReporteAgenteService
from ominicontacto_app.services.reporte_agente_venta import ReporteFormularioVentaService
from ominicontacto_app.utiles import convert_fecha_datetime
from ominicontacto_app.services.asterisk_ami_http import (
    AsteriskHttpClient, AsteriskHttpOriginateError
)
import logging as _logging


logger = _logging.getLogger(__name__)


class AgenteReporteCalificaciones(FormView):
    """Vista que muestra reporte de las calificaciones de las llamadas"""
    template_name = 'agente/reporte_agente_calificaciones.html'
    context_object_name = 'agente'
    model = AgenteProfile
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        # Crear reporte csv para las calficaciones no interesada(no gestion) y gestion
        service.crea_reporte_csv(agente, hoy, hoy_ahora)
        service_formulario.crea_reporte_csv(agente, hoy, hoy_ahora)
        fecha_desde = datetime.datetime.combine(hoy, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(hoy_ahora, datetime.time.max)
        listado_calificaciones = agente.calificaciones.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        # Crear reporte csv para las calficaciones no interesada(no gestion) y gestion
        # de acuerdo al periodo de fecha seleccionado
        service.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
        service_formulario.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        listado_calificaciones = agente.calificaciones.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente))


class ExportaReporteFormularioVentaView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la la venta.
    """

    model = AgenteProfile
    context_object_name = 'agente'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteFormularioVentaService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class ExportaReporteCalificacionView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de las calificaciones.
    """

    model = AgenteProfile
    context_object_name = 'agente'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteAgenteService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


def cambiar_estado_agente_view(request):
    # TODO: Debería ser por POST
    """Vista GET para cambiar el estado del agente"""
    pk_agente = request.GET['pk_agente']
    estado = request.GET['estado']
    agente = AgenteProfile.objects.get(pk=int(pk_agente))
    agente.estado = int(estado)
    agente.save()
    response = JsonResponse({'status': 'OK'})
    return response


def logout_view(request):
    """Vista para desloguear el agente de django y de asterisk"""
    if request.user.is_agente and request.user.get_agente_profile():
        agente = request.user.get_agente_profile()
        variables = {
            'AGENTE': str(agente.sip_extension),
            'AGENTNAME': "{0}_{1}".format(agente.id, request.user.get_full_name())
        }
        # Deslogueo el agente de asterisk via AMI
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate("Local/066LOGOUT@oml-agent-actions/n", "oml-agent-actions", True,
                             variables, True, aplication='Hangup')

        except AsteriskHttpOriginateError:
            logger.exception("Originate failed - agente: %s ", agente)

        except Exception as e:
            logger.exception("Originate failed {0} - agente: {1}".format(e, agente))
    logout(request)
    return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


class LlamarContactoView(RedirectView):
    """
    Esta vista realiza originate hacia wombate
    """

    pattern_name = 'view_blanco'

    def _call_originate(self, request, campana_id, campana_nombre, agente, contacto,
                        click2call_type, tipo_campana):
        variables = {
            'IdCamp': str(campana_id),
            'codCli': str(contacto.pk),
            'CAMPANA': campana_nombre,
            'origin': click2call_type,
            'Tipocamp': tipo_campana,
            'FTSAGENTE': "{0}_{1}".format(agente.id,
                                          request.user.get_full_name())
        }
        channel = "Local/{0}@click2call/n".format(agente.sip_extension)
        # Genero la llamada via originate por AMI
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate(channel, "from-internal", False, variables, True,
                             exten=contacto.telefono, priority=1, timeout=45000)

        except AsteriskHttpOriginateError:
            logger.exception("Originate failed - contacto: %s ", contacto.telefono)

        except Exception as e:
            logger.exception("Originate failed by {0} - contacto: {1}".format(e, contacto.telefono))

    def post(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=request.POST['pk_agente'])
        contacto = Contacto.objects.get(pk=request.POST['pk_contacto'])
        click2call_type = request.POST.get('click2call_type', 'false')
        tipo_campana = request.POST.get('tipo_campana')
        campana_id = request.POST.get('pk_campana')
        campana_nombre = request.POST.get('campana_nombre')

        if campana_id == '':
            calificacion_cliente = CalificacionCliente.objects.filter(
                contacto=contacto, agente=agente).order_by('-fecha')
            if calificacion_cliente.exists():
                campana = calificacion_cliente[0].campana
                campana_id = str(campana.pk)
                campana_nombre = campana.nombre
                tipo_campana = str(campana.type)

        elif click2call_type == 'preview':
            asignado = AgenteEnContacto.asignar_contacto(contacto.id, campana_id, agente)
            if not asignado:
                message = _(u'No es posible llamar al contacto.'
                            ' Para poder llamar un contacto debe obtenerlo'
                            ' desde el menu de Campañas Preview.'
                            ' Asegurese de no haber perdido la reserva')
                messages.warning(self.request, message)
                return HttpResponseRedirect(
                    reverse('agenda_agente_list'))

        self._call_originate(
            request, campana_id, campana_nombre, agente, contacto, click2call_type, tipo_campana)
        return super(LlamarContactoView, self).post(request, *args, **kwargs)


class LiberarContactoAsignado(View):
    """
    Libera un contacto Asignado en AgenteEnContacto
    """
    def post(self, request, *args, **kwargs):
        # TODO: Validar que el supervisor tiene permisos sobre la campaña
        campana_id = request.POST.get('campana_id')
        agente = request.user.get_agente_profile()
        if AgenteEnContacto.liberar_contacto(agente.id, campana_id):
            return JsonResponse({'status': 'OK'})
        else:
            return JsonResponse({'status': 'ERROR'})


class AgenteCampanasPreviewActivasView(TemplateView):
    """
    Campañas previews activas de las cuales es miembro un agente
    """
    template_name = 'agente/campanas_preview.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AgenteCampanasPreviewActivasView, self).get_context_data(*args, **kwargs)
        agente_profile = self.request.user.get_agente_profile()
        campanas_preview_activas = agente_profile.get_campanas_preview_activas_miembro()
        context['campanas_preview_activas'] = campanas_preview_activas.values_list(
            'queue_name__campana', 'queue_name__campana__nombre')
        return context


class CampanasActivasView(View):
    """
    Devuelve un JSON con información de las campañas activas del sistema
    """
    def get(self, request):
        campanas_activas = Campana.objects.obtener_activas().values('id', 'nombre', 'type')
        return JsonResponse(data={'campanas': list(campanas_activas)})


class AgentesLogueadosCampana(View):
    """
    Devuelve un JSON con la información de los agentes logueados por campaña
    """
    # TODO: pasar este servicio a DRF si es posible
    def _get_all_logged_in_users(self, campana_id):
        # devuelve las sesiones que aún no han expirado
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []
        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id', False)
            if user_id and user_id not in uid_list:
                uid_list.append(user_id)

        # encuentra todos los agentes a partir los uids encontrados y la campaña
        return AgenteProfile.objects.filter(
            user__id__in=uid_list, campana_member__queue_name__campana__pk=campana_id).distinct()

    def _parsear_agentes_profiles(self, agentes_profiles):
        for agente_profile in agentes_profiles:
            agente_profile['username'] = agente_profile.pop('user__username')
            agente_profile['user_id'] = agente_profile.pop('user__id')
            agente_profile['grupo_id'] = agente_profile.pop('grupo__id')
        return agentes_profiles

    def get(self, request, *args, **kwargs):
        campana_id = kwargs.get('campana_id', False)
        agentes_profiles = self._get_all_logged_in_users(campana_id).values(
            'id', 'user__username', 'sip_extension', 'user__id', 'grupo__id')
        agentes_profiles_result = self._parsear_agentes_profiles(agentes_profiles)
        return JsonResponse(data={'agentes': list(agentes_profiles_result)})


class AgentesDeGrupoPropioView(View):
    """
    Devuelve un JSON con información de los agentes pertenecientes al grupo del agente
    """
    def get(self, request):
        agente_profile = self.request.user.get_agente_profile()
        agentes_del_grupo = agente_profile.grupo.agentes.obtener_activos() \
            .exclude(id=agente_profile.id)
        data_agentes = agentes_del_grupo.annotate(
            full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name'))) \
            .values('id', 'full_name', 'sip_extension')
        return JsonResponse(data={'agentes': list(data_agentes)})
