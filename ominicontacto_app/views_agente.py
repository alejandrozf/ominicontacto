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

# Vista relacionada al Agente

from __future__ import unicode_literals

import datetime
import logging as _logging

from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.views.generic import FormView, TemplateView, UpdateView, View

from django.views.generic.base import RedirectView

from ominicontacto_app.forms.base import ReporteForm, UpdateAgentPasswordForm
from ominicontacto_app.models import (
    AgenteEnContacto, AgenteProfile, CalificacionCliente, Campana, Contacto
)

from ominicontacto_app.services.click2call import Click2CallOriginator

from ominicontacto_app.services.reporte_agente_calificacion import ReporteAgenteService

from ominicontacto_app.services.reporte_agente_venta import ReporteFormularioVentaService


from ominicontacto_app.utiles import convert_fecha_datetime, fecha_hora_local


logger = _logging.getLogger(__name__)


class AgenteReporteCalificaciones(FormView):
    """Vista que muestra reporte de las calificaciones de las llamadas"""
    template_name = 'agente/reporte_agente_calificaciones.html'
    context_object_name = 'agente'
    model = AgenteProfile
    form_class = ReporteForm

    def dispatch(self, request, *args, **kwargs):
        self.agente = request.user.get_agente_profile()
        if not self.agente.grupo.acceso_calificaciones_agente:
            raise PermissionDenied
        return super(AgenteReporteCalificaciones, self).dispatch(
            request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.agente

    def get_context_data(self, **kwargs):
        context = super(AgenteReporteCalificaciones, self).get_context_data(**kwargs)
        context['agente'] = self.agente
        return context

    def get(self, request, *args, **kwargs):
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = self.agente
        # Crear reporte csv para las calficaciones no interesada(no gestion) y gestion
        service.crea_reporte_csv(agente, hoy, hoy_ahora)
        service_formulario.crea_reporte_csv(agente, hoy, hoy_ahora)
        fecha_desde = fecha_hora_local(datetime.datetime.combine(hoy, datetime.time.min))
        fecha_hasta = fecha_hora_local(datetime.datetime.combine(hoy_ahora, datetime.time.max))
        listado_calificaciones = agente.calificaciones.filter(modified__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        resultado = form.cleaned_data.get('resultado_auditoria')
        service = ReporteAgenteService()
        service_formulario = ReporteFormularioVentaService()
        agente = self.agente
        # Crear reporte csv para las calficaciones no interesada(no gestion) y gestion
        # de acuerdo al periodo de fecha seleccionado
        if not resultado == ReporteForm.TODOS_RESULTADOS:
            service.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
            service_formulario.crea_reporte_csv(agente, fecha_desde, fecha_hasta)
        else:
            service.crea_reporte_csv(agente, fecha_desde, fecha_hasta, resultado=resultado)
            service_formulario.crea_reporte_csv(agente, fecha_desde, fecha_hasta,
                                                resultado=resultado)
        fecha_desde = fecha_hora_local(datetime.datetime.combine(fecha_desde, datetime.time.min))
        fecha_hasta = fecha_hora_local(datetime.datetime.combine(fecha_hasta, datetime.time.max))
        listado_calificaciones = agente.calificaciones.filter(modified__range=(
            fecha_desde, fecha_hasta))
        if not resultado == ReporteForm.TODOS_RESULTADOS:
            listado_calificaciones = listado_calificaciones.filter(
                auditoriacalificacion__resultado=resultado)
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones))


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


class DashboardAgenteView(TemplateView):
    """Vista que renderiza el dashboard con los datos diarios del agente
    """
    template_name = 'agente/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardAgenteView, self).get_context_data(**kwargs)
        context['agente_id'] = self.request.user.get_agente_profile().pk
        return context

    def dispatch(self, request, *args, **kwargs):
        agent_profile = request.user.get_agente_profile()
        agent_group = agent_profile.grupo
        if agent_group.acceso_dashboard_agente:
            return super(DashboardAgenteView, self).dispatch(
                request, *args, **kwargs)
        else:
            raise PermissionDenied


