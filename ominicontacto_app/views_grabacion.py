# -*- coding: utf-8 -*-

"""
Aca se encuentran las vistas relacionada con las grabaciones en cuanto a su busqueda
ya que el insert lo hace kamailio/asterisk(hablar con fabian como hace el insert )
"""

import datetime
import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView
from django.core import paginator as django_paginator
from ominicontacto_app.forms import (
    GrabacionBusquedaForm, GrabacionReporteForm
)
from ominicontacto_app.models import (
    Grabacion, Campana
)
from ominicontacto_app.services.reporte_grafico import GraficoService
from utiles import convert_fecha_datetime, UnicodeWriter
from ominicontacto_app.services.reporte_campana_csv import (ReporteCampanaCSVService,
                                                            obtener_datos_total_llamadas_csv,
                                                            obtener_llamadas_campanas)


class BusquedaGrabacionFormView(FormView):
    """Vista que realiza la busqeda de las grabaciones"""
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
        return self.render_to_response(
            self.get_context_data(
                listado_de_grabaciones=Grabacion.objects.
                grabacion_by_fecha_intervalo_campanas(hoy, hoy, campanas),
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


class GrabacionReporteFormView(FormView):
    """Vista que despliega reporte de las grabaciones de las llamadas"""
    template_name = 'grabaciones/total_llamadas.html'
    context_object_name = 'grabacion'
    model = Grabacion
    form_class = GrabacionReporteForm

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        graficos_estadisticas = service.general_llamadas_hoy(
            hoy, hoy_ahora, request.user, False)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta, final_dia=True)
        finalizadas = form.cleaned_data.get('finalizadas')
        # obtener_estadisticas_render_graficos_supervision()
        service = GraficoService()
        graficos_estadisticas = service.general_llamadas_hoy(
            fecha_desde, fecha_hasta, self.request.user, finalizadas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


def exporta_reporte_grabacion_llamada_view(request, tipo_reporte):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """
    service = ReporteCampanaCSVService()
    url = service.obtener_url_reporte_csv_descargar(tipo_reporte)
    return redirect(url)


def obtener_filas_reporte(tipo_reporte, datos_reporte):
    if tipo_reporte == 'total_llamadas':
        encabezado = ["Total llamadas", "Cantidad"]
        return obtener_datos_total_llamadas_csv(encabezado, datos_reporte)
    if tipo_reporte in ['llamadas_campanas_entrantes', 'llamadas_campanas_dialer',
                        'llamadas_campanas_manuales']:
        encabezado = ["Campana", "Recibidas", "Atendidas", "Expiradas", "Abandonadas"]
        return obtener_llamadas_campanas(encabezado, datos_reporte)
    if tipo_reporte == "llamadas_campanas":
        encabezado = ["Total llamadas", "Cantidad", "Tipo de campaña"]
        return obtener_llamadas_campanas(encabezado, datos_reporte)


def exportar_llamadas(request, tipo_reporte):
    """
    Realiza el reporte a formato .csv del reporte recibido como parámetro
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(tipo_reporte)
    writer = UnicodeWriter(response)
    datos_json = request.POST.get(tipo_reporte, False)

    if datos_json:
        datos_reporte = json.loads(datos_json)
        filas_csv = obtener_filas_reporte(tipo_reporte, datos_reporte)
        writer.writerows(filas_csv)
    else:
        writer.writerow(['No hay datos disponibles para este reporte'])

    return response
