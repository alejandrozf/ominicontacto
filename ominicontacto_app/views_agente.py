# -*- coding: utf-8 -*-

"""
Vista relacionada al Agente
"""

from __future__ import unicode_literals

import datetime
from django.views.generic import FormView, UpdateView, ListView
from django.views.generic.base import RedirectView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ominicontacto_app.models import (
    AgenteProfile, Contacto, CalificacionCliente, Grupo
)
from ominicontacto_app.forms import ReporteForm, ReporteAgenteForm
from ominicontacto_app.services.reporte_agente_calificacion import \
    ReporteAgenteService
from ominicontacto_app.services.reporte_agente_venta import \
    ReporteFormularioVentaService
from ominicontacto_app.utiles import convert_fecha_datetime
from ominicontacto_app.services.reporte_llamadas import EstadisticasService
from django.http import JsonResponse
from django.contrib.auth import logout
from django.conf import settings
from ominicontacto_app.services.asterisk_ami_http import (
    AsteriskHttpClient, AsteriskHttpOriginateError
)
from ominicontacto_app.services.reporte_llamada_csv import ReporteAgenteCSVService
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
        calificaciones_manuales = agente.calificacionesmanuales.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente,
            calificaciones_manuales=calificaciones_manuales))

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
        calificaciones_manuales = agente.calificacionesmanuales.filter(fecha__range=(
            fecha_desde, fecha_hasta))
        return self.render_to_response(self.get_context_data(
            listado_calificaciones=listado_calificaciones, agente=agente,
            calificaciones_manuales=calificaciones_manuales))


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
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
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
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class AgenteReporteListView(FormView):
    """
    Esta vista lista los tiempo de los agentes

    """

    template_name = 'agente/tiempos.html'
    context_object_name = 'agentes'
    model = AgenteProfile
    form_class = ReporteAgenteForm

    # def get_context_data(self, **kwargs):
    #     context = super(AgenteReporteListView, self).get_context_data(
    #        **kwargs)
    #     agente_service = EstadisticasService()
    #     context['estadisticas'] = agente_service._calcular_estadisticas()
    #     return context

    def get(self, request, *args, **kwargs):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente_service = EstadisticasService()
        agentes = []
        graficos_estadisticas = agente_service.general_campana(hoy, hoy_ahora, agentes,
                                                               request.user)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        grupo_id = form.cleaned_data.get('grupo_agente')
        agentes_pk = form.cleaned_data.get('agente')
        agentes = []
        if agentes_pk:
            for agente_pk in agentes_pk:
                agente = AgenteProfile.objects.get(pk=agente_pk)
                agentes.append(agente)
        if grupo_id:
            grupo = Grupo.objects.get(pk=int(grupo_id))
            agentes = grupo.agentes.all()
        #agentes = ["{0}_{1}".format(agente.id, agente.user.get_full_name())
         #          for agente in agentes]
        agente_service = EstadisticasService()
        graficos_estadisticas = agente_service.general_campana(
            fecha_desde, fecha_hasta, agentes, self.request.user)

        service_csv = ReporteAgenteCSVService()
        service_csv.crea_reporte_csv(graficos_estadisticas)

        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


def cambiar_estado_agente_view(request):
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
            client.originate("Local/066LOGOUT@fts-pausas/n", "ftp-pausas", True,
                             variables, True, aplication='Hangup')

        except AsteriskHttpOriginateError:
            logger.exception("Originate failed - agente: %s ", agente)

        except:
            logger.exception("Originate failed - agente: %s ", agente)
    logout(request)
    return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


class LlamarContactoView(RedirectView):
    """
    Esta vista realiza originate hacia wombate
    """

    pattern_name = 'view_blanco'

    def post(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=request.POST['pk_agente'])
        contacto = Contacto.objects.get(pk=request.POST['pk_contacto'])
        calificacion_cliente = CalificacionCliente.objects.filter(
            contacto=contacto, agente=agente).order_by('-fecha')
        campana_id = 0
        campana_nombre = "None"
        if calificacion_cliente > 0:
            campana_id = calificacion_cliente[0].campana.pk
            campana_nombre = calificacion_cliente[0].campana.nombre
        variables = {
            'IdCamp': str(campana_id),
            'codCli': str(contacto.pk),
            'CAMPANA': campana_nombre,
            'origin': 'click2call'
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

        except:
            logger.exception("Originate failed - contacto: %s ", contacto.telefono)
        return super(LlamarContactoView, self).post(request, *args, **kwargs)


def exporta_reporte_agente_llamada_view(request, tipo_reporte):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """
    service = service_csv = ReporteAgenteCSVService()
    url = service.obtener_url_reporte_csv_descargar(tipo_reporte)
    return redirect(url)


class DesactivarAgenteView(RedirectView):
    """
    Esta vista actualiza el agente desactivandolo
    """

    pattern_name = 'agente_list'

    def get(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        agente.desactivar()
        return HttpResponseRedirect(reverse('agente_list'))


class ActivarAgenteView(RedirectView):
    """
    Esta vista actualiza el agente activandolo
    """

    pattern_name = 'agente_list'

    def get(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        agente.activar()
        return HttpResponseRedirect(reverse('agente_list'))
