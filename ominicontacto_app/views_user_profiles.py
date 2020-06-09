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
import json
from formtools.wizard.views import SessionWizardView

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import (
    UpdateView, ListView, DeleteView, RedirectView, FormView, TemplateView, )

from constance import config

from ominicontacto_app.forms import (
    CustomUserCreationForm, SupervisorProfileForm, UserChangeForm, AgenteProfileForm,
)

from ominicontacto_app.models import (
    SupervisorProfile, AgenteProfile, ClienteWebPhoneProfile, User, QueueMember, Grupo,
)
from ominicontacto_app.permisos import PermisoOML

from ominicontacto_app.views_queue_member import activar_cola, remover_agente_cola_asterisk

from .services.asterisk_service import ActivacionAgenteService, RestablecerConfigSipError


import logging as logging_

logger = logging_.getLogger(__name__)


def show_agente_profile_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(wizard.USER) or {}
    rol = cleaned_data.get('rol')
    if rol:
        return rol.name == User.AGENTE


class CustomUserWizard(SessionWizardView):
    USER = '0'
    AGENTE = '1'
    condition_dict = {AGENTE: show_agente_profile_form_condition}
    form_list = [(USER, CustomUserCreationForm),
                 (AGENTE, AgenteProfileForm), ]
    template_name = "user/user_create_form.html"

    def _grupos_disponibles(self):
        grupos = Grupo.objects.all()
        return grupos.count() > 0

    def dispatch(self, request, *args, **kwargs):
        if not self._grupos_disponibles():
            message = _(u"Para poder crear un Usuario Agente asegurese de contar con al menos "
                        "un Grupo cargado.")
            messages.warning(self.request, message)
        return super(CustomUserWizard, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(CustomUserWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.USER:
            context['titulo'] = _('Nuevo Usuario: Datos Básicos')
        elif self.steps.current == self.AGENTE:
            context['titulo'] = _('Nuevo Usuario: Perfil de Agente')

        return context

    def get_form_kwargs(self, step):
        kwargs = super(CustomUserWizard, self).get_form_kwargs(step)
        if step == self.USER:
            # TODO: Limitar los tipos de Usuarios que puede crear segun el tipo de usuario
            # Admin y gerentes: Agentes y Supervisores
            # Supervisores: Agentes y ¿Supervisores?
            roles_queryset = Group.objects.all()
            if not config.WEBPHONE_CLIENT_ENABLED:
                roles_queryset = roles_queryset.exclude(name=User.CLIENTE_WEBPHONE)
            if not self._grupos_disponibles():
                roles_queryset = roles_queryset.exclude(name=User.AGENTE)

            kwargs['roles_queryset'] = roles_queryset

        if step == self.AGENTE:
            # TODO: Limitar los agentes y grupos que puede seleccionar segun el tipo de usuario
            kwargs['grupos_queryset'] = Grupo.objects.all()
        return kwargs

    def _save_supervisor(self, user, rol):
        sip_extension = 1000 + user.id
        is_administrador = rol.name == User.ADMINISTRADOR
        is_customer = rol.name == User.REFERENTE
        supervisor = SupervisorProfile(
            user=user,
            sip_extension=sip_extension,
            is_administrador=is_administrador,
            is_customer=is_customer
        )
        supervisor.save()

        asterisk_sip_service = ActivacionAgenteService()
        try:
            asterisk_sip_service.activar(regenerar_families=False)
        except RestablecerConfigSipError as e:
            message = _("<strong>¡Cuidado!</strong> "
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
        # generar archivos sip en asterisk
        asterisk_sip_service = ActivacionAgenteService()
        try:
            asterisk_sip_service.activar_agente(agente_profile)
        except RestablecerConfigSipError as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error{0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

    def _save_cliente_webphone(self, user):
        sip_extension = 1000 + user.id
        cliente_webphone = ClienteWebPhoneProfile(user=user, sip_extension=sip_extension)
        cliente_webphone.save()

        asterisk_sip_service = ActivacionAgenteService()
        try:
            asterisk_sip_service.activar(regenerar_families=False)
        except RestablecerConfigSipError as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error{0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

    def done(self, form_list, **kwargs):
        # Ver el tipo de Usuario que se crea.
        # TODO: ver como convertir de forma mas elegante un odict_values a lista
        # en python3
        form_list = [i for i in form_list]
        user_form = form_list[int(self.USER)]
        rol = user_form.cleaned_data.get('rol')
        user = user_form.save(commit=False)
        user.is_agente = rol.name == User.AGENTE
        user.is_cliente_webphone = rol.name == User.CLIENTE_WEBPHONE
        user.is_supervisor = rol.name not in (User.AGENTE, User.CLIENTE_WEBPHONE)
        user.save()
        user.groups.add(rol)

        if rol.name == User.AGENTE:
            self._save_agente_form(user, form_list[1])
        elif rol.name == User.CLIENTE_WEBPHONE:
            self._save_cliente_webphone(user)
        else:
            self._save_supervisor(user, rol)

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
                         _('El usuario fue actualizado correctamente'))

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
        if usuario.id == 1:
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
            agente_profile = self.object.get_agente_profile()
            agente_profile.borrar()
            # ahora vamos a remover el agente de la cola de asterisk
            queues_member_agente = agente_profile.campana_member.all()
            for queue_member in queues_member_agente:
                campana = queue_member.queue_name.campana
                remover_agente_cola_asterisk(campana, agente_profile)
            activar_cola()
            QueueMember.objects.borrar_member_queue(agente_profile)

        if self.object.is_supervisor and self.object.get_supervisor_profile():
            self.object.get_supervisor_profile().borrar()
        if self.object.is_cliente_webphone and self.object.get_cliente_webphone_profile():
            self.object.get_cliente_webphone_profile().borrar()
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


class SupervisorProfileUpdateView(FormView):
    """Vista para modificar el Rol de un usuario con perfil supervisor"""
    model = SupervisorProfile
    template_name = 'base_create_update_form.html'
    form_class = SupervisorProfileForm

    # TODO: Dispatch - Verificar si tiene permisos para editar al usuario segun el rol.
    def dispatch(self, request, *args, **kwargs):
        self.profile = SupervisorProfile.objects.get(id=kwargs['pk'])
        return super(SupervisorProfileUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SupervisorProfileUpdateView, self).get_form_kwargs()
        kwargs['rol'] = self.profile.user.rol
        roles_de_supervision = Group.objects.exclude(name__in=[User.AGENTE, User.CLIENTE_WEBPHONE])
        kwargs['roles_de_supervisores_queryset'] = roles_de_supervision
        return kwargs

    def form_valid(self, form):
        rol = form.cleaned_data['rol']
        self.profile.is_administrador = rol.name == User.ADMINISTRADOR
        self.profile.is_customer = rol.name == User.REFERENTE
        self.profile.user.groups.set([rol])
        self.profile.save()
        return super(SupervisorProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('supervisor_list')


class SupervisorListView(ListView):
    """Vista lista los supervisores """
    model = SupervisorProfile
    template_name = 'usuarios_grupos/supervisor_profile_list.html'

    def get_queryset(self):
        """Returns Supervisor excluyendo los borrados"""
        return SupervisorProfile.objects.exclude(borrado=True)


class AgenteListView(ListView):
    """Vista para listar los agentes"""
    model = AgenteProfile
    template_name = 'usuarios_grupos/agente_profile_list.html'

    def get_context_data(self, **kwargs):
        context = super(AgenteListView, self).get_context_data(
            **kwargs)
        agentes = AgenteProfile.objects.exclude(borrado=True)

        # TODO: Limitar la lista a los agentes que tiene asignado
        # if self.request.user.is_authenticated and self.request.user:
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
        kwargs['grupos_queryset'] = Grupo.objects.all()
        return kwargs

    def form_valid(self, form):
        self.object = form.save()

        asterisk_sip_service = ActivacionAgenteService()
        try:
            # Como solo puede cambiar el grupo no impacta en AstDB
            asterisk_sip_service.activar(regenerar_families=False)
        except RestablecerConfigSipError as e:
            message = _("<strong>¡Cuidado!</strong> "
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


class ClienteWebPhoneListView(ListView):
    """Vista para listar los Clientes WebPhone """
    model = ClienteWebPhoneProfile
    template_name = 'user/cliente_webphone_list.html'

    def get_context_data(self, **kwargs):
        context = super(ClienteWebPhoneListView, self).get_context_data(
            **kwargs)
        clientes = ClienteWebPhoneProfile.objects.exclude(borrado=True)

        # TODO: Limitar la lista a los clientes que tiene asignado

        context['clientes'] = clientes
        return context


class ToggleActivarClienteWebPhoneView(RedirectView):
    """
    Esta vista cambia el estado de activacion de un Cliente WebPhone
    """

    def get(self, request, *args, **kwargs):
        cliente = ClienteWebPhoneProfile.objects.get(pk=self.kwargs['pk'])
        cliente.toggle_is_inactive()
        if cliente.is_inactive:
            msg = _('El Cliente WebPhone fue desactivado')
        else:
            msg = _('El Cliente WebPhone fue activado')
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('cliente_webphone_list'))


class UserRoleManagementView(TemplateView):
    template_name = 'user/user_role_management.html'

    def _get_informacion_de_roles(self):
        roles = []
        roles_inmutables = [
            User.ADMINISTRADOR, User.GERENTE, User.SUPERVISOR, User.REFERENTE, User.AGENTE,
            User.CLIENTE_WEBPHONE]
        for rol in Group.objects.all():
            roles.append({
                'id': rol.id,
                'is_immutable': rol.name in roles_inmutables,
                'name': rol.name,  # TODO: Mostrar nombres de Roles de OML traducidos
                'permissions': list(rol.permissions.values_list('id', flat=True))
            })
        return roles

    def get_context_data(self, **kwargs):
        context = super(UserRoleManagementView, self).get_context_data(**kwargs)
        # Necesita Lista de permisos
        context['roles'] = json.dumps(self._get_informacion_de_roles())
        context['permisos'] = json.dumps(dict(PermisoOML.objects.values_list('id', 'name')))
        return context
