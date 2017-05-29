# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import RedirectView
from ominicontacto_app.forms import (
    BusquedaContactoForm, ContactoForm, ReporteForm, FormularioNuevoContacto,
    FormularioCampanaContacto, UpdateBaseDatosForm
)
from ominicontacto_app.models import (
    Campana, Queue, Contacto, AgenteProfile
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService

from ominicontacto_app.services.reporte_campana_calificacion import \
    ReporteCampanaService
from ominicontacto_app.services.estadisticas_campana import EstadisticasService
from ominicontacto_app.utiles import convert_fecha_datetime
from ominicontacto_app.services.reporte_agente import EstadisticasAgenteService
from ominicontacto_app.services.reporte_metadata_cliente import \
    ReporteMetadataClienteService
from ominicontacto_app.services.reporte_campana_pdf import \
    ReporteCampanaPDFService
from ominicontacto_app.services.reporte_llamadas_campana import \
    EstadisticasCampanaLlamadasService


import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaListView(ListView):
    """
    Esta vista lista los objetos Campana
    """

    template_name = 'campana/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaListView, self).get_context_data(
           **kwargs)
        context['inactivas'] = Campana.objects.obtener_inactivas().filter(
            type=Campana.TYPE_ENTRANTE)
        context['pausadas'] = Campana.objects.obtener_pausadas().filter(
            type=Campana.TYPE_ENTRANTE)
        context['activas'] = Campana.objects.obtener_activas().filter(
            type=Campana.TYPE_ENTRANTE)
        context['borradas'] = Campana.objects.obtener_borradas().filter(
            oculto=False, type=Campana.TYPE_ENTRANTE)
        return context


class CampanaDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Queue
    template_name = 'campana/delete_campana.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Eliminamos el registro de la tabla de asterisk en mysql
        servicio_asterisk = AsteriskService()
        servicio_asterisk.delete_cola_asterisk(self.object.queue_campana)
        # realizamos la eliminacion de la queue
        self.object.remover()
        # actualizamos el archivo de dialplan
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError, e:
            message = ("<strong>Operación Errónea!</strong> "
                       "No se pudo confirmar la creación del dialplan  "
                       "al siguiente error: {0}".format(e))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_list')


class BusquedaFormularioFormView(FormView):
    form_class = BusquedaContactoForm
    template_name = 'agente/formulario_busqueda_contacto.html'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
            campana.bd_contacto)
        return self.render_to_response(self.get_context_data(
            listado_de_contacto=listado_de_contacto))

    def get_context_data(self, **kwargs):
        context = super(BusquedaFormularioFormView, self).get_context_data(
            **kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def form_valid(self, form):
        filtro = form.cleaned_data.get('buscar')
        try:
            campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            listado_de_contacto = Contacto.objects.\
                contactos_by_filtro_bd_contacto(campana.bd_contacto, filtro)
        except Contacto.DoesNotExist:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))

        if listado_de_contacto:
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))
        else:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))


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
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class CampanaReporteListView(ListView):
    """
    Muestra un listado de contactos a los cuales se le enviaron o se estan
    por enviar mensajes de texto
    """
    template_name = 'reporte/reporte_campana_formulario.html'
    context_object_name = 'campana'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteListView, self).get_context_data(
            **kwargs)

        service = ReporteCampanaService()
        service_formulario = ReporteMetadataClienteService()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        service.crea_reporte_csv(campana)
        service_formulario.crea_reporte_csv(campana)
        context['campana'] = campana
        return context


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
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        url = service.obtener_url_reporte_csv_descargar(self.object)

        return redirect(url)


class CampanaReporteGrafico(FormView):

    template_name = 'campana/reporte_campana.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        graficos_estadisticas = service.general_campana(self.get_object(), hoy,
                                                        hoy_ahora)
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))

    def get_context_data(self, **kwargs):
        context = super(CampanaReporteGrafico, self).get_context_data(
            **kwargs)

        context['campana'] = self.get_object()
        return context

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasService()
        graficos_estadisticas = service.general_campana(
            self.get_object(), fecha_desde, fecha_hasta)
        service_pdf = ReporteCampanaPDFService()
        service_pdf.crea_reporte_pdf(self.get_object(), graficos_estadisticas)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))


class ExportaReportePDFView(UpdateView):
    """
    Esta vista invoca a generar un pdf de reporte de la campana
    """

    model = Campana
    context_object_name = 'campana'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = ReporteCampanaPDFService()
        url = service.obtener_url_reporte_pdf_descargar(self.object)
        return redirect(url)


class AgenteCampanaReporteGrafico(FormView):

    template_name = 'campana/reporte_agente.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasAgenteService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(), hoy,
                                                        hoy_ahora)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))

    def get_context_data(self, **kwargs):
        context = super(AgenteCampanaReporteGrafico, self).get_context_data(
            **kwargs)

        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        context['pk_campana'] = self.kwargs['pk_campana']

        context['agente'] = agente
        return context

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasAgenteService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(),
                                                        fecha_desde,
                                                        fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


class FormularioSeleccionCampanaFormView(FormView):
    form_class = FormularioCampanaContacto
    template_name = 'agente/seleccion_campana_form.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
        if not agente.campana_member.all():
            message = ("Este agente no esta asignado a ninguna campaña ")
            messages.warning(self.request, message)
        return super(FormularioSeleccionCampanaFormView,
                     self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
            campanas = [queue.queue_name.campana
                        for queue in agente.campana_member.all()]

        campana_choice = [(campana.id, campana.nombre) for campana in
                          campanas]
        return form_class(campana_choice=campana_choice,
                          **self.get_form_kwargs())

    def form_valid(self, form):
        campana = form.cleaned_data.get('campana')
        return HttpResponseRedirect(
            reverse('nuevo_contacto_campana',
                    kwargs={"pk_campana": campana}))

    def get_success_url(self):
        reverse('view_blanco')


class FormularioNuevoContactoFormView(FormView):
    form_class = FormularioNuevoContacto
    template_name = 'agente/nuevo_contacto_campana.html'

    def get_form(self, form_class):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        telefono = form.cleaned_data.get('telefono')

        datos = []
        nombres.remove('telefono')

        for nombre in nombres:
            campo = form.cleaned_data.get(nombre)
            datos.append(campo)
        contacto = Contacto.objects.create(
            telefono=telefono, datos=json.dumps(datos),
            bd_contacto=base_datos)
        agente = self.request.user.get_agente_profile()
        return HttpResponseRedirect(
            reverse('calificacion_formulario_update',
                    kwargs={"pk_campana": self.kwargs['pk_campana'],
                            "pk_contacto": contacto.pk,
                            "id_agente": agente.pk,
                            "wombat_id": 0}))

    def get_success_url(self):
        reverse('view_blanco')


class OcultarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    pattern_name = 'campana_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_list'))


class DesOcultarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    pattern_name = 'campana_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_list'))


def mostrar_campanas_borradas_ocultas_view(request):
    borradas = Campana.objects.obtener_borradas()
    data = {
        'borradas': borradas,
    }
    return render(request, 'campana/campanas_borradas.html', data)


class CampanaReporteQueueListView(FormView):
    """
    Esta vista lista los tiempo de llamadas de las camapans

    """

    template_name = 'campana/tiempos_llamadas.html'
    context_object_name = 'campanas'
    model = Campana
    form_class = ReporteForm


    def get(self, request, *args, **kwargs):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        campana_llamadas_service = EstadisticasCampanaLlamadasService()
        estadisticas = campana_llamadas_service.general_campana(hoy, hoy_ahora)
        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)

        campana_llamadas_service = EstadisticasCampanaLlamadasService()
        estadisticas = campana_llamadas_service.general_campana(fecha_desde, fecha_hasta)

        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))
