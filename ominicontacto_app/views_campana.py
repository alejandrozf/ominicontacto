# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
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
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService


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
        context['inactivas'] = Campana.objects.obtener_inactivas()
        context['pausadas'] = Campana.objects.obtener_pausadas()
        context['activas'] = Campana.objects.obtener_activas()
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
        self.object.delete()
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


# FIXME eliminar prontamente esta vista
class ContactoFormularioUpdateView(UpdateView):
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = ContactoForm

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['id_cliente'])

    def get_success_url(self):
        return reverse('formulario_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.object.id_cliente})


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
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        fecha_desde, fecha_hasta = fecha.split('-')
        fecha_desde = convert_fecha_datetime(fecha_desde)
        fecha_hasta = convert_fecha_datetime(fecha_hasta)
        # obtener_estadisticas_render_graficos_supervision()
        service = EstadisticasService()
        graficos_estadisticas = service.general_campana(
            self.get_object(), fecha_desde, fecha_hasta)
        return self.render_to_response(self.get_context_data(
            graficos_estadisticas=graficos_estadisticas,
            pk_campana=self.kwargs['pk_campana']))


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
        id_cliente = form.cleaned_data.get('id_cliente')
        contacto = Contacto.objects.filter(id_cliente=int(id_cliente),
                                           bd_contacto=base_datos)
        if contacto.count() > 0:
            return self.form_invalid(form, id_cliente=id_cliente)
        datos = []
        for nombre in nombres:
            campo = form.cleaned_data.get(nombre)
            datos.append(campo)
        contacto = Contacto.objects.create(
            telefono=telefono, id_cliente=id_cliente, datos=json.dumps(datos),
            bd_contacto=base_datos)
        agente = self.request.user.get_agente_profile()
        return HttpResponseRedirect(
            reverse('calificacion_formulario_update',
                    kwargs={"pk_campana": self.kwargs['pk_campana'],
                            "id_cliente": contacto.id_cliente,
                            "id_agente": agente.pk,
                            "wombat_id": 0}))

    def form_invalid(self, form, id_cliente=None):

        message = '<strong>Operación Errónea!</strong> \
                  ya existe un cliente con este id_cliente. {0}'.format(
            id_cliente)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        reverse('view_blanco')


class PlayCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.start_campana_wombat(campana)
        campana.play()
        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la activación de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito la activación de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(PlayCampanaView, self).post(request, *args, **kwargs)


class PausarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.pausar_campana_wombat(campana)
        campana.pausar()

        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la pausa de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito el pausado de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(PausarCampanaView, self).post(request, *args, **kwargs)


class ActivarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana activándola.
    """

    pattern_name = 'campana_list'

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_id'])
        campana_service = CampanaService()
        resultado = campana_service.despausar_campana_wombat(campana)
        campana.activar()

        if resultado:
            message = '<strong>Operación Exitosa!</strong>\
            Se llevó a cabo con éxito la activación de\
            la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        else:
            message = '<strong>ERROR!</strong>\
                        No se pudo llevar  cabo con éxito la activación de\
                        la Campaña.'

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        return super(ActivarCampanaView, self).post(request, *args, **kwargs)


class UpdateBaseDatosView(FormView):
    """
    Esta vista sincroniza base datos con discador
    """

    model = Campana
    context_object_name = 'campana'
    form_class = UpdateBaseDatosForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self, form_class):
        self.object = self.get_object()
        metadata = self.object.bd_contacto.get_metadata()
        columnas_telefono = metadata.columnas_con_telefono
        nombres_de_columnas = metadata.nombres_de_columnas
        tts_choices = [(columna, nombres_de_columnas[columna]) for columna in
                       columnas_telefono if columna > 6]
        return form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        usa_contestador = form.cleaned_data.get('usa_contestador')
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        telefonos = form.cleaned_data.get('telefonos')
        bd_contacto = form.cleaned_data.get('bd_contacto')
        self.object = self.get_object()
        campana_service = CampanaService()
        error = campana_service.validar_modificacion_bd_contacto(
            self.get_object(), bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        self.object.bd_contacto = bd_contacto
        self.object.save()
        service_base = SincronizarBaseDatosContactosService()
        lista = service_base.crear_lista(self.object, telefonos,
                                         usa_contestador, evitar_duplicados,
                                         evitar_sin_telefono, prefijo_discador)

        campana_service.desasociacion_campana_wombat(self.object)
        campana_service.crear_lista_wombat(lista, self.object)
        campana_service.crear_lista_asociacion_campana_wombat(self.object)
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la exportación del reporte.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  La base de datos es erronea. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )

    def get_success_url(self):
        return reverse('campana_list')
