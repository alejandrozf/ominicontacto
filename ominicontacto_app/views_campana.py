# -*- coding: utf-8 -*-

"""Vista para administrar el modelo Campana de tipo entrantes"""

from __future__ import unicode_literals

import json
import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.base import RedirectView
from ominicontacto_app.forms import (
    BusquedaContactoForm, ContactoForm, ReporteForm, FormularioNuevoContacto,
    FormularioCampanaContacto, UpdateBaseDatosForm, CampanaSupervisorUpdateForm
)
from ominicontacto_app.models import (
    Campana, Queue, Contacto, AgenteProfile, SupervisorProfile
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService

from ominicontacto_app.services.reporte_campana_calificacion import \
    ReporteCampanaService
from ominicontacto_app.services.estadisticas_campana import EstadisticasService
from ominicontacto_app.utiles import convert_fecha_datetime, convertir_ascii_string
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
    Esta vista lista los objetos Campana de tipo Entrantes
    """

    template_name = 'campana/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaListView, self).get_context_data(
           **kwargs)
        campanas = Campana.objects.obtener_campanas_entrantes()
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated() and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_vista_by_user(campanas, user)

        context['inactivas'] = campanas.filter(estado=Campana.ESTADO_INACTIVA)
        context['pausadas'] = campanas.filter(estado=Campana.ESTADO_PAUSADA)
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
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
    """Vista para buscar un contacto dentro de una campana"""
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
    Vista muetra un listado de listado de las calificaciones de la campana y
    genera los reportes csv de gestion y de calificacion
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
    """Esta vista genera el reporte grafico de la campana"""

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
        # genera los reportes grafico de la campana
        graficos_estadisticas = service.general_campana(self.get_object(), hoy,
                                                        hoy_ahora)
        # generar el reporte pdf
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
        # generar el reporte grafico de acuerdo al periodo de fecha seleccionado
        service = EstadisticasService()
        graficos_estadisticas = service.general_campana(
            self.get_object(), fecha_desde, fecha_hasta)
        # genera el reporte pdf de la campana
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
    """Esta vista genera el reporte grafico de la campana para un agente"""
    template_name = 'campana/reporte_agente.html'
    context_object_name = 'campana'
    model = Campana
    form_class = ReporteForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get(self, request, *args, **kwargs):
        service = EstadisticasAgenteService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        # generar el reporte para el agente de la campana
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
        # genera el reporte para el agente de esta campana
        service = EstadisticasAgenteService()
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        graficos_estadisticas = service.general_campana(agente,
                                                        self.get_object(),
                                                        fecha_desde,
                                                        fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas))


class FormularioSeleccionCampanaFormView(FormView):
    """Vista para seleccionar una campana a la cual se le agregar un nuevo contacto"""
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

    def get_form(self):
        self.form_class = self.get_form_class()
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
            campanas = [queue.queue_name.campana
                        for queue in agente.campana_member.all()]

        campana_choice = [(campana.id, campana.nombre) for campana in
                          campanas]
        return self.form_class(campana_choice=campana_choice,   **self.get_form_kwargs())

    def form_valid(self, form):
        campana = form.cleaned_data.get('campana')
        return HttpResponseRedirect(
            reverse('nuevo_contacto_campana',
                    kwargs={"pk_campana": campana}))

    def get_success_url(self):
        reverse('view_blanco')


class FormularioNuevoContactoFormView(FormView):
    """Esta vista agrega un nuevo contacto para la campana seleccionada"""
    form_class = FormularioNuevoContacto
    template_name = 'agente/nuevo_contacto_campana.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        telefono = form.cleaned_data.get('telefono')

        datos = []
        nombres.remove('telefono')

        for nombre in nombres:
            campo = form.cleaned_data.get(convertir_ascii_string(nombre))
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


class CampanaReporteQueueListView(FormView):
    """
    Esta vista lista los tiempo de llamadas de las campanas
    """

    template_name = 'campana/tiempos_llamadas.html'
    context_object_name = 'campanas'
    model = Campana
    form_class = ReporteForm

    def get(self, request, *args, **kwargs):
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        campana_llamadas_service = EstadisticasCampanaLlamadasService()
        estadisticas = campana_llamadas_service.general_campana(hoy, hoy_ahora,
                                                                request.user)
        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)

        campana_llamadas_service = EstadisticasCampanaLlamadasService()
        estadisticas = campana_llamadas_service.general_campana(fecha_desde, fecha_hasta,
                                                                self.request.user)

        return self.render_to_response(self.get_context_data(
            estadisticas=estadisticas))


def campana_json_view(request, pk_campana):
    """Esta vista devuelve un json con datos de la campana"""
    campana = Campana.objects.get(pk=pk_campana)
    nombre_interacion = 'SITIO_EXTERNO'
    if campana.tipo_interaccion is Campana.FORMULARIO:
        nombre_interacion = 'FORMULARIO'
    url_sitio_externo = None
    if campana.sitio_externo:
        url_sitio_externo = campana.sitio_externo.url
    repuesta = {
        'campana': campana.nombre,
        'pk_campana': campana.pk,
        'tipo_interaccion': campana.tipo_interaccion,
        'nombre_interacion': nombre_interacion,
        'url_sitio_externo': url_sitio_externo
    }
    response = JsonResponse(repuesta)
    return response


class CampanaSupervisorUpdateView(UpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    template_name = 'campana_dialer/campana_supervisors.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaSupervisorUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self):
        self.form_class = self.get_form_class()
        supervisores = SupervisorProfile.objects.all()
        supervisors_choices = [(supervisor.user.pk, supervisor.user) for supervisor in
                               supervisores]
        return self.form_class(supervisors_choices=supervisors_choices,
                               **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('campana_list')
