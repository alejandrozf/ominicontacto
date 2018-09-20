# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Aca en esta vista se crear el supervisor que es un perfil de usuario con su
sip extension y sip password"""

from __future__ import unicode_literals

from formtools.wizard.views import SessionWizardView

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, ListView, DeleteView, RedirectView

from ominicontacto_app.forms import (
    CustomUserCreationForm, SupervisorProfileForm, UserChangeForm, AgenteProfileForm,
)

from ominicontacto_app.models import (
    SupervisorProfile, AgenteProfile, User, QueueMember, Modulo, Grupo,
)

from services.asterisk_service import ActivacionAgenteService, RestablecerConfigSipError


import logging as logging_

logger = logging_.getLogger(__name__)


def show_agente_profile_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(wizard.USER) or {}
    # check if the field ``is_agente`` was checked.
    return cleaned_data.get('is_agente', True)


def show_supervisor_profile_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(wizard.USER) or {}
    # check if the field ``is_supervisor`` was checked.
    return cleaned_data.get('is_supervisor', True)


class CustomUserWizard(SessionWizardView):
    USER = '0'
    SUPERVISOR = '1'
    AGENTE = '2'
    condition_dict = {SUPERVISOR: show_supervisor_profile_form_condition,
                      AGENTE: show_agente_profile_form_condition}
    form_list = [(USER, CustomUserCreationForm),
                 (SUPERVISOR, SupervisorProfileForm),
                 (AGENTE, AgenteProfileForm), ]
    template_name = "user/user_create_form.html"

    def _grupos_y_modulos_disponibles(self):
        modulos = Modulo.objects.all()
        grupos = Grupo.objects.all()
        return modulos.count() > 0 and grupos.count() > 0

    def dispatch(self, request, *args, **kwargs):
        if not self._grupos_y_modulos_disponibles():
            message = _(u"Para poder crear un Usuario Agente asegurese de contar con al menos "
                        "un Grupo y un Modulo cargados.")
            messages.warning(self.request, message)
        return super(CustomUserWizard, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(CustomUserWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.USER:
            context['titulo'] = _('Nuevo Usuario: Datos Básicos')
        elif self.steps.current == self.SUPERVISOR:
            context['titulo'] = _('Nuevo Usuario: Perfil de Supervisor')
        elif self.steps.current == self.AGENTE:
            context['titulo'] = _('Nuevo Usuario: Perfil de Agente')

        return context

    def get_form_kwargs(self, step):
        kwargs = super(CustomUserWizard, self).get_form_kwargs(step)
        if step == self.USER:
            # TODO: Limitar los tipos de Usuarios que puede crear segun el tipo de usuario
            # Admin y gerentes: Agentes y Supervisores
            # Supervisores: Agentes y ¿Supervisores?
            if not self._grupos_y_modulos_disponibles():
                kwargs['deshabilitar_agente'] = True
        if step == self.SUPERVISOR:
            kwargs['rol'] = SupervisorProfile.ROL_GERENTE
            # TODO: Limitar los roles que puede seleccionar segun el tipo de usuario
            # Admin: Todos - Gerentes: Supervisores y Clientes
            # Supervisores: ¿Clientes?
        if step == self.AGENTE:
            # TODO: Limitar los agentes y grupos que puede seleccionar segun el tipo de usuario
            kwargs['grupos_queryset'] = Grupo.objects.all()
            kwargs['modulos_queryset'] = Modulo.objects.all()
        return kwargs

    def _save_supervisor_form(self, user, form):
        supervisor = form.save(commit=False)

        rol = form.cleaned_data['rol']
        supervisor.is_administrador = False
        supervisor.is_customer = False
        if rol == SupervisorProfile.ROL_ADMINISTRADOR:
            supervisor.is_administrador = True
        elif rol == SupervisorProfile.ROL_CLIENTE:
            supervisor.is_customer = True

        supervisor.user = user
        supervisor.sip_extension = 1000 + user.id
        sip_extension = supervisor.sip_extension
        supervisor.timestamp = supervisor.user.generar_usuario(sip_extension).split(':')[0]
        timestamp = supervisor.timestamp
        sip_usuario = timestamp + ":" + str(sip_extension)
        supervisor.sip_password = supervisor.user.generar_contrasena(sip_usuario)
        supervisor.save()
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

    def _save_agente_form(self, user, form):
        agente_profile = form.save(commit=False)
        agente_profile.user = user
        agente_profile.sip_extension = 1000 + user.id
        agente_profile.reported_by = self.request.user
        agente_profile.save()
        agente_profile.modulos = form.cleaned_data['modulos']
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

    def done(self, form_list, **kwargs):
        # Ver el tipo de Usuario que se crea.
        user_form = form_list[int(self.USER)]
        user = user_form.save()

        # Como no se usan los dos formularios, el segundo formulario es el de agente o supervisor
        if user.is_supervisor:
            self._save_supervisor_form(user, form_list[1])
        elif user.is_agente:
            self._save_agente_form(user, form_list[1])
        return HttpResponseRedirect(reverse('user_list', kwargs={"page": 1}))


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


class SupervisorProfileUpdateView(UpdateView):
    """Vista para modificar el perfil de un usuario supervisor"""
    model = SupervisorProfile
    template_name = 'base_create_update_form.html'
    form_class = SupervisorProfileForm

    def get_form_kwargs(self):
        kwargs = super(SupervisorProfileUpdateView, self).get_form_kwargs()
        profile = self.get_object()
        if profile.is_administrador:
            kwargs['rol'] = SupervisorProfile.ROL_ADMINISTRADOR
        elif profile.is_customer:
            kwargs['rol'] = SupervisorProfile.ROL_CLIENTE
        else:
            kwargs['rol'] = SupervisorProfile.ROL_GERENTE
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        rol = form.cleaned_data['rol']
        self.object.is_administrador = False
        self.object.is_customer = False
        if rol == SupervisorProfile.ROL_ADMINISTRADOR:
            self.object.is_administrador = True
        elif rol == SupervisorProfile.ROL_CLIENTE:
            self.object.is_customer = True

        sip_extension = self.object.sip_extension
        self.object.timestamp = self.object.user.generar_usuario(sip_extension).split(':')[0]
        timestamp = self.object.timestamp
        sip_usuario = timestamp + ":" + str(sip_extension)
        self.object.sip_password = self.object.user.generar_contrasena(sip_usuario)
        self.object.save()
        return super(SupervisorProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('supervisor_list')


class SupervisorListView(ListView):
    """Vista lista los supervisores """
    model = SupervisorProfile
    template_name = 'supervisor_profile_list.html'

    def get_queryset(self):
        """Returns Supervisor excluyendo los borrados"""
        return SupervisorProfile.objects.exclude(borrado=True)


class AgenteListView(ListView):
    """Vista para listar los agentes"""
    model = AgenteProfile
    template_name = 'agente_profile_list.html'

    def get_context_data(self, **kwargs):
        context = super(AgenteListView, self).get_context_data(
            **kwargs)
        agentes = AgenteProfile.objects.exclude(borrado=True)

        # TODO: Limitar la lista a los agentes que tiene asignado
        # if self.request.user.is_authenticated() and self.request.user:
        #     user = self.request.user
        #     agentes = agentes.filter(reported_by=user)

        context['agentes'] = agentes
        return context


class AgenteProfileUpdateView(UpdateView):
    """Vista para modificar un agente"""
    model = AgenteProfile
    form_class = AgenteProfileForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return AgenteProfile.objects.get(pk=self.kwargs['pk_agenteprofile'])

    def get_form_kwargs(self):
        kwargs = super(AgenteProfileUpdateView, self).get_form_kwargs()
        kwargs['modulos_queryset'] = Modulo.objects.all()
        kwargs['grupos_queryset'] = Grupo.objects.all()
        return kwargs

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


class DesactivarAgenteView(RedirectView):
    """
    Esta vista actualiza el agente desactivandolo
    """

    pattern_name = 'agente_list'

    def get(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        agente.desactivar()
        return HttpResponseRedirect(reverse('agente_list'))


class ActivarAgenteView(RedirectView):
    """
    Esta vista actualiza el agente activandolo
    """

    pattern_name = 'agente_list'

    def get(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=self.kwargs['pk_agente'])
        agente.activar()
        return HttpResponseRedirect(reverse('agente_list'))
