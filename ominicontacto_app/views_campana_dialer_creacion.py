# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)
from ominicontacto_app.forms import (
    CampanaDialerForm, QueueDialerForm, QueueDialerUpdateForm,
    CampanaDialerUpdateForm, SincronizaDialerForm, ActuacionDialerForm,
    ActuacionVigenteForm, ReglasIncidenciaForm, CampanaForm
)
from ominicontacto_app.models import (
    CampanaDialer, Campana, Queue, BaseDatosContacto, Actuacion, ActuacionVigente,
    ReglasIncidencia
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


class CampanaDialerCreateView(CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana_dialer/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana dialer")
            messages.warning(self.request, message)
        return super(CampanaDialerCreateView, self).dispatch(request, *args, **kwargs)

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
        if self.object.tipo_interaccion is Campana.FORMULARIO and \
            not self.object.formulario:
            error = "Debe seleccionar un formulario"
            return self.form_invalid(form, error=error)
        elif self.object.tipo_interaccion is Campana.SITIO_EXTERNO and \
            not self.object.sitio_externo:
            error = "Debe seleccionar un sitio externo"
            return self.form_invalid(form, error=error)
        self.object.type = Campana.TYPE_DIALER
        self.object.save()
        return super(CampanaDialerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'campana_dialer_queue_create',
            kwargs={"pk_campana": self.object.pk})


class CampanaDialerUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana_dialer/edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaDialerUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse(
            'campana_dialer_queue_update',
            kwargs={"pk_campana": self.object.pk})


class ActuacionCampanaDialerCreateView(CheckEstadoCampanaDialerMixin, CreateView):
    """
    Esta vista crea uno o varios objetos Actuacion
    para la Campana que se este creando.
    Inicializa el form con campo campana (hidden)
    con el id de campana que viene en la url.
    """

    template_name = 'campana_dialer/actuacion_campana.html'
    model = Actuacion
    context_object_name = 'actuacion'
    form_class = ActuacionDialerForm

    def get_initial(self):
        initial = super(ActuacionCampanaDialerCreateView, self).get_initial()
        initial.update({'campana': self.campana.id})
        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ActuacionCampanaDialerCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        context['actuaciones_validas'] = \
            self.campana.obtener_actuaciones_validas()
        return context

    def form_valid(self, form):
        form_valid = super(ActuacionCampanaDialerCreateView, self).form_valid(form)

        if not self.campana.valida_actuaciones():
            message = """<strong>¡Cuidado!</strong>
            Los días del rango de fechas seteados en la campaña NO coinciden
            con ningún día de las actuaciones programadas. Por consiguiente
            la campaña NO se ejecutará."""
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

        return form_valid

    def get_success_url(self):
        return reverse(
            'actuacion_campana_dialer',
            kwargs={"pk_campana": self.kwargs['pk_campana']}
        )


class ActuacionCampanaDialerDeleteView(CheckEstadoCampanaDialerMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto Actuación seleccionado.
    """

    model = Actuacion
    template_name = 'campana_dialer/elimina_actuacion_campana.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        if not self.campana.valida_actuaciones():
            message = """<strong>¡Cuidado!</strong>
            Los días del rango de fechas seteados en la campaña NO coinciden
            con ningún día de las actuaciones programadas. Por consiguiente
            la campaña NO se ejecutará."""
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

        message = '<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la Actuación.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse(
            'actuacion_campana_dialer',
            kwargs={"pk_campana": self.campana.pk}
        )


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
        columnas_telefono = metadata.columnas_con_telefono
        nombres_de_columnas = metadata.nombres_de_columnas
        tts_choices = [(columna, nombres_de_columnas[columna]) for columna in
                       columnas_telefono if columna > 6]
        return self.form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        usa_contestador = form.cleaned_data.get('usa_contestador')
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        telefonos = form.cleaned_data.get('telefonos')
        self.object = self.get_object()
        service_base = SincronizarBaseDatosContactosService()
        service_base.crear_lista(self.object, telefonos, usa_contestador,
                                 evitar_duplicados, evitar_sin_telefono,
                                 prefijo_discador)
        campana_service = CampanaService()
        campana_service.crear_campana_wombat(self.object)
        campana_service.crear_trunk_campana_wombat(self.object)
        for regla in self.object.reglas_incidencia.all():
            parametros = [regla.get_estado_wombat(), regla.estado_personalizado,
                          regla.intento_max, regla.reintentar_tarde,
                          regla.get_en_modo_wombat( )]
            campana_service.crear_reschedule_campana_wombat(self.object, parametros)

        campana_service.crear_endpoint_campana_wombat(self.object)
        campana_service.crear_endpoint_asociacion_campana_wombat(
            self.object)
        campana_service.crear_lista_wombat(self.object)
        campana_service.crear_lista_asociacion_campana_wombat(self.object)
        self.object.estado = Campana.ESTADO_INACTIVA
        self.object.save()
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la exportación del reporte.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
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

    regla = ReglasIncidencia.objects.get(pk=pk_regla)
    regla.delete()
    return HttpResponseRedirect(
        reverse(
            'nueva_reglas_incidencia_campana_dialer',
            kwargs={"pk_campana": pk_campana}
        ))


class QueueDialerCreateView(CheckEstadoCampanaDialerMixin,
                            CampanaDialerEnDefinicionMixin, CreateView):
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
            return HttpResponseRedirect("/campana_dialer/" + self.kwargs['pk_campana']
                                        + "/cola/")
        else:
            return super(QueueDialerUpdateView, self).dispatch(*args, **kwargs)

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
        return super(QueueDialerUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueDialerUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse('campana_dialer_list')
