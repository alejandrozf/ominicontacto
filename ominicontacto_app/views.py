# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from services.sms_services import SmsManager
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import (
    User, AgenteProfile, Modulo, Grupo, Pausa, Contacto)
from ominicontacto_app.forms import (CustomUserCreationForm,
                                     CustomUserChangeForm, UserChangeForm,
                                     AgenteProfileForm)
from django.contrib.auth.forms import AuthenticationForm
from services.kamailio_service import KamailioService
from services.sms_services import SmsManager
from django.views.decorators.csrf import csrf_protect


# def mensajes_recibidos_view(request):
#
#     service_sms = SmsManager()
#     mensajes = service_sms.obtener_ultimo_mensaje_por_numero()
#     response = JsonResponse(service_sms.armar_json_mensajes_recibidos(mensajes))
#     return response


def index_view(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


def login_agente_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            if user.is_agente:
                login(request, user)
                return HttpResponseRedirect('/node/')

            else:
                message = 'Operación Errónea! \
                           El usuario con el cuál usted intenta loguearse' \
                          ' no es un agente.'
                messages.add_message(
                    request,
                    messages.ERROR,
                    message,
                )

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

    def get_success_url(self):
        return reverse('user_list')


class UserListView(ListView):
    model = User
    template_name = 'user/user_list.html'


class AgenteProfileCreateView(CreateView):
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'base_create_update_form.html'

    # def get_initial(self):
    #     initial = super(AgenteProfileCreateView, self).get_initial()
    #     initial.update({'user': self.kwargs['pk_user']})
    #     return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        usuario = User.objects.get(pk=self.kwargs['pk_user'])
        self.object.user = usuario

        self.object.save()
        kamailio_service = KamailioService()
        kamailio_service.crear_agente_kamailio(self.object)

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
        kamailio_service = KamailioService()
        kamailio_service.update_agente_kamailio(self.object)

        return super(AgenteProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_list')


class ModuloCreateView(CreateView):
    model = Modulo
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

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
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('grupo_list')


class GrupoListView(ListView):
    model = Grupo
    template_name = 'grupo_list.html'


class PausaCreateView(CreateView):
    model = Pausa
    template_name = 'base_create_update_form.html'
    fields = ('nombre',)

    def get_success_url(self):
        return reverse('pausa_list')


class PausaListView(ListView):
    model = Pausa
    template_name = 'pausa_list.html'


class ContactoCreateView(CreateView):
    model = Contacto
    template_name = 'contacto_create_update_form.html'
    fields = ('id_cliente', 'nombre', 'apellido', 'email', 'telefono', 'datos')

    def get_success_url(self):
        return reverse('contacto_list')


class ContactoListView(ListView):
    model = Contacto
    template_name = 'contacto_list.html'


def node_view(request):
    context = {
        'pausas': Pausa.objects.all,
    }
    return render_to_response('migracionnodejs/layout.html', context,
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

