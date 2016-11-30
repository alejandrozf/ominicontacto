# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from services.sms_services import SmsManager
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from ominicontacto_app.models import (
    User, AgenteProfile, Modulo, Grupo, Pausa, DuracionDeLlamada, Agenda
)
from ominicontacto_app.forms import (
    CustomUserCreationForm, CustomUserChangeForm, UserChangeForm,
    AgenteProfileForm, AgendaBusquedaForm
)
from django.contrib.auth.forms import AuthenticationForm
from services.kamailio_service import KamailioService
from services.sms_services import SmsManager
from services.asterisk_service import ActivacionAgenteService,\
    RestablecerConfigSipError
from services.regeneracion_asterisk import RegeneracionAsteriskService,\
    RestablecerDialplanError
from django.views.decorators.csrf import csrf_protect
from ominicontacto_app.utiles import convert_string_in_boolean,\
    convert_fecha_datetime, convert_fecha_datetime_2


# def mensajes_recibidos_view(request):
#
#     service_sms = SmsManager()
#     mensajes = service_sms.obtener_ultimo_mensaje_por_numero()
#     response = JsonResponse(service_sms.armar_json_mensajes_recibidos(mensajes))
#     return response


def index_view(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, user)
            if user.is_agente:
                return HttpResponseRedirect(reverse('view_node'))
            else:
                return HttpResponseRedirect(reverse('index'))

    else:
        form = AuthenticationForm(request)

    context = {
        'form': form,
    }
    template_name = 'registration/login.html'
    return TemplateResponse(request, template_name, context)


class CustomerUserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user/user_create_update_form.html'

    def get_success_url(self):
        return reverse('user_list')


class CustomerUserUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'user/user_create_update_form.html'

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
        return reverse('user_list')


class UserDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto user
    """
    model = AgenteProfile
    template_name = 'user/delete_user.html'

    def get_object(self, queryset=None):
     return User.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('user_list')


class UserListView(ListView):
    model = User
    template_name = 'user/user_list.html'


class AgenteProfileCreateView(CreateView):
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
            message = ("Debe cargar un grupo antes de crear un perfil de agente"
                       )
            messages.warning(self.request, message)
        return super(AgenteProfileCreateView, self).dispatch(request, *args,
                                                             **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        usuario = User.objects.get(pk=self.kwargs['pk_user'])
        self.object.user = usuario
        self.object.sip_extension = AgenteProfile.objects.\
            obtener_ultimo_sip_extension()
        self.object.sip_password = User.objects.make_random_password()
        self.object.save()
        kamailio_service = KamailioService()
        kamailio_service.crear_agente_kamailio(self.object)
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
        return reverse('user_list')


class AgenteProfileUpdateView(UpdateView):
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agenteprofile'])

    def form_valid(self, form):
        self.object = form.save()
        kamailio_service = KamailioService()
        kamailio_service.update_agente_kamailio(self.object)
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
        return reverse('user_list')


class ModuloCreateView(CreateView):
    model = Modulo
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloUpdateView(UpdateView):
    model = Modulo
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Modulo
    template_name = 'delete_modulo.html'

    def get_success_url(self):
        return reverse('modulo_list')


class ModuloListView(ListView):
    model = Modulo
    template_name = 'modulo_list.html'


class AgenteListView(ListView):
    model = AgenteProfile
    template_name = 'agente_profile_list.html'


class GrupoCreateView(CreateView):
    model = Grupo
    template_name = 'base_create_update_form.html'
    fields = ('nombre', 'auto_attend_ics', 'auto_attend_inbound',
              'auto_attend_dialer', 'auto_pause')

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoUpdateView(UpdateView):
    model = Grupo
    template_name = 'base_create_update_form.html'
    fields = ('nombre', 'auto_attend_ics', 'auto_attend_inbound',
              'auto_attend_dialer', 'auto_pause')

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoListView(ListView):
    model = Grupo
    template_name = 'grupo_list.html'


class GrupoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Grupo
    template_name = 'delete_grupo.html'

    def get_success_url(self):
        return reverse('grupo_list')


class PausaCreateView(CreateView):
    model = Pausa
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('pausa_list')


class PausaUpdateView(UpdateView):
    model = Pausa
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('pausa_list')


class PausaListView(ListView):
    model = Pausa
    template_name = 'pausa_list.html'


class PausaDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto pausa
    """
    model = Pausa
    template_name = 'delete_pausa.html'

    def get_success_url(self):
        return reverse('pausa_list')


def node_view(request):
    context = {
        'pausas': Pausa.objects.all,
    }
    return render_to_response('agente/base_agente.html', context,
                              context_instance=RequestContext(request))


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
    response = JsonResponse(service_sms.
                            armar_json_mensajes_recibidos_por_remitente(mensajes),
                            safe=False)
    return response


def blanco_view(request):
    return render_to_response('blanco.html',
                              context_instance=RequestContext(request))


def nuevo_evento_agenda_view(request):
    agente = request.GET['agente']
    es_personal = request.GET['personal']
    fecha = request.GET['fechaEvento']
    fecha = convert_fecha_datetime_2(fecha)
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
            fecha_desde = convert_fecha_datetime_2(fecha_desde)
            fecha_hasta = convert_fecha_datetime_2(fecha_hasta)
        else:
            fecha_desde = ''
            fecha_hasta = ''
        agente = self.request.user.get_agente_profile()
        listado_de_eventos = agente.eventos.eventos_filtro_fecha(fecha_desde,
                                                                 fecha_hasta)
        return self.render_to_response(self.get_context_data(
            listado_de_eventos=listado_de_eventos))


def regenerar_asterisk_view(request):
    activacion_queue_service = RegeneracionAsteriskService()
    try:
        activacion_queue_service.regenerar()
    except RestablecerDialplanError, e:
        message = ("Operación Errónea! "
                   "No se realizo de manera correcta la regeneracion de los "
                   "archivos de asterisk al siguiente error: {0}".format(e))
        messages.add_message(
            request,
            messages.ERROR,
            message,
        )
    messages.success(request,
                     'La regeneracion de los archivos de configuracion de'
                     ' asterisk y el reload se hizo de manera correcta')
    return render_to_response('regenerar_asterisk.html',
                              context_instance=RequestContext(request))


def nuevo_duracion_llamada_view(request):
    agente = request.GET['agente']
    numero_telefono = request.GET['numero_telefono']
    tipo_llamada = request.GET['tipo_llamada']
    duracion = request.GET['duracion']

    agente = AgenteProfile.objects.get(pk=int(agente))
    DuracionDeLlamada.objects.create(agente=agente,
                                     numero_telefono=numero_telefono,
                                     tipo_llamada=tipo_llamada,
                                     duracion=duracion)
    response = JsonResponse({'status': 'OK'})
    return response
