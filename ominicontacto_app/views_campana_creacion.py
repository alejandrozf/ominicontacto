# -*- coding: utf-8 -*-

"""Vista para la creacion de un objecto campana de tipo entrante"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView
from ominicontacto_app.forms import (
    CampanaForm, QueueEntranteForm, QueueEntranteUpdateForm, CampanaUpdateForm,
    ParametroExtraParaWebformFormSet
)
from ominicontacto_app.models import (
    Campana, Queue, BaseDatosContacto, ArchivoDeAudio
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService


import logging as logging_

logger = logging_.getLogger(__name__)


class CheckEstadoCampanaMixin(object):
    """Mixin para utilizar en las vistas de creación de campañas.
    Utiliza `Campana.objects.obtener_en_definicion_para_editar()`
    para obtener la campaña pasada por url.
    Este metodo falla si la campaña no deberia ser editada.
    ('editada' en el contexto del proceso de creacion de la campaña)
    """

    def dispatch(self, request, *args, **kwargs):
        chequeada = kwargs.pop('_campana_chequeada', False)
        if not chequeada:
            self.campana = Campana.objects.obtener_en_definicion_para_editar(
                self.kwargs['pk_campana'])

        return super(CheckEstadoCampanaMixin, self).dispatch(request, *args,
                                                             **kwargs)


class CampanaEnDefinicionMixin(object):
    """Mixin para obtener el objeto campama que valida que siempre este en
    el estado en definición.
    """

    def get_object(self, queryset=None):
        return Campana.objects.obtener_en_definicion_para_editar(
            self.kwargs['pk_campana'])


class CampanaEntranteConFormsetParametrosViewMixin(object):
    model = Campana
    context_object_name = 'campana'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        parametro_extra_formset = ParametroExtraParaWebformFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(
            form=form, parametro_extra_formset=parametro_extra_formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        parametro_extra_formset = ParametroExtraParaWebformFormSet(self.request.POST,
                                                                   instance=self.object)

        if form.is_valid() and parametro_extra_formset.is_valid():
            return self.form_valid(form, parametro_extra_formset)
        else:
            return self.form_invalid(form, parametro_extra_formset)


class CampanaEntranteCreateView(CampanaEntranteConFormsetParametrosViewMixin, CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana/nueva_edita_campana.html'
    form_class = CampanaForm

    def get_object(self):
        return None

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana")
            messages.warning(self.request, message)
        return super(CampanaEntranteCreateView, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form, parametro_extra_formset, error=None):

        message = '<strong>Operación Errónea!</strong> \
                . {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        context_data = self.get_context_data()
        context_data['form'] = form
        context_data['parametro_extra_formset'] = parametro_extra_formset
        return self.render_to_response(context_data)

    def form_valid(self, form, parametro_extra_formset):
        self.object = form.save(commit=False)
        self.object.type = Campana.TYPE_ENTRANTE
        self.object.reported_by = self.request.user
        self.object.save()
        parametro_extra_formset.instance = self.object
        parametro_extra_formset.save()
        return super(CampanaEntranteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_nuevo',
            kwargs={"pk_campana": self.object.pk})


class CampanaEntranteUpdateView(CampanaEntranteConFormsetParametrosViewMixin, UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana/edita_campana.html'
    form_class = CampanaUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form, parametro_extra_formset):
        self.object = form.save(commit=False)
        campana_service = CampanaService()
        error = None
        if self.object.bd_contacto:
            error = campana_service.validar_modificacion_bd_contacto(
                self.get_object(), self.object.bd_contacto)
        if error:
            return self.form_invalid(form, parametro_extra_formset, error=error)
        parametro_extra_formset.instance = self.object
        parametro_extra_formset.save()
        return super(CampanaEntranteUpdateView, self).form_valid(form)

    def form_invalid(self, form, parametro_extra_formset, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  La base de datos es erronea. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )

        context_data = self.get_context_data()
        context_data['form'] = form
        context_data['parametro_extra_formset'] = parametro_extra_formset
        return self.render_to_response(context_data)

    def get_success_url(self):
        return reverse(
            'queue_update',
            kwargs={"pk_campana": self.object.pk})


class QueueEntranteCreateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                              CreateView):
    """Vista para la creacion de una Cola"""
    model = Queue
    form_class = QueueEntranteForm
    template_name = 'campana/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueEntranteCreateView, self).get_initial()
        initial.update({'campana': self.campana.id,
                        'name': self.campana.nombre})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        audios = ArchivoDeAudio.objects.all()
        return self.form_class(audios_choices=audios, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.wrapuptime = 0
        self.object.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        audio_pk = form.cleaned_data['audios']
        if audio_pk:
            audio = ArchivoDeAudio.objects.get(pk=int(audio_pk))
            self.object.announce = audio.audio_asterisk
        else:
            self.object.announce = None
        self.object.save()
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(self.object)
        self.campana.estado = Campana.ESTADO_ACTIVA
        self.campana.save()
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
        return super(QueueEntranteCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueEntranteCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse('campana_list')


class QueueEntranteUpdateView(UpdateView):
    """Vista actualiza una Queue(Cola)"""
    model = Queue
    form_class = QueueEntranteUpdateForm
    template_name = 'campana/create_update_queue.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        audios = ArchivoDeAudio.objects.all()
        conversor_audio = ConversorDeAudioService()
        if self.get_object().announce:
            id_audio = conversor_audio.obtener_id_archivo_de_audio_desde_path(
                self.get_object().announce)
        else:
            id_audio = 0
        return self.form_class(
            audios_choices=audios, id_audio=id_audio, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return campana.queue_campana

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        try:
            Queue.objects.get(campana=campana)
        except Queue.DoesNotExist:
            return HttpResponseRedirect("/campana/" + self.kwargs['pk_campana']
                                        + "/cola/")
        else:
            return super(QueueEntranteUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        audio_pk = form.cleaned_data['audios']
        if audio_pk:
            audio = ArchivoDeAudio.objects.get(pk=int(audio_pk))
            self.object.announce = audio.audio_asterisk
        else:
            self.object.announce = None
        self.object.save()

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
        return super(QueueEntranteUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueEntranteUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse('campana_list')
