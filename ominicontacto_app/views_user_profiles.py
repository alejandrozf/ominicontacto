# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Aca en esta vista se crear el supervisor que es un perfil de usuario con su
sip extension y sip password"""

from __future__ import unicode_literals
import json
from formtools.wizard.views import SessionWizardView

from import_export import resources
from import_export.fields import Field

from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import (
    View, UpdateView, ListView, DeleteView, RedirectView, FormView, TemplateView, )

from constance import config

from ominicontacto_app.forms import (
    CustomUserCreationForm, SupervisorProfileForm, UserChangeForm, AgenteProfileForm,
    ForcePasswordChangeForm,
)

from ominicontacto_app.models import (
    SupervisorProfile, AgenteProfile, ClienteWebPhoneProfile, User, QueueMember, Grupo,
)
from ominicontacto_app.permisos import PermisoOML
from ominicontacto_app.services.asterisk.redis_database import AgenteFamily

from ominicontacto_app.views_queue_member import activar_cola, remover_agente_cola_asterisk

from .services.asterisk_service import ActivacionAgenteService, RestablecerConfigSipError
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnectorError, \
    AmiManagerClient

import logging as logging_
import os
import csv

from notification_app.message import emsg

from utiles_globales import obtener_paginas

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
        self.crear_agentes_unicamente = False
        if 'create_agent' in kwargs:
            self.crear_agentes_unicamente = True
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

        agente_rol = Group.objects.filter(name=User.AGENTE).first()
        if agente_rol:
            context['AGENTE_ROL_ID'] = agente_rol.pk
        return context

    def get_form_kwargs(self, step):
        kwargs = super(CustomUserWizard, self).get_form_kwargs(step)
        if step == self.USER:
            # Gerentes no pueden crear Administradores
            # Supervisores solo pueden crear agentes.
            roles_queryset = Group.objects.all()
            if not self.request.user.get_is_administrador():
                roles_queryset = roles_queryset.exclude(name=User.ADMINISTRADOR)
            if not config.WEBPHONE_CLIENT_ENABLED:
                roles_queryset = roles_queryset.exclude(name=User.CLIENTE_WEBPHONE)
            if not self._grupos_disponibles():
                roles_queryset = roles_queryset.exclude(name=User.AGENTE)
            if self.crear_agentes_unicamente:
                roles_queryset = Group.objects.filter(name=User.AGENTE)

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

        if user.email:
            user._password = user_form.cleaned_data["password1"]
            emsg.create("user.created", user=user, request=self.request).send()

        return HttpResponseRedirect(reverse('user_list', kwargs={"page": 1}))


class CustomerUserUpdateView(UpdateView):
    """Vista para modificar un usuario"""
    model = User

    def dispatch(self, *args, **kwargs):
        self.force_password_change = False
        self.for_agent = False
        if 'change_password' in kwargs:
            self.force_password_change = True
        else:
            user = self.get_object()
            if 'for_agent' in kwargs:
                self.for_agent = True
                if not user.is_agente:
                    raise ValueError(_('URL incorrecta'))
            else:
                if user.is_agente:
                    raise ValueError(_('URL incorrecta'))
            if not self._can_edit_user(user):
                message = _('No tiene permiso para editar al usuario {}'.format(
                    user.get_full_name()))
                messages.warning(self.request, message)
                return HttpResponseRedirect(reverse('user_list', kwargs={"page": 1}))
        return super(CustomerUserUpdateView, self).dispatch(*args, **kwargs)

    def _can_edit_user(self, user):
        # Solo un administrador puede editar otro administrador
        if user.get_is_administrador() and not self.request.user.get_is_administrador():
            return False
        if self.for_agent:
            if self.request.user.is_supervisor:
                supervisor_profile = self.request.user.get_supervisor_profile()
                agente_profile = user.get_agente_profile()
                asignado = self.request.user.tiene_agente_asignado(agente_profile)
                creado = supervisor_profile.es_creador_de_agente(agente_profile)
                return asignado or creado
        return True

    def get_object(self, *args, **kwargs):
        if self.force_password_change:
            return self.request.user
        return super(CustomerUserUpdateView, self).get_object(*args, **kwargs)

    def get_template_names(self, *args, **kwargs):
        if self.force_password_change:
            return ['user/force_password_change.html', ]
        return ['user/user_create_update_form.html', ]

    def get_form_class(self, *args, **kwargs):
        if self.force_password_change:
            return ForcePasswordChangeForm
        return UserChangeForm

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

        if self.force_password_change:
            login(self.request, updated_user)
            updated_user.set_session_key(self.request.session.session_key)
        else:
            agente_profile = form.instance.get_agente_profile()
            if agente_profile:
                # generar archivos sip en asterisk
                asterisk_sip_service = ActivacionAgenteService()
                try:
                    asterisk_sip_service.activar_agente(agente_profile, preservar_status=True)
                except RestablecerConfigSipError as e:
                    message = _("<strong>¡Cuidado!</strong> "
                                "con el siguiente error{0} .".format(e))
                    messages.add_message(
                        self.request,
                        messages.WARNING,
                        message,
                    )

        if form.instance.email and form.cleaned_data["password1"]:
            form.instance._password = form.cleaned_data["password1"]
            emsg.create("user.password-updated", user=form.instance, request=self.request).send()

        messages.success(self.request,
                         _('El usuario fue actualizado correctamente'))

        return ret

    def get_success_url(self):
        if self.request.user.tiene_permiso_oml('user_list'):
            return reverse('user_list', kwargs={"page": 1})
        return reverse('index')


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
        self.for_agent = False
        user = self.get_object()
        if 'for_agent' in kwargs:
            self.for_agent = True
            if not user.is_agente:
                raise ValueError(_('URL incorrecta'))
        else:
            if user.is_agente:
                raise ValueError(_('URL incorrecta'))
        if not self._can_delete_user(user):
            message = _('No tiene permiso para eliminar al usuario {}'.format(
                user.get_full_name()))
            messages.warning(self.request, message)
            return HttpResponseRedirect(reverse('user_list', kwargs={"page": 1}))
        return super(UserDeleteView, self).dispatch(request, *args, **kwargs)

    def _can_delete_user(self, user):
        # Solo un administrador puede eliminar otro administrador
        if user.get_is_administrador() and not self.request.user.get_is_administrador():
            return False
        if self.for_agent:
            if self.request.user.is_supervisor:
                supervisor_profile = self.request.user.get_supervisor_profile()
                agente_profile = user.get_agente_profile()
                asignado = self.request.user.tiene_agente_asignado(agente_profile)
                creado = supervisor_profile.es_creador_de_agente(agente_profile)
                return asignado or creado
        return True

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
            try:
                client = AmiManagerClient()
                client.connect()
            except AMIManagerConnectorError:
                logger.exception(_("QueueRemove failed "))
            for queue_member in queues_member_agente:
                campana = queue_member.queue_name.campana
                remover_agente_cola_asterisk(campana, agente_profile, client)
            client.disconnect()
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

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        user = self.request.user
        context['modifica_perfil_agente'] = user.tiene_permiso_oml('agenteprofile_update')
        context['modifica_perfil_supervisor'] = user.tiene_permiso_oml('supervisor_update')
        context['edita_user'] = user.tiene_permiso_oml('user_update')
        context['elimina_user'] = user.tiene_permiso_oml('user_delete')
        context['edita_agente'] = user.tiene_permiso_oml('agent_update')
        context['elimina_agente'] = user.tiene_permiso_oml('agent_delete')
        context['numero_usuarios_activos'] = User.numero_usuarios_activos()
        if 'search' in self.request.GET:
            context['search'] = self.request.GET.get('search')
            context['search_url'] = '?search=' + context['search']

        obtener_paginas(context, 7)
        return context

    def get_queryset(self):
        """Returns user ordernado por id"""
        users = User.objects.exclude(borrado=True).order_by('id')
        if 'search' in self.request.GET:
            search = self.request.GET.get('search')
            users = users.annotate(full_name=Concat('first_name', V(' '), 'last_name')).\
                filter(Q(full_name__icontains=search) | Q(username__icontains=search))
        return users


class SupervisorProfileUpdateView(FormView):
    """Vista para modificar el Rol de un usuario con perfil supervisor"""
    model = SupervisorProfile
    template_name = 'base_create_update_form.html'
    form_class = SupervisorProfileForm

    def _puede_editar_profile(self):
        # Solo un administrador puede editar otro administrador
        if self.profile.is_administrador and not self.request.user.get_is_administrador():
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        self.profile = SupervisorProfile.objects.get(id=kwargs['pk'])
        if not self._puede_editar_profile():
            message = _('No tiene permiso para editar al usuario {}'.format(
                self.profile.user.get_full_name()))
            messages.warning(self.request, message)
            return HttpResponseRedirect(reverse('user_list', kwargs={"page": 1}))
        return super(SupervisorProfileUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SupervisorProfileUpdateView, self).get_form_kwargs()
        kwargs['rol'] = self.profile.user.rol
        excluidos = [User.AGENTE, User.CLIENTE_WEBPHONE]
        if not self.request.user.get_is_administrador():
            excluidos.append(User.ADMINISTRADOR)
        roles_de_supervision = Group.objects.exclude(name__in=excluidos)
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
        return reverse('supervisor_list', kwargs={"page": 1})


class SupervisorListView(ListView):
    """Vista lista los supervisores """
    model = SupervisorProfile
    template_name = 'usuarios_grupos/supervisor_profile_list.html'
    paginate_by = 40

    def get_context_data(self, **kwargs):
        context = super(SupervisorListView, self).get_context_data(
            **kwargs)
        supervisores = SupervisorProfile.objects.exclude(borrado=True)
        context['supervisores'] = supervisores

        obtener_paginas(context, 7)
        return context

    def get_queryset(self):
        """Returns user ordernado por id"""
        supervisores = SupervisorProfile.objects.exclude(borrado=True).order_by('id')
        if 'search' in self.request.GET:
            search = self.request.GET.get('search')
            supervisores = supervisores.annotate(
                user__full_name=Concat('user__first_name', V(' '), 'user__last_name')).\
                filter(Q(user__full_name__icontains=search) | Q(user__username__icontains=search))
        return supervisores


class AgenteListView(ListView):
    """Vista para listar los agentes"""
    model = AgenteProfile
    template_name = 'usuarios_grupos/agente_profile_list.html'

    def get_queryset(self):
        # TODO: Limitar la lista a los agentes que tiene asignado
        # if self.request.user.is_authenticated and self.request.user:
        #     user = self.request.user
        #     agentes = agentes.filter(reported_by=user)
        agentes = AgenteProfile.objects.exclude(borrado=True).order_by('id')
        return agentes.select_related('user', 'grupo')


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
        agente_family = AgenteFamily()
        agente_family.regenerar_family(agente)
        return HttpResponseRedirect(reverse('agente_list'))


class ClienteWebPhoneListView(ListView):
    """Vista para listar los Clientes WebPhone """
    model = ClienteWebPhoneProfile
    template_name = 'user/cliente_webphone_list.html'

    def _get_addon_version(self):
        if os.getenv('WEBPHONE_CLIENT_VERSION'):
            return os.getenv('WEBPHONE_CLIENT_VERSION')
        else:
            return "DEVENV"

    def get_context_data(self, **kwargs):
        context = super(ClienteWebPhoneListView, self).get_context_data(
            **kwargs)
        clientes = ClienteWebPhoneProfile.objects.exclude(borrado=True)

        # TODO: Limitar la lista a los clientes que tiene asignado

        context['clientes'] = clientes
        context['version'] = self._get_addon_version()
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


class UserResourceExport(resources.ModelResource):

    profile = Field()
    group = Field()

    def dehydrate_profile(self, user):
        return user.rol.name

    def dehydrate_group(self, user):
        if user.get_is_agente():
            return user.agenteprofile.grupo.nombre
        return ''

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'profile', 'group')
        export_order = ('id', 'username', 'first_name', 'last_name', 'profile', 'group')


class ExportCsvUsuariosView(View):

    def post(self, request, *args, **kwargs):
        filtro = request.POST.get('nombre_usuario', False)
        # ID, username, first name, last name,
        # Profile (Agente / Supervisor / Administrador o nombre del perfil custom)
        usuarios_activos = User.objects.filter(borrado=False)
        if filtro:
            usuarios_activos = usuarios_activos.annotate(
                full_name=Concat('first_name', V(' '), 'last_name')).\
                filter(Q(full_name__icontains=filtro) | Q(username__icontains=filtro))
        response = HttpResponse(content_type='text/csv')
        content_disposition = 'attachment; filename="active_users.csv"'
        response['Content-Disposition'] = content_disposition
        dataset = UserResourceExport().export(usuarios_activos)
        writer = csv.writer(response)
        columnas_headers = ('Id', 'Username', 'First Name', 'Last Name', 'Profile')
        writer.writerow(columnas_headers)
        for row in dataset:
            writer.writerow(row)
        return response
