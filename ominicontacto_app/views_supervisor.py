# -*- coding: utf-8 -*-

"""Aca en esta vista se crear el supervisor que es un perfil de usuario con su
sip extension y sip password"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, ListView
from ominicontacto_app.forms import SupervisorProfileForm
from ominicontacto_app.models import SupervisorProfile, User
from services.kamailio_service import KamailioService
from services.asterisk_service import ActivacionAgenteService,\
    RestablecerConfigSipError


import logging as logging_

logger = logging_.getLogger(__name__)


class SupervisorProfileCreateView(CreateView):
    """Vista para crear un usuario con perfil de supervisor"""
    model = SupervisorProfile
    template_name = 'base_create_update_form.html'
    form_class = SupervisorProfileForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        usuario = User.objects.get(pk=self.kwargs['pk_user'])
        self.object.user = usuario
        self.object.sip_extension = SupervisorProfile.objects.\
            obtener_ultimo_sip_extension()
        # se le genera un sip_password aleatorio
        self.object.sip_password = User.objects.make_random_password()
        self.object.save()
        kamailio_service = KamailioService()
        # FIXME = Crear servicio para crer un supervisor en kamailio-debian o renombrar el
        # metodo
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
        return super(SupervisorProfileCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('supervisor_list')


class SupervisorProfileUpdateView(UpdateView):
    """Vista para modificar el perfil de un usuario supervisor"""
    model = SupervisorProfile
    template_name = 'base_create_update_form.html'
    form_class = SupervisorProfileForm

    def get_success_url(self):
        return reverse('supervisor_list')


class SupervisorListView(ListView):
    """Vista lista los supervisores """
    model = SupervisorProfile
    template_name = 'supervisor_profile_list.html'
