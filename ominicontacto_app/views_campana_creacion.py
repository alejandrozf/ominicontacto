# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView)
from ominicontacto_app.forms import (
    CampanaForm, QueueForm, QueueMemberForm, QueueUpdateForm,
    FormularioDemoForm, BusquedaContactoForm, ContactoForm, GrupoAgenteForm,
    ReporteForm
)
from ominicontacto_app.models import (
    Campana, Queue, QueueMember, FormularioDemo, Contacto, BaseDatosContacto,
    Grupo
)
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.reporte_campana_calificacion import \
    ReporteCampanaService
from ominicontacto_app.services.reporte_campana_venta import \
    ReporteFormularioVentaService
from ominicontacto_app.services.estadisticas_campana import EstadisticasService

import logging as logging_

from ominicontacto_app.utiles import convert_fecha_datetime

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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        campana_service = CampanaService()
        self.object.save()
        campana_service.crear_formulario(self.object)
        return super(CampanaCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'queue_nuevo',
            kwargs={"pk_campana": self.object.pk})


class CampanaUpdateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                        UpdateView):
    """
    Esta vista actualiza un objeto Campana.
    """

    template_name = 'campana/nueva_edita_campana.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaForm

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
        return super(QueueCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QueueCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.campana.pk})


class QueueMemberCreateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                            FormView):
    model = QueueMember
    form_class = QueueMemberForm
    template_name = 'queue/queue_member.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        existe_member = QueueMember.objects.\
            existe_member_queue(self.object.member, self.campana.queue_campana)

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
            self.object.queue_name = self.campana.queue_campana
            self.object.membername = self.object.member.user.get_full_name()
            self.object.interface = """Local/{0}@from-queue/n""".format(
            self.object.member.sip_extension)
            self.object.paused = 0  # por ahora no lo definimos
            self.object.save()

        return super(QueueMemberCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            QueueMemberCreateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.campana.pk})


class GrupoAgenteCreateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                            FormView):
    model = QueueMember
    form_class = GrupoAgenteForm
    template_name = 'queue/queue_member.html'

    def form_valid(self, form):
        grupo_id = form.cleaned_data.get('grupo')
        grupo = Grupo.objects.get(pk=grupo_id)
        for agente in grupo.agentes.all():
            QueueMember.objects.get_or_create(
                member=agente,
                queue_name=self.campana.queue_campana,
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
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member_campana',
            kwargs={"pk_campana": self.campana.pk})


class QueueMemberCampanaView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                             TemplateView):
    template_name = 'queue/queue_member.html'

    def get_object(self, queryset=None):
        return self.campana.queue_campana

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
        context['campana'] = self.campana
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


class QueueUpdateView(CheckEstadoCampanaMixin, CampanaEnDefinicionMixin,
                      UpdateView):
    model = Queue
    form_class = QueueUpdateForm
    template_name = 'queue/create_update_queue.html'

    def get_object(self, queryset=None):
         return self.campana.queue_campana

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.obtener_en_definicion_para_editar(
            self.kwargs['pk_campana'])
        try:
            Queue.objects.get(campana=campana)
        except Queue.DoesNotExist:
            return HttpResponseRedirect("/campana/" + self.kwargs['pk_campana']
                                        + "/cola/")
        else:
            return super(QueueUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QueueUpdateView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_success_url(self):
        return reverse(
            'queue_member',
            kwargs={"pk_campana": self.campana.pk})


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


class CampanaListView(ListView):
    """
    Esta vista lista los objetos Campana
    """

    template_name = 'campana/campana_list.html'
    context_object_name = 'campanas'
    model = Campana


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


class FormularioDemoFormUpdateView(UpdateView):
    """
    Esta vista actualiza un objeto formulario.
    """

    template_name = 'agente/formulario_create_update_form.html'
    model = FormularioDemo
    context_object_name = 'formulario_demo'
    form_class = FormularioDemoForm

    def get_context_data(self, **kwargs):
        context = super(FormularioDemoFormUpdateView, self).get_context_data(
            **kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(bd_contacto=campana.bd_contacto,
                                        id_cliente=self.kwargs['id_cliente'])
        context['contacto'] = contacto
        return context

    def get_object(self, queryset=None):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        contacto = Contacto.objects.get(bd_contacto=campana.bd_contacto,
                                        id_cliente=self.kwargs['id_cliente'])
        return FormularioDemo.objects.get(campana=campana, contacto=contacto)

    def dispatch(self, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        try:
            Contacto.objects.get(bd_contacto=campana.bd_contacto,
                                 id_cliente=self.kwargs['id_cliente'])
        except Contacto.DoesNotExist:
            return HttpResponseRedirect(reverse('formulario_buscar',
                                                kwargs={"pk_campana":
                                                self.kwargs['pk_campana']}))
        except Contacto.MultipleObjectsReturned:
            return HttpResponseRedirect(reverse('contacto_list_id_cliente',
                                                kwargs={"id_cliente":
                                                self.kwargs['id_cliente']}))
        return super(FormularioDemoFormUpdateView, self).dispatch(*args,
                                                                  **kwargs)

    def get_success_url(self):
        return reverse('formulario_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.object.contacto.id_cliente})


class FormularioDemoFormCreateView(CreateView):
    """
    Esta vista actualiza un objeto formulario.
    """

    template_name = 'agente/formulario_create_update_form.html'
    model = FormularioDemo
    context_object_name = 'formulario_demo'
    form_class = FormularioDemoForm

    def get_initial(self):
        initial = super(FormularioDemoFormCreateView, self).get_initial()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        initial.update({'campana': campana.id})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        contacto = Contacto.objects.create(id_cliente=self.object.id_cliente,
                                           nombre=self.object.nombre,
                                           apellido=self.object.apellido,
                                           telefono=self.object.telefono,
                                           email=self.object.email,
                                           datos=self.object.datos,
                                           bd_contacto=self.object.campana.
                                           bd_contacto)
        self.object.contacto = contacto
        self.object.save()
        return super(FormularioDemoFormCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('formulario_update',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "id_cliente": self.object.contacto.id_cliente})


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
            listado_de_contacto = Contacto.objects.contactos_by_filtro(
                campana.bd_contacto, filtro)
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
        service_formulario = ReporteFormularioVentaService()
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

        service = ReporteFormularioVentaService()
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
            graficos_estadisticas=graficos_estadisticas))

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
            graficos_estadisticas=graficos_estadisticas))
