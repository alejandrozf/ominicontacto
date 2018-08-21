# -*- coding: utf-8 -*-

"""En este modulo se encuentran las vistas basicas para inicializar el sistema,
usuarios, modulos, grupos, pausas

DT:Mover la creacion de agente a otra vista
"""

from __future__ import unicode_literals

import logging

from services.sms_services import SmsManager
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
)
from defender import utils
from defender import config

from ominicontacto_app.models import (
    User, AgenteProfile, Modulo, Grupo, Pausa, DuracionDeLlamada, Agenda,
    Chat, MensajeChat, QueueMember
)
from ominicontacto_app.forms import (
    CustomUserCreationForm, UserChangeForm, AgenteProfileForm,
    AgendaBusquedaForm, PausaForm, GrupoForm
)
from services.asterisk_service import ActivacionAgenteService,\
    RestablecerConfigSipError
from services.regeneracion_asterisk import RegeneracionAsteriskService,\
    RestablecerDialplanError
from ominicontacto_app.utiles import convert_string_in_boolean,\
    convert_fecha_datetime
from ominicontacto_app import version
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    RestablecerConfiguracionTelefonicaError, SincronizadorDeConfiguracionPausaAsterisk)

logger = logging.getLogger(__name__)

# def mensajes_recibidos_view(request):
#
#     service_sms = SmsManager()
#     mensajes = service_sms.obtener_ultimo_mensaje_por_numero()
#     response = JsonResponse(service_sms.armar_json_mensajes_recibidos(
# mensajes))
#     return response


def index_view(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


def login_view(request):
    detail = None
    user_is_blocked = False
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        login_unsuccessful = False
        if utils.is_already_locked(request, username=username):
            intentos_fallidos = config.FAILURE_LIMIT + 2
            detail = _("Haz tratado de loguearte {intentos_fallidos} veces,"
                       " sin exito. Tu cuenta y dirección IP"
                       " permanecerán bloqueadas por {cooloff_time_seconds} segundos."
                       " Contacta al Administrador".format(intentos_fallidos=intentos_fallidos,
                                                           cooloff_time_seconds=config.COOLOFF_TIME)

                       )
            user_is_blocked = True
            login_unsuccessful = True
        user = authenticate(username=username, password=password)
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            login_unsuccessful = True
        utils.add_login_attempt_to_db(request, login_valid=not login_unsuccessful,
                                      username=username)
        user_not_blocked = utils.check_request(request, login_unsuccessful=login_unsuccessful,
                                               username=username)
        if user_not_blocked and not user_is_blocked and not login_unsuccessful:
            if form.is_valid():
                login(request, user)
                user.set_session_key(request.session.session_key)
                if user.is_agente:
                    return HttpResponseRedirect(reverse('view_node'))
                else:
                    return HttpResponseRedirect(reverse('index'))
    else:
        form = AuthenticationForm(request)
    context = {
        'form': form,
        'detail': detail,
        'user_is_blocked': user_is_blocked,
    }
    template_name = 'registration/login.html'
    return TemplateResponse(request, template_name, context)


class CustomerUserCreateView(CreateView):
    """Vista para crear un usuario"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user/user_create_update_form.html'

    def get_success_url(self):
        return reverse('user_list', kwargs={"page": 1})


class CustomerUserUpdateView(UpdateView):
    """Vista para modificar un usuario"""
    model = User
    form_class = UserChangeForm
    template_name = 'user/user_create_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(CustomerUserUpdateView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        ret = super(CustomerUserUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = User.objects.get(pk=form.instance.id)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request,
                         'El usuario fue actualizado correctamente')

        return ret

    def get_success_url(self):
        return reverse('user_list', kwargs={"page": 1})


class UserDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto user
    """
    model = User
    template_name = 'user/delete_user.html'

    def dispatch(self, request, *args, **kwargs):
        usuario = User.objects.get(pk=self.kwargs['pk'])
        if usuario.id is 1:
            return HttpResponseRedirect(
                reverse('user_list', kwargs={"page": 1}))
        return super(UserDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserDeleteView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_agente and self.object.get_agente_profile():
            self.object.get_agente_profile().borrar()
            QueueMember.objects.borrar_member_queue(
                self.object.get_agente_profile())
        if self.object.is_supervisor and self.object.get_supervisor_profile():
            self.object.get_supervisor_profile().borrar()
        self.object.borrar()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('user_list', kwargs={"page": 1})


class UserListView(ListView):
    """Vista que que muestra el listao de usuario paginado 40 por pagina y
    ordenado por id"""
    model = User
    template_name = 'user/user_list.html'
    paginate_by = 40

    def get_queryset(self):
        """Returns user ordernado por id"""
        return User.objects.exclude(borrado=True).order_by('id')


class AgenteProfileCreateView(CreateView):
    """Vista para crear un agente"""
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'base_create_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        modulo = Modulo.objects.all()
        grupo = Grupo.objects.all()
        if not modulo:
            message = ("Debe cargar un modulo antes de crear un perfil de "
                       "agente")
            messages.warning(self.request, message)
        if not grupo:
            message = (
                "Debe cargar un grupo antes de crear un perfil de agente"
            )
            messages.warning(self.request, message)

        usuario = User.objects.get(pk=self.kwargs['pk_user'])
        if usuario.get_supervisor_profile():
            message = (
                "No puede crear un perfil de agente a un supervisor"
            )

            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('user_list', kwargs={"page": 1}))
        return super(AgenteProfileCreateView, self).dispatch(request, *args,
                                                             **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        usuario = User.objects.get(pk=self.kwargs['pk_user'])
        self.object.user = usuario
        self.object.sip_extension = 1000 + usuario.id
        self.object.reported_by = self.request.user
        self.object.save()
        # generar archivos sip en asterisk
        asterisk_sip_service = ActivacionAgenteService()
        try:
            asterisk_sip_service.activar()
        except RestablecerConfigSipError, e:
            message = ("<strong>¡Cuidado!</strong> "
                       "con el siguiente error{0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return super(AgenteProfileCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_list', kwargs={"page": 1})


class AgenteProfileUpdateView(UpdateView):
    """Vista para modificar un agente"""
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agenteprofile'])

    def form_valid(self, form):
        self.object = form.save()

        asterisk_sip_service = ActivacionAgenteService()
        try:
            asterisk_sip_service.activar()
        except RestablecerConfigSipError, e:
            message = ("<strong>¡Cuidado!</strong> "
                       "con el siguiente error{0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return super(AgenteProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_list', kwargs={"page": 1})


class ModuloCreateView(CreateView):
    """Vista para crear un modulo"""
    model = Modulo
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloUpdateView(UpdateView):
    """Vista para modificar un modulo"""
    model = Modulo
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto modulo
    """
    model = Modulo
    template_name = 'delete_modulo.html'

    def dispatch(self, request, *args, **kwargs):
        modulo = Modulo.objects.get(pk=self.kwargs['pk'])
        agentes_relacionados = modulo.agenteprofile_set.exists()
        if agentes_relacionados:
            message = _("No está permitido eliminar un módulo con agentes relacionados")
            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('modulo_list'))
        return super(ModuloDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloListView(ListView):
    """Vista para listar los modulos"""
    model = Modulo
    template_name = 'modulo_list.html'


class AgenteListView(ListView):
    """Vista para listar los agentes"""
    model = AgenteProfile
    template_name = 'agente_profile_list.html'

    def get_context_data(self, **kwargs):
        context = super(AgenteListView, self).get_context_data(
            **kwargs)
        agentes = AgenteProfile.objects.exclude(borrado=True)

        # if self.request.user.is_authenticated() and self.request.user:
        #     user = self.request.user
        #     agentes = agentes.filter(reported_by=user)

        context['agentes'] = agentes
        return context


class GrupoCreateView(CreateView):
    """Vista para crear un grupo
    DT: eliminar fields de la vista crear un form para ello
    """
    model = Grupo
    template_name = 'grupo_create_update.html'
    form_class = GrupoForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.object.auto_unpause:
            self.object.auto_unpause = 0
        self.object.save()
        return super(GrupoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoUpdateView(UpdateView):
    """Vista para modificar un grupo
        DT: eliminar fields de la vista crear un form para ello
        """
    model = Grupo
    template_name = 'grupo_create_update.html'
    form_class = GrupoForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        auto_unpause = form.cleaned_data.get('auto_unpause')
        if not auto_unpause:
            self.object.auto_unpause = 0
        self.object.save()
        return super(GrupoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoListView(ListView):
    """Vista para listar los grupos"""
    model = Grupo
    template_name = 'grupo_list.html'


class GrupoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Grupo
    template_name = 'delete_grupo.html'

    def dispatch(self, request, *args, **kwargs):
        grupo = Grupo.objects.get(pk=self.kwargs['pk'])
        agentes = grupo.agentes.all()
        if agentes:
            message = ("No está permitido eliminar un grupo que tiene agentes")
            messages.warning(self.request, message)
            return HttpResponseRedirect(
                reverse('grupo_list'))
        return super(GrupoDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('grupo_list')


####################
# PAUSAS
####################
class PausaListView(TemplateView):
    """Vista para listar pausa"""
    model = Pausa
    template_name = 'pausa_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PausaListView, self).get_context_data(**kwargs)
        context['pausas_activas'] = Pausa.objects.activas()
        context['pausas_eliminadas'] = Pausa.objects.eliminadas()
        return context


class SincronizarPausaMixin(object):

    def get_success_url(self):
        return reverse('pausa_list')

    def form_valid(self, form):
        self.object = form.save()
        self.sincronizar(self.object, self.request)
        return super(SincronizarPausaMixin, self).form_valid(form)

    def sincronizar(self, pausa, request, eliminar=False):
        sincronizador = SincronizadorDeConfiguracionPausaAsterisk()
        try:
            if eliminar:
                sincronizador.eliminar_y_regenerar_asterisk(pausa)
                message = (_(u"La pausa se ha elimiado exitosamente."))
            else:
                sincronizador.regenerar_asterisk(pausa)
                message = (_(u"La pausa se ha guardado exitosamente."))
            messages.add_message(self.request, messages.SUCCESS, message)
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("Operación Errónea! "
                       "No se realizo de manera correcta la sincronización de los  "
                       "datos en asterisk según el siguiente error: {0}".format(e))
            messages.add_message(self.request, messages.WARNING, message)


class PausaCreateView(SincronizarPausaMixin, CreateView):
    """Vista para crear pausa"""
    model = Pausa
    template_name = 'base_create_update_form.html'
    form_class = PausaForm


class PausaUpdateView(SincronizarPausaMixin, UpdateView):
    """Vista para modificar pausa"""
    model = Pausa
    template_name = 'base_create_update_form.html'
    form_class = PausaForm


class PausaToggleDeleteView(SincronizarPausaMixin, TemplateView):
    """
    Esta vista se encarga de la eliminación/activación del
    objeto pausa
    """
    template_name = 'delete_pausa.html'

    def get(self, request, pk):
        try:
            pausa = Pausa.objects.get(pk=pk)
        except Pausa.DoesNotExist:
            return redirect('pausa_list')
        return self.render_to_response({'object': pausa})

    def post(self, request, pk):
        try:
            pausa = Pausa.objects.get(pk=pk)
        except Pausa.DoesNotExist:
            return redirect('pausa_list')
        pausa.eliminada = not pausa.eliminada
        pausa.save()
        if pausa.eliminada:
            self.sincronizar(pausa, request, True)
        else:
            self.sincronizar(pausa, request)
        return redirect('pausa_list')


def node_view(request):
    """Esta vista renderiza la pantalla del agente"""
    registro = []
    campanas_preview_activas = []
    agente_profile = request.user.get_agente_profile()
    if request.user.is_authenticated() and agente_profile and not agente_profile.is_inactive:
        sip_usuario = request.user.generar_usuario(agente_profile.sip_extension)
        sip_password = request.user.generar_contrasena(sip_usuario)
        registro = DuracionDeLlamada.objects.filter(
            agente=request.user.get_agente_profile(),
            tipo_llamada__in=(DuracionDeLlamada.TYPE_INBOUND,
                              DuracionDeLlamada.TYPE_MANUAL)
        ).order_by("-fecha_hora_llamada")[:10]
        campanas_preview_activas = \
            agente_profile.has_campanas_preview_activas_miembro()
        context = {
            'pausas': Pausa.objects.activas,
            'registro': registro,
            'campanas_preview_activas': campanas_preview_activas,
            'agente_profile': agente_profile,
            'sip_usuario': sip_usuario,
            'sip_password': sip_password,
        }
        return render_to_response(
            'agente/base_agente.html',
            context,
            context_instance=RequestContext(request)
        )
    if agente_profile.is_inactive:
        message = ("El agente con el cuál ud intenta loguearse está inactivo, contactese con"
                   " su supervisor")
        messages.warning(request, message)
        logout(request)
    return HttpResponseRedirect(reverse('login'))


def mensajes_recibidos_enviado_remitente_view(request):
    remitente = request.GET['phoneNumber']
    service_sms = SmsManager()
    mensajes = service_sms.obtener_mensaje_enviado_recibido(remitente)
    response = JsonResponse(service_sms.
                            armar_json_mensajes_recibidos_enviados(mensajes),
                            safe=False)
    return response


def mensajes_recibidos_view(request):
    service_sms = SmsManager()
    mensajes = service_sms.obtener_mensajes_recibidos_por_remitente()
    response = JsonResponse(
        service_sms.armar_json_mensajes_recibidos_por_remitente(mensajes),
        safe=False
    )

    return response


def blanco_view(request):
    return render_to_response('blanco.html',
                              context_instance=RequestContext(request))


def nuevo_evento_agenda_view(request):
    """Vista get para insertar un nuevo evento en la agenda
        REVISAR si se usa esta vista si no es obsoleta. Referenciada en Calendar.js
    """
    agente = request.GET['agente']
    es_personal = request.GET['personal']
    fecha = request.GET['fechaEvento']
    fecha = convert_fecha_datetime(fecha)
    hora = request.GET['horaEvento']
    es_smart = request.GET['smart']
    medio_comunicacion = request.GET['channel']
    medio = request.GET['dirchan']
    descripcion = request.GET['descripcion']
    es_smart = convert_string_in_boolean(es_smart)
    es_personal = convert_string_in_boolean(es_personal)

    agenda = Agenda(fecha=fecha, hora=hora, es_smart=es_smart,
                    medio_comunicacion=medio_comunicacion,
                    descripcion=descripcion, es_personal=es_personal)

    # verifico el agente logueado
    try:
        agente_logueado = AgenteProfile.objects.get(pk=agente)
    except AgenteProfile.DoesNotExist:
        agente_logueado = request.user.get_agente_profile()

    if es_personal:
        agenda.agente = agente_logueado

    if int(medio_comunicacion) is Agenda.MEDIO_LLAMADA:
        agenda.telefono = medio
    elif int(medio_comunicacion) is Agenda.MEDIO_SMS:
        agenda.telefono = medio
    elif int(medio_comunicacion) is Agenda.MEDIO_EMAIL:
        agenda.email = medio

    agenda.save()
    response = JsonResponse({'status': 'OK'})
    return response


class AgenteEventosFormView(FormView):
    """Esta vista devuelve el listado de los eventos de agenda por agente"""
    model = AgenteProfile
    template_name = 'agente/agenda_agente.html'
    form_class = AgendaBusquedaForm

    def get(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.eventos.eventos_filtro_fecha('', '')
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos))

    def form_valid(self, form):
        fecha = form.cleaned_data.get('fecha')
        if fecha:
            fecha_desde, fecha_hasta = fecha.split('-')
            fecha_desde = convert_fecha_datetime(fecha_desde)
            fecha_hasta = convert_fecha_datetime(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.eventos.eventos_filtro_fecha(fecha_desde,
                                                                 fecha_hasta)
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos))


# TODO: Se puede Eliminar esta vista?
# def regenerar_asterisk_view(request):
#     """Vista para regenerar los archivos de asterisk"""
#     activacion_queue_service = RegeneracionAsteriskService()
#     try:
#         activacion_queue_service.regenerar()
#     except RestablecerDialplanError, e:
#         message = ("Operación Errónea! "
#                    "No se realizo de manera correcta la regeneracion de los "
#                    "archivos de asterisk al siguiente error: {0}".format(e))
#         messages.add_message(
#             request,
#             messages.ERROR,
#             message,
#         )
#     messages.success(request,
#                      'La regeneracion de los archivos de configuracion de'
#                      ' asterisk y el reload se hizo de manera correcta')
#     return render_to_response('regenerar_asterisk.html',
#                               context_instance=RequestContext(request))


def nuevo_duracion_llamada_view(request):
    """Vista para crear una nueva duracion de llamada"""
    agente = request.GET['agente']
    numero_telefono = request.GET['numero_telefono']
    tipo_llamada = request.GET['tipo_llamada']
    duracion = request.GET['duracion']

    agente = AgenteProfile.objects.get(pk=int(agente))
    DuracionDeLlamada.objects.create(agente=agente,
                                     numero_telefono=numero_telefono,
                                     tipo_llamada=tipo_llamada,
                                     duracion=duracion)
    ctx = {
        'registros': DuracionDeLlamada.objects.filter(
            agente=request.user.get_agente_profile(),
            tipo_llamada__in=(DuracionDeLlamada.TYPE_INBOUND,
                              DuracionDeLlamada.TYPE_MANUAL)).order_by(
            "-fecha_hora_llamada")[:10]
    }
    return render_to_response('agente/update_registros_llamadas.html', ctx,
                              context_instance=RequestContext(request))


def mensaje_chat_view(request):
    """Vistar para crear un nuevo mensaje de chat"""
    sender = request.GET['sender']
    to = request.GET['to']
    mensaje = request.GET['mensaje']
    chat = request.GET['chat']

    chat = Chat.objects.get(pk=int(chat))
    sender = User.objects.get(pk=int(sender))
    to = User.objects.get(pk=int(to))
    MensajeChat.objects.create(
        sender=sender, to=to, mensaje=mensaje, chat=chat)
    response = JsonResponse({'status': 'OK'})
    return response


def crear_chat_view(request):
    """Vista para crear un nuevo char"""
    agente = request.GET['agente']
    user = request.GET['user']
    agente = User.objects.get(pk=int(agente))
    user = User.objects.get(pk=int(user))
    chat = Chat.objects.create(agente=agente, user=user)
    response = JsonResponse({'status': 'OK', 'chat': chat.pk})
    return response


def supervision_url_externa(request):
    """Vista que redirect a la supervision externa de marce"""
    user = request.user
    if user.get_is_supervisor_normal() or user.get_is_supervisor_customer():
        supervisor = user.get_supervisor_profile()
        sip_extension = supervisor.sip_extension
        timestamp = user.generar_usuario(sip_extension).split(':')[0]
        sip_usuario = timestamp + ":" + str(sip_extension)
        supervisor.timestamp = timestamp
        supervisor.sip_password = request.user.generar_contrasena(sip_usuario)
        supervisor.save()
        url = settings.OML_SUPERVISION_URL + str(supervisor.pk)
        if supervisor.is_administrador:
            # TODO: Con los nuevos permisos nunca se puede dar este caso
            # Discutir si este caso de uso queda descartado
            url += "&es_admin=t"
        else:
            url += "&es_admin=f"
        return redirect(url)
    message = "Supervision: Funcion valida para usuario tipo supervisor!!!"
    messages.warning(request, message)
    return HttpResponseRedirect(reverse('index'))


# =============================================================================
# Acerca
# =============================================================================


class AcercaTemplateView(TemplateView):
    """
    Esta vista es para generar el Acerca de la app.
    """

    template_name = 'acerca/acerca.html'
    context_object_name = 'acerca'

    def get_context_data(self, **kwargs):
        context = super(
            AcercaTemplateView, self).get_context_data(**kwargs)

        context['branch'] = version.OML_BRANCH
        context['commit'] = version.OML_COMMIT
        context['fecha_deploy'] = version.OML_BUILD_DATE
        return context


# TEST para probar sitio externo
def profile_page(request, username):
    prueba = request.GET.get('q', '')
    print prueba
    return render_to_response('blanco.html',
                              context_instance=RequestContext(request))
