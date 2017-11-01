# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging as logging_

from ast import literal_eval

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.utils import DatabaseError
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, View

from ominicontacto_app.models import BaseDatosContacto, Campana, Queue, AgenteEnContacto
from ominicontacto_app.forms import CampanaPreviewForm
from ominicontacto_app.views_campana_manual import CampanaManualListView, CampanaManualDeleteView
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView

logger = logging_.getLogger(__name__)


class CampanaPreviewCreateView(CreateView):
    """
    Crea una campaña de tipo Preview
    """
    model = Campana
    template_name = 'campana_preview/campana_preview.html'
    context_object_name = 'campana'
    form_class = CampanaPreviewForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas().exists()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana")
            messages.warning(self.request, message)
        return super(CampanaPreviewCreateView, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                . {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        tipo_interaccion = form.instance.tipo_interaccion
        if tipo_interaccion is Campana.FORMULARIO and not form.instance.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif tipo_interaccion is Campana.SITIO_EXTERNO and not form.instance.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        form.instance.type = Campana.TYPE_PREVIEW
        form.instance.reported_by = self.request.user
        form.instance.estado = Campana.ESTADO_ACTIVA
        form.save()
        auto_grabacion = form.cleaned_data['auto_grabacion']
        detectar_contestadores = form.cleaned_data['detectar_contestadores']
        queue = Queue(
            campana=form.instance,
            name=form.instance.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120,
            queue_asterisk=Queue.objects.ultimo_queue_asterisk(),
            auto_grabacion=auto_grabacion,
            detectar_contestadores=detectar_contestadores
        )
        queue.save()

        # rellenar la tabla que relación agentes y contactos con los valores iniciales
        form.instance.establecer_valores_iniciales_agente_contacto()
        return super(CampanaPreviewCreateView, self).form_valid(form)
        return super(CampanaPreviewCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('campana_preview_list')


class CampanaPreviewUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    model = Campana
    template_name = 'campana_preview/campana_preview_update.html'
    context_object_name = 'campana'
    form_class = CampanaPreviewForm

    def get_initial(self):
        initial = super(CampanaPreviewUpdateView, self).get_initial()
        campana = self.get_object()
        initial.update({
            'auto_grabacion': campana.queue_campana.auto_grabacion,
            'detectar_contestadores': campana.queue_campana.detectar_contestadores})
        return initial

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form):
        tipo_interaccion = form.instance.tipo_interaccion
        if tipo_interaccion is Campana.FORMULARIO and \
           not form.instance.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif tipo_interaccion is Campana.SITIO_EXTERNO and not form.instance.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        form.save()
        auto_grabacion = form.cleaned_data['auto_grabacion']
        detectar_contestadores = form.cleaned_data['detectar_contestadores']
        queue = self.object.queue_campana
        queue.auto_grabacion = auto_grabacion
        queue.detectar_contestadores = detectar_contestadores
        queue.save()
        return super(CampanaPreviewUpdateView, self).form_valid(form)

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                . {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse('campana_preview_list')


class CampanaPreviewDeleteView(CampanaManualDeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campana_preview/delete_campana.html'

    def get_success_url(self):
        return reverse('campana_preview_list')


class CampanaPreviewListView(CampanaManualListView):
    """
    Vista que lista las campañas preview
    """
    template_name = 'campana_preview/campana_list.html'

    def get_queryset(self):
        return Campana.objects.obtener_campanas_preview()

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewListView, self).get_context_data(**kwargs)
        context['finalizadas'] = context['campanas'].filter(estado=Campana.ESTADO_FINALIZADA)
        context['mostrar_ocultas_tipo'] = "mostrar_campanas_preview_ocultas()"
        return context


class CampanaPreviewBorradasListView(CampanaPreviewListView):
    """
    Vista que lista las campañas preview pero de incluyendo las borradas ocultas
    """

    template_name = 'campana_preview/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(CampanaPreviewBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})


class CampanaPreviewSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    def get_success_url(self):
        return reverse('campana_preview_list')


def campana_mostrar_ocultar_view(request, *args, **kwargs):
    """
    Cambia el atributo 'oculto' de la campaña hacia el valor opuesto (muestra/oculta)
    """
    pk = kwargs.get('pk_campana')
    campana = get_object_or_404(Campana, pk=pk)
    campana.oculto = not campana.oculto
    campana.save()
    return JsonResponse({'result': 'Ok'})


class ObtenerContactoView(View):
    """
    Devuelve un contacto de una campaña preview, y además lo marca como entregado
    para evitar que sea entregado a más de un agente de forma simultánea
    """

    def dispatch(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        agente_profile = request.user.get_agente_profile()
        agente_in_campana_preview = False
        if agente_profile:
            agente_in_campana_preview = agente_profile.campana_member.filter(
                queue_name__campana__pk=pk_campana).exists()
        if agente_profile and agente_in_campana_preview:
            return super(ObtenerContactoView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def _gestionar_contacto(self, request, qs_agentes_contactos):
        if qs_agentes_contactos.exists():
            agente_en_contacto = qs_agentes_contactos.first()
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_ENTREGADO
            agente_en_contacto.agente_id = request.user.get_agente_profile().pk
            agente_en_contacto.save()
            data = model_to_dict(agente_en_contacto)
            data['datos_contacto'] = literal_eval(data['datos_contacto'])
            return JsonResponse(data)
        else:
            return JsonResponse({'result': 'Error',
                                 'code': 'error-no-contactos',
                                 'data': 'No hay contactos para asignar en esta campaña'})

    def post(self, request, *args, **kwargs):
        campana_id = kwargs.get('pk_campana', False)
        try:
            qs_agentes_contactos = AgenteEnContacto.objects.select_for_update().filter(
                agente_id=-1, campana_id=campana_id)
        except DatabaseError:
            return JsonResponse({'result': 'Error',
                                 'code': 'error-concurrencia',
                                 'data': 'Contacto siendo accedido por más de un agente'})
        else:
            return self._gestionar_contacto(request, qs_agentes_contactos)
