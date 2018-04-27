# -*- coding: utf-8 -*-

"""Vistas de reportes para campañas de tipo entrantes"""

from __future__ import unicode_literals

from django.shortcuts import redirect
from django.views.generic import UpdateView

from ominicontacto_app.models import Campana

from ominicontacto_app.services.reporte_campana_calificacion import ReporteCampanaService
from ominicontacto_app.services.reporte_metadata_cliente import ReporteMetadataClienteService


class ExportaReporteCampanaView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la campana.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        service = ReporteCampanaService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class ExportaReporteFormularioVentaView(UpdateView):
    """
    Esta vista invoca a generar un csv de reporte de la la venta.
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        service = ReporteMetadataClienteService()
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)
