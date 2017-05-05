# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)
from ominicontacto_app.forms import (
    CampanaForm, QueueForm, QueueMemberForm, QueueUpdateForm, GrupoAgenteForm,
    CampanaUpdateForm, SincronizaDialerForm
)
from ominicontacto_app.models import (
    Campana, Queue, QueueMember, BaseDatosContacto, Grupo,
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.exportar_base_datos import\
    SincronizarBaseDatosContactosService


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


class CampanaCreateView(CreateView):
    """
    Esta vista crea un objeto Campana.
    Por defecto su estado es EN_DEFICNICION,
    Redirecciona a crear las opciones para esta
    Campana.
    """

    template_name = 'campana/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaForm

    def dispatch(self, request, *args, **kwargs):
        base_datos = BaseDatosContacto.objects.obtener_definidas()
        if not base_datos:
            message = ("Debe cargar una base de datos antes de comenzar a "
                       "configurar una campana")
            messages.warning(self.request, message)
        return super(CampanaCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'queue_nuevo',
            kwargs={"pk_campana": self.object.pk})


class CampanaUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana/edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        campana_service = CampanaService()
        error = campana_service.validar_modificacion_bd_contacto(
            self.get_object(), self.object.bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        return super(CampanaUpdateView, self).form_valid(form)

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
            'queue_update',
            kwargs={"pk_campana": self.object.pk})


class QueueCreateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                      CreateView):
    model = Queue
    form_class = QueueForm
    template_name = 'queue/create_update_queue.html'

    def get_initial(self):
        initial = super(QueueCreateView, self).get_initial()
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
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(self.object)
        if self.object.type == Queue.TYPE_DIALER:
            return HttpResponseRedirect(
                reverse('sincroniza_dialer',
                        kwargs={"pk_campana": self.kwargs['pk_campana']}))
        return super(QueueCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse('campana_list')


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


class QueueListView(ListView):
    model = Queue
    template_name = 'queue/queue_list.html'


class QueueDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto queue.
    """
    model = Queue
    template_name = 'queue/delete_queue.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Eliminamos el registro de la tabla de asterisk en mysql
        servicio_asterisk = AsteriskService()
        servicio_asterisk.delete_cola_asterisk(self.object)
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
        Se llevó a cabo con éxito la eliminación de la queue.'

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return Queue.objects.get(name=self.kwargs['pk_queue'])

    def get_success_url(self):
        return reverse('queue_list')


class QueueUpdateView(UpdateView):
    model = Queue
    form_class = QueueUpdateForm
    template_name = 'queue/create_update_queue.html'

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
            return super(QueueUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QueueUpdateView, self).get_context_data(**kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def get_success_url(self):
        return reverse('campana_list')


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

    model = Campana
    context_object_name = 'campana'
    form_class = SincronizaDialerForm
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
        campana_service.crear_endpoint_campana_wombat(self.object.queue_campana)
        campana_service.crear_endpoint_asociacion_campana_wombat(
            self.object.queue_campana)
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