class LlamarContactoView(RedirectView):
    """
    Esta vista realiza originate hacia Asterisk para llamar dentro de una campaña
    TODO: Eliminar esta vista y utilizar la API actualizandola para tener en cuenta todos los casos.
    """

    pattern_name = 'view_blanco'

    def post(self, request, *args, **kwargs):
        # TODO: Analizar bien el caso de que se este agregando un contacto
        # TODO: DEJAR DE MANDAR pk_agente
        # TODO: DEJAR DE MANDAR tipo_campana
        agente = self.request.user.get_agente_profile()
        click2call_type = request.POST.get('click2call_type', 'false')
        campana_id = request.POST.get('pk_campana')
        telefono = request.POST.get('telefono', '')

        # Patch: Para deectar que hubo un error cuando se le pega por AJAX...
        self.no_redirect = request.POST.get('404_on_error')

        # Si el pk es 0 es porque no se quiere identificar al contacto.
        # El tipo de click2call no será "preview".
        contacto_id = request.POST['pk_contacto']
        if not contacto_id == '-1':
            try:
                contacto = Contacto.objects.get(pk=contacto_id)
            except Contacto.DoesNotExist:
                message = _(
                    u'No es posible llamar al contacto. No se pudo identificar al contacto.')
                return self.error_return_value('view_blanco', message)

        if not telefono:
            if not contacto:
                message = _(
                    u'No es posible llamar al contacto. No se pudo identificar un teléfono.')
                return self.error_return_value('view_blanco', message)
            telefono = contacto.telefono

        if campana_id == '':
            calificacion_cliente = CalificacionCliente.objects.filter(
                contacto=contacto, agente=agente).order_by('-fecha')
            if calificacion_cliente.exists():
                campana = calificacion_cliente[0].campana
                campana_id = str(campana.pk)
                tipo_campana = str(campana.type)
        else:
            try:
                campana = Campana.objects.obtener_actuales().get(id=campana_id)
            except Campana.DoesNotExist:
                message = _(
                    u'No es posible llamar al contacto.'
                    ' La campaña no se encuentra activa o no existe en el sistema.')
                return self.error_return_value('view_blanco', message)
            campana_id = str(campana.pk)
            tipo_campana = str(campana.type)

            if click2call_type == 'preview':
                asignado = AgenteEnContacto.asignar_contacto(contacto.id, campana.pk, agente)
                if not asignado:
                    message = _(u'No es posible llamar al contacto.'
                                ' Para poder llamar un contacto debe obtenerlo'
                                ' desde el menu de Campañas Preview.'
                                ' Asegurese de no haber perdido la reserva')
                    return self.error_return_value('campana_preview_activas_miembro', message)

        originator = Click2CallOriginator()
        originator.call_originate(
            agente, campana_id, tipo_campana, contacto_id, telefono, click2call_type)
        return HttpResponseRedirect(reverse('view_blanco'))

    def error_return_value(self, view_name, message):
        if self.no_redirect:
            raise Http404(message)
        else:
            messages.warning(self.request, message)
            return HttpResponseRedirect(reverse(view_name))


class LlamarFueraDeCampanaView(RedirectView):
    """
    Esta vista realiza originate hacia Asterisk para llamar por fuera de una campaña
    """

    pattern_name = 'view_blanco'

    def post(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        tipo_destino = request.POST.get('tipo_destino')
        destino = request.POST.get('destino', '')

        originator = Click2CallOriginator()
        if tipo_destino == Click2CallOriginator.AGENT:
            try:
                agente_destino = AgenteProfile.objects.get(id=destino)
            except AgenteProfile.DoesNotExist:
                # TODO: Deberia devolver json con error de agente incorrecto?
                pass
            else:
                originator.call_agent(agente, agente_destino)
        elif tipo_destino == Click2CallOriginator.EXTERNAL:
            # TODO: Validar destino como un numero valido?
            originator.call_external(agente, destino)
        else:
            # TODO: Devolver Json con error de tipo destino incorrecto?
            pass

        return HttpResponseRedirect(reverse('view_blanco'))


class LiberarContactoAsignado(View):
    """
    Libera un contacto Asignado en AgenteEnContacto
    """
    def post(self, request, *args, **kwargs):
        # TODO: Validar que el supervisor tiene permisos sobre la campaña
        campana_id = request.POST.get('campana_id')
        agente = request.user.get_agente_profile()
        status, ___ = AgenteEnContacto.liberar_contacto(agente.id, campana_id)
        if status:
            return JsonResponse({'status': 'OK'})
        else:
            return JsonResponse({'status': 'ERROR'})


class AgenteCampanasPreviewActivasView(TemplateView):
    """
    Campañas previews activas de las cuales es miembro un agente
    """
    template_name = 'agente/campanas_preview.html'

    def dispatch(self, request, *args, **kwargs):
        agente_profile = self.request.user.get_agente_profile()
        if not agente_profile.grupo.acceso_campanas_preview_agente:
            raise PermissionDenied
        return super(AgenteCampanasPreviewActivasView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AgenteCampanasPreviewActivasView, self).get_context_data(*args, **kwargs)
        agente_profile = self.request.user.get_agente_profile()
        campanas_preview_activas = agente_profile.get_campanas_preview_activas_miembro()
        context['campanas_preview_activas'] = campanas_preview_activas.values_list(
            'queue_name__campana', 'queue_name__campana__nombre')
        context['get_contact'] = kwargs.get('get_contact') is not None
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


class UpdateAgentPasswordView(UpdateView):
    """Vista para actualizar la contrasena de un agente"""
    model = AgenteProfile
    form_class = UpdateAgentPasswordForm
    template_name = 'agente/update_agent_password.html'

    def get_object(self):
        agente_profile = self.request.user.get_agente_profile()
        return agente_profile

    def form_valid(self, form):
        self.object = form.save()
        if form['password1'].value():
            agente = self.request.user.get_agente_profile()
            agente.user.set_password(form['password1'].value())
            agente.user.save()
        messages.success(self.request,
                         _('El usuario fue actualizado correctamente'))
        return super(UpdateAgentPasswordView, self).form_valid(form)

    def get_success_url(self):
        return reverse('consola_de_agente')
