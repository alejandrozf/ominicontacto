# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import CampanaDialer
from django.views.generic import ListView
from ominicontacto_app.services.reporte_metadata_cliente import \
    ReporteMetadataClienteService
from ominicontacto_app.services.reporte_campana_calificacion import \
    ReporteCampanaService


class CampanaDialerReporteCalificacionListView(ListView):
    """
    Muestra un listado de contactos a los cuales se los calificaron
    """
    template_name = 'reporte/reporte_campana_formulario.html'
    context_object_name = 'campana'
    model = CampanaDialer

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerReporteCalificacionListView, self).get_context_data(
            **kwargs)

        service = ReporteCampanaService()
        service_formulario = ReporteMetadataClienteService()
        campana = CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])
        service.crea_reporte_csv(campana)
        service_formulario.crea_reporte_csv(campana)
        context['campana'] = campana
        return context