# -*- coding: utf-8 -*-

"""Vista para reportes de campana dialer"""

from __future__ import unicode_literals

from django.shortcuts import redirect, render
from ominicontacto_app.models import Campana, OpcionCalificacion
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.reporte_llamados_contactados_csv import ReporteCampanaContactadosCSV


class ExportaReporteNoAtendidosView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "no_atendidos")

        return redirect(url)


class ExportaReporteCalificadosView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "calificados")

        return redirect(url)


class ExportaReporteContactadosView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_csv = ReporteCampanaContactadosCSV()
        url = service_csv.obtener_url_reporte_csv_descargar(
            self.object, "contactados")

        return redirect(url)


class CampanaDialerDetailView(DetailView):
    """Detalle de una campana dialer"""
    template_name = 'campana_dialer/detalle.html'
    model = Campana
    context_object_name = 'campana'

    def get_context_data(self, **kwargs):
        context = super(
            CampanaDialerDetailView, self).get_context_data(**kwargs)
        campana = self.get_object()
        campana_service = CampanaService()
        estados_running_wombat = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                                  Campana.ESTADO_FINALIZADA]
        opciones_calificacion = campana.opciones_calificacion.all()
        context['opciones_calificacion'] = opciones_calificacion.values('nombre')
        context['opciones_calificacion_gestion'] = opciones_calificacion.filter(
            tipo=OpcionCalificacion.GESTION).values('nombre')
        if campana.estado in estados_running_wombat:
            dato_campana = campana_service.obtener_dato_campana_run(campana)
            if dato_campana:
                status = campana_service.obtener_status_campana_running(
                    dato_campana['hoppercampId'])
                context['efectuadas'] = dato_campana['n_calls_attempted']
                context['terminadas'] = dato_campana['n_calls_completed']
                context['estimadas'] = dato_campana['n_est_remaining_calls']
                context['status'] = status
                context['resultado'] = True
            else:
                context['resultado'] = False
        return context

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])


def detalle_campana_dialer_view(request):
    """Vista que muestrar el detalle de campana en wombat"""
    pk_campana = int(request.GET['pk_campana'])
    campana = Campana.objects.get(pk=pk_campana)
    campana_service = CampanaService()
    dato_campana = campana_service.obtener_dato_campana_run(campana)
    status = campana_service.obtener_status_campana_running(
        dato_campana['hoppercampId'])
    data = {
        'campana': campana,
        'efectuadas': dato_campana['n_calls_attempted'],
        'terminadas': dato_campana['n_calls_completed'],
        'estimadas': dato_campana['n_est_remaining_calls'],
        'status': status

    }
    return render(request, 'campana_dialer/detalle_campana.html', data)
