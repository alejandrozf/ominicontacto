# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)
from ominicontacto_app.forms import (
    CampanaDialerForm, QueueForm, QueueMemberForm, QueueUpdateForm, GrupoAgenteForm,
    CampanaDialerUpdateForm, SincronizaDialerForm, ActuacionDialerForm
)
from ominicontacto_app.models import (
    CampanaDialer, Campana, Queue, QueueMember, BaseDatosContacto, Grupo, Actuacion
)

from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService


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
            self.campana = CampanaDialer.objects.obtener_en_definicion_para_editar(
                self.kwargs['pk_campana'])

        return super(CheckEstadoCampanaDialerMixin, self).dispatch(request, *args,
                                                             **kwargs)


class CampanaDialerEnDefinicionMixin(object):
    """Mixin para obtener el objeto campama que valida que siempre este en
    el estado en definición.
    """

    def get_object(self, queryset=None):
        return CampanaDialer.objects.obtener_en_definicion_para_editar(
            self.kwargs['pk_campana'])


class CampanaDialerCreateView(CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana_dialer/nueva_edita_campana.html'
    model = CampanaDialer
    context_object_name = 'campana'
    form_class = CampanaDialerForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana dialer")
            messages.warning(self.request, message)
        return super(CampanaDialerCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.eventmemberstatus = True
        self.object.eventwhencalled = True
        self.object.ringinuse = True
        self.object.setinterfacevar = True
        self.object.save()
        return super(CampanaDialerCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'actuacion_campana_dialer',
            kwargs={"pk_campana": self.object.pk})


class CampanaDialerUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana_dialer/edita_campana.html'
    model = CampanaDialer
    context_object_name = 'campana'
    form_class = CampanaDialerUpdateForm

    def get_object(self, queryset=None):
        return CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        campana_service = CampanaService()
        error = campana_service.validar_modificacion_bd_contacto(
            self.get_object(), self.object.bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        return super(CampanaDialerUpdateView, self).form_valid(form)

    def form_invalid(self, form, error=None):

        message = '<strong>Operación Errónea!</strong> \
                  La base de datos es erronea. {0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )

        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse(
            'actuacion_campana_dialer',
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

class QueueMemberCreateView(FormView):
    model = QueueMember
    form_class = QueueMemberForm
    template_name = 'queue/queue_member.html'

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.object = form.save(commit=False)
        existe_member = QueueMember.objects.\
            existe_member_queue(self.object.member, campana.queue_campana)

        if existe_member:
            message = 'Operación Errónea! \
                Este miembro ya se encuentra en esta cola'
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return self.form_invalid(form)
        else:
            self.object.queue_name = campana.queue_campana
            self.object.membername = self.object.member.user.get_full_name()
            self.object.interface = """Local/{0}@from-queue/n""".format(
            self.object.member.sip_extension)
            self.object.paused = 0  # por ahora no lo definimos
            self.object.save()

        return super(QueueMemberCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.kwargs['pk_campana']})


class GrupoAgenteCreateView(FormView):
    model = QueueMember
    form_class = GrupoAgenteForm
    template_name = 'queue/queue_member.html'

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        grupo_id = form.cleaned_data.get('grupo')
        grupo = Grupo.objects.get(pk=grupo_id)
        for agente in grupo.agentes.all():
            QueueMember.objects.get_or_create(
                member=agente,
                queue_name=campana.queue_campana,
                defaults={'membername': agente.user.get_full_name(),
                          'interface': """Local/{0}@from-queue/n""".format(
                              agente.sip_extension),
                          'penalty': 0,
                          'paused': 0},
            )
        return super(GrupoAgenteCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            GrupoAgenteCreateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.kwargs['pk_campana']})


class QueueMemberCampanaView(TemplateView):
    template_name = 'queue/queue_member.html'

    def get_object(self, queryset=None):
         campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
         return campana.queue_campana

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        queue_member_form = QueueMemberForm(self.request.GET or None)
        grupo_agente_form = GrupoAgenteForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['queue_member_form'] = queue_member_form
        context['grupo_agente_form'] = grupo_agente_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCampanaView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context


# usa template de confirmacion por eso se usa la view queue_member_delete_view
class QueueMemberDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto queue.
    """
    model = QueueMember

    def get_object(self, queryset=None):
        return QueueMember.objects.get(pk=self.kwargs['pk_queuemember'])

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.campana.pk})


def queue_member_delete_view(request, pk_queuemember, pk_campana):

    queue_member = QueueMember.objects.get(pk=pk_queuemember)
    queue_member.delete()
    return HttpResponseRedirect("/campana/" + str(pk_campana) +
                                "/queue_member_campana/")


class SincronizaDialerView(FormView):
    """
    Esta vista sincroniza base datos con discador
    """

    model = CampanaDialer
    context_object_name = 'campana'
    form_class = SincronizaDialerForm
    template_name = 'campana_dialer/sincronizar_lista.html'

    def get_object(self, queryset=None):
        return CampanaDialer.objects.get(pk=self.kwargs['pk_campana'])

    def get_context_data(self, **kwargs):
        context = super(
            SincronizaDialerView, self).get_context_data(**kwargs)
        context['campana'] = self.get_object()
        return context

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
        self.object = self.get_object()
        service_base = SincronizarBaseDatosContactosService()
        service_base.crear_lista(self.object, telefonos, usa_contestador,
                                 evitar_duplicados, evitar_sin_telefono,
                                 prefijo_discador)
        campana_service = CampanaService()
        campana_service.crear_campana_wombat(self.object)
        campana_service.crear_trunk_campana_wombat(self.object)
        parametros = ["RS_BUSY", "", 3, 120]
        campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        parametros = ["TERMINATED", "CONTESTADOR", 3, 1800]
        campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        parametros = ["RS_NOANSWER", "", 3, 220]
        campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        parametros = ["RS_REJECTED", "", 3, 300]
        campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        parametros = ["RS_TIMEOUT", "", 3, 300]
        campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        #parametros = ["RS_LOST", "", 1, 360]
        #campana_service.crear_reschedule_campana_wombat(self.object, parametros)
        campana_service.crear_endpoint_campana_wombat(self.object)
        campana_service.crear_endpoint_asociacion_campana_wombat(
            self.object)
        campana_service.crear_lista_wombat(self.object)
        campana_service.crear_lista_asociacion_campana_wombat(self.object)
        message = 'Operación Exitosa!\
                Se llevó a cabo con éxito la exportación del reporte.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('campana_list')
