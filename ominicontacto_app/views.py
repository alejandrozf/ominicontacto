# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from services.sms_services import SmsManager
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import (User, AgenteProfile, Modulo, Grupo, Pausa)
from ominicontacto_app.forms import (CustomUserCreationForm,
                                     CustomUserChangeForm, UserChangeForm,
                                     AgenteProfileForm)
from services.kamailio_service import KamailioService


def mensajes_recibidos_view(request):

    service_sms = SmsManager()
    mensajes = service_sms.obtener_ultimo_mensaje_por_numero()
    response = JsonResponse(service_sms.armar_json_mensajes_recibidos(mensajes))
    return response


def index_view(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))


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

