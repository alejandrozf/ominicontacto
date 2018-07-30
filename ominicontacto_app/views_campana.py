# -*- coding: utf-8 -*-

"""Vista para administrar el modelo Campana de tipo entrantes"""

from __future__ import unicode_literals

import datetime
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import (
    ListView, UpdateView, DeleteView, FormView)
from django.views.generic.base import RedirectView
from django.utils.translation import ugettext_lazy as _

from ominicontacto_app.forms import (
    ReporteForm, FormularioNuevoContacto,
    FormularioCampanaContacto, CampanaSupervisorUpdateForm
)
from ominicontacto_app.models import (
    Campana, Queue, Contacto, SupervisorProfile
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)

from ominicontacto_app.utiles import convert_fecha_datetime, convertir_ascii_string
from ominicontacto_app.services.reporte_llamadas_campana import \
    EstadisticasCampanaLlamadasService
from configuracion_telefonia_app.views import DeleteNodoDestinoMixin, SincronizadorDummy

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanasDeleteMixin(object):
    """
    Encapsula comportamiento común a todas las campanas en el momento de
    eliminar
    """
    nodo_eliminado = _(u'<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

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

        messages.add_message(
            self.request,
            messages.SUCCESS,
            self.nodo_eliminado,
        )


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

        context['campanas'] = campanas
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
        return context


class CampanaDeleteView(DeleteNodoDestinoMixin, CampanasDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    # TODO: realizar refactor aquí, la vista de eliminación no debería tener dos métodos
    # 'delete'
    model = Queue
    template_name = 'campana/delete_campana.html'
    imposible_eliminar = _('No se puede eliminar una Campaña que es destino en un flujo de llamada')
    nodo_eliminado = _(u'<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.')
    url_eliminar_name = 'campana_elimina'

    def delete(self, request, *args, **kwargs):
        super(CampanaDeleteView, self).delete(request, *args, **kwargs)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        # No se puede volver a borrar una campaña.
        return Campana.objects.exclude(
            estado=Campana.ESTADO_BORRADA).get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_list')

    def get_sincronizador_de_configuracion(self):
        return SincronizadorDummy()


# TODO: DEPRECATED? Verificar si se debe eliminar
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
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

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
            reverse('calificacion_formulario_update_or_create',
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
        supervisores = SupervisorProfile.objects.exclude(borrado=True)
        supervisors_choices = [(supervisor.user.pk, supervisor.user) for supervisor in
                               supervisores]
        return self.form_class(supervisors_choices=supervisors_choices,
                               **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('campana_list')


class CampanaBorradasListView(CampanaListView):
    """
    Vista que lista las campañas entrantes pero de incluyendo las borradas ocultas
    """

    template_name = 'campana/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(CampanaBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})
