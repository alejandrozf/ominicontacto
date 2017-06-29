# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic import FormView, ListView
from django.core import paginator as django_paginator
from ominicontacto_app.forms import (
    GrabacionBusquedaForm, GrabacionReporteForm
)
from ominicontacto_app.models import (
    Grabacion, Campana
)
from ominicontacto_app.services.reporte_grafico import GraficoService
from utiles import convert_fecha_datetime


class BusquedaGrabacionFormView(FormView):
    form_class = GrabacionBusquedaForm
    template_name = 'busqueda_grabacion.html'

    def get_context_data(self, **kwargs):
        context = super(BusquedaGrabacionFormView, self).get_context_data(
            **kwargs)

        listado_de_grabaciones = []

        if 'listado_de_grabaciones' in context:
            listado_de_grabaciones = context['listado_de_grabaciones']

        qs = listado_de_grabaciones
         # ----- <Paginate> -----
        page = self.kwargs['pagina']
        if context['pagina']:
            page = context['pagina']
        result_paginator = django_paginator.Paginator(qs, 40)
        try:
            qs = result_paginator.page(page)
        except django_paginator.PageNotAnInteger:
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----
        context['listado_de_grabaciones'] = qs
        context['grabacion_url'] = settings.OML_GRABACIONES_URL
        return context

    def get(self, request, *args, **kwargs):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=Grabacion.objects.
                grabacion_by_fecha_intervalo(hoy, hoy, campanas),
            pagina=self.kwargs['pagina']))

    def get_form(self):
        self.form_class = self.get_form_class()
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        campana_choice = [(campana.pk, campana.nombre)
                          for campana in campanas]
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        tipo_llamada = form.cleaned_data.get('tipo_llamada')
        tel_cliente = form.cleaned_data.get('tel_cliente')
        sip_agente = form.cleaned_data.get('sip_agente')
        campana = form.cleaned_data.get('campana')
        campanas = Campana.objects.all()
        if self.request.user.get_is_supervisor_customer():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)
        pagina = form.cleaned_data.get('pagina')
        listado_de_grabaciones = Grabacion.objects.grabacion_by_filtro(
            fecha_desde, fecha_hasta, tipo_llamada, tel_cliente, sip_agente, campana,
        campanas)
        return self.render_to_response(self.get_context_data(
            listado_de_grabaciones=listado_de_grabaciones, pagina=pagina))


class GrabacionReporteListView(ListView):
    """
    Esta vista lista los objetos Capanas
    diferenciadas por sus estados actuales.
    Pasa un diccionario al template
    con las claves como estados.
    """

    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion

    def get_context_data(self, **kwargs):
        context = super(GrabacionReporteListView, self).get_context_data(
           **kwargs)

        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        context['graficos_estadisticas'] = service.general_llamadas_hoy(hoy,
            hoy_ahora)
        return context


class GrabacionReporteSemanaListView(ListView):
    """
    Esta vista lista los objetos Capanas
    diferenciadas por sus estados actuales.
    Pasa un diccionario al template
    con las claves como estados.
    """

    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion

    def get_context_data(self, **kwargs):
        context = super(GrabacionReporteSemanaListView, self).get_context_data(
           **kwargs)

        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        ultima_semana = hoy - datetime.timedelta(days=7)
        context['graficos_estadisticas'] = service.general_llamadas_hoy(
            ultima_semana, hoy_ahora)
        return context


class GrabacionReporteMesListView(ListView):
    """
    Esta vista lista los objetos Capanas
    diferenciadas por sus estados actuales.
    Pasa un diccionario al template
    con las claves como estados.
    """

    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion

    def get_context_data(self, **kwargs):
        context = super(GrabacionReporteMesListView, self).get_context_data(
           **kwargs)

        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        ultima_mes = hoy - datetime.timedelta(days=30)
        context['graficos_estadisticas'] = service.general_llamadas_hoy(
            ultima_mes, hoy_ahora)
        return context


class GrabacionReporteFormView(FormView):

    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion
    form_class = GrabacionReporteForm

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        graficos_estadisticas = service.general_llamadas_hoy(hoy, hoy_ahora)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        graficos_estadisticas = service.general_llamadas_hoy(fecha_desde,
                                                             fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))