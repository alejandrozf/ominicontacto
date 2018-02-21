# -*- coding: utf-8 -*-

"""Vista para generar un objecto campana de tipo dialer"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, FormView
from ominicontacto_app.forms import (
    QueueDialerForm, QueueDialerUpdateForm, CampanaDialerUpdateForm,
    SincronizaDialerForm, ActuacionVigenteForm, ReglasIncidenciaForm, CampanaDialerForm,
    ParametroExtraParaWebformFormSet
)
from ominicontacto_app.models import (
    Campana, Queue, BaseDatosContacto, ActuacionVigente, ReglasIncidencia
)

from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)


import logging as logging_

logger = logging_.getLogger(__name__)


class CheckEstadoCampanaDialerMixin(object):
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

        return super(CheckEstadoCampanaDialerMixin, self).dispatch(request, *args,
                                                                   **kwargs)


class CampanaDialerEnDefinicionMixin(object):
    """Mixin para obtener el objeto campama que valida que siempre este en
    el estado en definición.
    """

    def get_object(self, queryset=None):
        return Campana.objects.obtener_en_definicion_para_editar(
            self.kwargs['pk_campana'])


class CampanaDialerConFormsetParametrosViewMixin(object):
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


class CampanaDialerCreateView(CampanaDialerConFormsetParametrosViewMixin, CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana_dialer/nueva_edita_campana.html'
    form_class = CampanaDialerForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana dialer")
            messages.warning(self.request, message)
        return super(CampanaDialerCreateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return None

    def form_valid(self, form, parametro_extra_formset):
        self.object = form.save(commit=False)
        tipo_interaccion = self.object.tipo_interaccion
        if tipo_interaccion is Campana.FORMULARIO and \
           not self.object.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif tipo_interaccion is Campana.SITIO_EXTERNO and not self.object.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        self.object.type = Campana.TYPE_DIALER
        self.object.reported_by = self.request.user
        self.object.save()
        parametro_extra_formset.instance = self.object
        parametro_extra_formset.save()
        return super(CampanaDialerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'campana_dialer_queue_create',
            kwargs={"pk_campana": self.object.pk})


class CampanaDialerUpdateView(CampanaDialerConFormsetParametrosViewMixin, UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana_dialer/edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaDialerUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form, parametro_extra_formset):
        self.object = form.save(commit=False)
        parametro_extra_formset.save()
        return super(CampanaDialerUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'campana_dialer_queue_update',
            kwargs={"pk_campana": self.object.pk})


class SincronizaDialerView(FormView):
    """
    Esta vista sincroniza base datos con discador
    """

    model = Campana
    context_object_name = 'campana'
    form_class = SincronizaDialerForm
    template_name = 'campana_dialer/sincronizar_lista.html'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_context_data(self, **kwargs):
        context = super(
            SincronizaDialerView, self).get_context_data(**kwargs)
        context['campana'] = self.get_object()
        return context

    def get_form(self):
        self.form_class = self.get_form_class()
        self.object = self.get_object()
        metadata = self.object.bd_contacto.get_metadata()
        nombres_de_columnas = metadata.nombres_de_columnas
        nombres_de_columnas.remove('telefono')
        tts_choices = [(columna, columna) for columna in
                       nombres_de_columnas]
        return self.form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        columnas = form.cleaned_data.get('columnas')
        self.object = self.get_object()
        service_base = SincronizarBaseDatosContactosService()
        # Crea un achivo con la lista de contactos para importar a wombat
        service_base.crear_lista(self.object, columnas, evitar_duplicados,
                                 evitar_sin_telefono, prefijo_discador)
        campana_service = CampanaService()
        # crear campana en wombat
        campana_service.crear_campana_wombat(self.object)
        # crea trunk en wombat
        campana_service.crear_trunk_campana_wombat(self.object)
        # crea reglas de incidencia en wombat
        for regla in self.object.reglas_incidencia.all():
            parametros = [regla.get_estado_wombat(), regla.estado_personalizado,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat()]
            campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        # crea endpoint en wombat
        campana_service.crear_endpoint_campana_wombat(self.object)
        # asocia endpoint en wombat a campana
        campana_service.crear_endpoint_asociacion_campana_wombat(
            self.object)
        # crea lista en wombat
        campana_service.crear_lista_wombat(self.object)
        # asocia lista a campana en wombat
        campana_service.crear_lista_asociacion_campana_wombat(self.object)
        self.object.estado = Campana.ESTADO_INACTIVA
        self.object.save()
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la creación de campana dialer.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
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
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('campana_dialer_list')


class ActuacionVigenteCampanaDialerCreateView(CheckEstadoCampanaDialerMixin, CreateView):
    """
    Esta vista crea uno objeto ActuacionVigente
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/actuacion_vigente_campana.html'
    model = ActuacionVigente
    context_object_name = 'actuacion'
    form_class = ActuacionVigenteForm

    def get_initial(self):
        initial = super(ActuacionVigenteCampanaDialerCreateView, self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ActuacionVigenteCampanaDialerCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'nueva_reglas_incidencia_campana_dialer',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )


class ReglasIncidenciaCampanaDialerCreateView(CheckEstadoCampanaDialerMixin, CreateView):
    """
    Esta vista crea uno o varios objetos ReglasIncidencia
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/reglas_incidencia.html'
    model = ReglasIncidencia
    context_object_name = 'reglas_incidencia'
    form_class = ReglasIncidenciaForm

    def get_initial(self):
        initial = super(ReglasIncidenciaCampanaDialerCreateView, self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ReglasIncidenciaCampanaDialerCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.campana.valida_reglas_incidencia(self.object):
            message = """¡Cuidado!
            El estado {0} ya se encuentra cargado""".format(
                self.object.get_estado_display())
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return self.form_invalid(form)
        if self.object.estado is ReglasIncidencia.TERMINATED:
            self.object.estado_personalizado = "CONTESTADOR"
        self.object.save()

        return super(ReglasIncidenciaCampanaDialerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'nueva_reglas_incidencia_campana_dialer',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )


def regla_incidencia_delete_view(request, pk_campana, pk_regla):
    """Esta vista elimina una regla de incidencia en wombat"""
    regla = ReglasIncidencia.objects.get(pk=pk_regla)
    regla.delete()
    return HttpResponseRedirect(
        reverse(
            'nueva_reglas_incidencia_campana_dialer',
            kwargs={"pk_campana": pk_campana}
        ))


class QueueDialerCreateView(CheckEstadoCampanaDialerMixin,
                            CampanaDialerEnDefinicionMixin, CreateView):
    """Vista crear cola para campana dialer"""
    model = Queue
    form_class = QueueDialerForm
    template_name = 'campana_dialer/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueDialerCreateView, self).get_initial()
        initial.update({'campana': self.campana.id,
                        'name': self.campana.nombre})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        if self.object.initial_boost_factor is None:
            self.object.initial_boost_factor = 1.0
        self.object.save()
        return super(QueueDialerCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueDialerCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        context['create'] = True
        return context

    def get_success_url(self):
        return reverse(
            'nuevo_actuacion_vigente_campana_dialer',
            kwargs={"pk_campana": self.campana.pk}
        )


class QueueDialerUpdateView(UpdateView):
    """Vista actualiza cola para campana dialer"""
    model = Queue
    form_class = QueueDialerUpdateForm
    template_name = 'campana_dialer/create_update_queue.html'

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return campana.queue_campana

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        try:
            Queue.objects.get(campana=campana)
        except Queue.DoesNotExist:
            return HttpResponseRedirect("/campana_dialer/" + self.kwargs['pk_campana'] + "/cola/")
        else:
            return super(QueueDialerUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.initial_boost_factor is None:
            self.object.initial_boost_factor = 1.0
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
        campana_service = CampanaService()
        campana_service.update_endpoint(self.object.campana)
        return super(QueueDialerUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueDialerUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse('campana_dialer_list')


class CampanaDialerReplicarView(CheckEstadoCampanaDialerMixin,
                                CampanaDialerEnDefinicionMixin, UpdateView):
    """
    Esta vista actualiza una campana luego de crearla por template
    """

    template_name = 'campana_dialer/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaDialerForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana dialer")
            messages.warning(self.request, message)
        return super(CampanaDialerReplicarView, self).dispatch(request, *args, **kwargs)

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
        self.object = form.save(commit=False)
        tipo_interaccion = self.object.tipo_interaccion
        if tipo_interaccion is Campana.FORMULARIO and not self.object.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif tipo_interaccion is Campana.SITIO_EXTERNO and not self.object.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        self.object.reported_by = self.request.user
        self.object.save()
        return super(CampanaDialerReplicarView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'campana_dialer_replicar_cola',
            kwargs={"pk_campana": self.object.pk})


class QueueDialerReplicarView(CheckEstadoCampanaDialerMixin,
                              CampanaDialerEnDefinicionMixin, UpdateView):
    """Vista replicar cola de campana dialer"""
    model = Queue
    form_class = QueueDialerUpdateForm
    template_name = 'campana_dialer/create_update_queue.html'

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        Campana.objects.replicar_campana_queue(campana)
        return campana.queue_campana

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        try:
            Queue.objects.get(campana=campana)
        except Queue.DoesNotExist:
            return HttpResponseRedirect("/campana_dialer/" + self.kwargs['pk_campana'] + "/cola/")
        else:
            return super(QueueDialerReplicarView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
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
        return super(QueueDialerReplicarView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueDialerReplicarView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        context['create'] = True
        return context

    def get_success_url(self):
        return reverse('campana_dialer_update_actuacion_vigente',
                       kwargs={"pk_campana": self.campana.pk})


class ActuacionVigenteCampanaDialerUpdateView(CheckEstadoCampanaDialerMixin, UpdateView):
    """
    Esta vista actualiza uno objeto ActuacionVigente
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/actuacion_vigente_campana.html'
    model = ActuacionVigente
    context_object_name = 'actuacion'
    form_class = ActuacionVigenteForm

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        return campana.actuacionvigente

    def get_context_data(self, **kwargs):
        context = super(
            ActuacionVigenteCampanaDialerUpdateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'nueva_reglas_incidencia_campana_dialer',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )
