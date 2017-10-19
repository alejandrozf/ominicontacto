# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging as logging_

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView

from ominicontacto_app.models import BaseDatosContacto, Campana, Queue
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

    template_name = 'campana_manual/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaPreviewBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context


class CampanaPreviewSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    def get_success_url(self):
        return reverse('campana_preview_list')
