# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from services.sms_services import SmsManager
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView
from ominicontacto_app.models import (User, AgenteProfile)
from ominicontacto_app.forms import (CustomUserCreationForm,
                                     CustomUserChangeForm, UserChangeForm,
                                     AgenteProfileForm)



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
    template_name = 'user/user_creation_form.html'

    def get_success_url(self):
        return reverse('user_list')


class CustomerUserUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'user/user_creation_form.html'

    def get_success_url(self):
        return reverse('user_list')


class UserListView(ListView):
    model = User
    template_name = 'user/user_list.html'


class AgenteProfileCreateView(CreateView):
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'user/user_creation_form.html'

    def get_initial(self):
        initial = super(AgenteProfileCreateView, self).get_initial()
        initial.update({'user': self.kwargs['pk_user']})
        return initial

    def get_success_url(self):
        return reverse('user_list')

