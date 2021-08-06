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

"""En este modulo se encuentran las vistas basicas para inicializar el sistema,
usuarios, modulos, grupos, pausas

DT:Mover la creacion de agente a otra vista
"""

from __future__ import unicode_literals

import logging
import requests
import json

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now, datetime, make_aware
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.conf import settings
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
)

from constance import config as config_constance

from defender import utils
from defender import config

from ominicontacto_app.models import (
    User, AgenteProfile, Grupo, Pausa, AgendaContacto,
    Chat, MensajeChat, ClienteWebPhoneProfile, ContactoListaRapida
)
from ominicontacto_app.forms import PausaForm, GrupoForm, RegistroForm
from ominicontacto_app.services.kamailio_service import KamailioService
from ominicontacto_app.utiles import fecha_local
from ominicontacto_app import version
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    RestablecerConfiguracionTelefonicaError, SincronizadorDeConfiguracionPausaAsterisk)
from reportes_app.models import LlamadaLog

from utiles_globales import AddSettingsContextMixin

logger = logging.getLogger(__name__)


def index_view(request):
    template_name = "base.html"
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.user.is_agente:
            return HttpResponseRedirect(reverse('consola_de_agente'))
        return TemplateResponse(request, template_name)


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

        # TODO: Si es cliente webphone lo bloqueo
        if ClienteWebPhoneProfile.objects.filter(user__username=username).exists():
            user_is_blocked = True
            detail = _("Este tipo de usuario no puede loguearse en este momento.")

        if user_not_blocked and not user_is_blocked and not login_unsuccessful:
            if form.is_valid():
                primer_log = user.last_login is None
                login(request, user)
                user.set_session_key(request.session.session_key)
                if user.get_supervisor_profile() is not None and primer_log:
                    return HttpResponseRedirect(reverse('user_change_password'))
                if 'next' in request.GET and request.GET.get('next') != reverse(
                        'api_agente_logout'):
                    return redirect(request.GET.get('next'))
                if user.is_agente:
                    return HttpResponseRedirect(reverse('consola_de_agente'))
                else:
                    return HttpResponseRedirect(reverse('index'))

    else:
        if request.user.is_authenticated and not request.user.borrado:
            if request.user.is_agente and request.user.get_agente_profile().is_inactive:
                form = AuthenticationForm(request)
                logout(request)
            elif 'next' in request.GET:
                return redirect(request.GET.get('next'))
            elif request.user.is_agente:
                return HttpResponseRedirect(reverse('consola_de_agente'))
            else:
                return HttpResponseRedirect(reverse('index'))
        else:
            form = AuthenticationForm(request)
            if request.user.is_authenticated:
                logout(request)
    context = {
        'form': form,
        'detail': detail,
        'user_is_blocked': user_is_blocked,
    }
    template_name = 'registration/login.html'
    return TemplateResponse(request, template_name, context)


####################
# GRUPOS
####################
class GrupoCreateView(CreateView):
    """Vista para crear un grupo
    DT: eliminar fields de la vista crear un form para ello
    """
    model = Grupo
    template_name = 'usuarios_grupos/grupo_create_update.html'
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
    template_name = 'usuarios_grupos/grupo_create_update.html'
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
    template_name = 'usuarios_grupos/grupo_list.html'


class GrupoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación del
    objeto grupo
    """
    model = Grupo
    template_name = 'usuarios_grupos/delete_grupo.html'

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
        except RestablecerConfiguracionTelefonicaError as e:
            message = _("Operación Errónea! "
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


##################
# Vista de Agente
##################

class ConsolaAgenteView(AddSettingsContextMixin, TemplateView):
    template_name = "agente/base_agente.html"

    def dispatch(self, request, *args, **kwargs):
        agente_profile = request.user.get_agente_profile()
        if agente_profile.is_inactive:
            message = _("El agente con el cuál ud intenta loguearse está inactivo, contactese con"
                        " su supervisor")
            messages.warning(request, message)
            logout(request)
            return redirect('login')

        return super(ConsolaAgenteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ConsolaAgenteView, self).get_context_data(**kwargs)
        campanas_preview_activas = []
        usuario_agente = self.request.user
        agente_profile = usuario_agente.get_agente_profile()
        kamailio_service = KamailioService()
        sip_usuario = kamailio_service.generar_sip_user(agente_profile.sip_extension)
        sip_password = kamailio_service.generar_sip_password(sip_usuario)
        video_domain = ''
        if 'WEBPHONE_VIDEO_DOMAIN' in settings.CONSTANCE_CONFIG:
            video_domain = config_constance.WEBPHONE_VIDEO_DOMAIN
        fechas_agendas = AgendaContacto.objects.proximas(agente_profile).values_list(
            'fecha', 'hora')
        fechas_agendas = [
            make_aware(datetime.combine(x[0], x[1])).isoformat() for x in fechas_agendas]

        hoy = fecha_local(now())
        registros = LlamadaLog.objects.obtener_llamadas_finalizadas_del_dia(agente_profile.id, hoy)
        campanas_preview_activas = \
            agente_profile.has_campanas_preview_activas_miembro()
        context['pausas'] = Pausa.objects.activas
        context['registros'] = registros
        context['tipos_salientes'] = LlamadaLog.TIPOS_LLAMADAS_SALIENTES
        context['campanas_preview_activas'] = campanas_preview_activas
        context['agente_profile'] = agente_profile
        context['sip_usuario'] = sip_usuario
        context['sip_password'] = sip_password
        context['agentes'] = AgenteProfile.objects.obtener_activos().exclude(id=agente_profile.id)
        context['max_session_age'] = settings.SESSION_COOKIE_AGE
        context['video_domain'] = video_domain
        context['fechas_agendas_json'] = json.dumps(fechas_agendas)
        context['listas_rapidas'] = ContactoListaRapida.objects.all()

        return context


class BlancoView(TemplateView):
    template_name = 'blanco.html'


# =============================================================================
# Acerca
# =============================================================================

class AcercaTemplateView(TemplateView):
    """
    Esta vista es para generar el Acerca de la app.
    """

    template_name = 'acerca/acerca.html'

    def get_context_data(self, **kwargs):
        context = super(
            AcercaTemplateView, self).get_context_data(**kwargs)

        context['branch'] = version.OML_BRANCH
        context['commit'] = version.OML_COMMIT
        context['fecha_deploy'] = version.OML_BUILD_DATE
        return context


class RegistroFormView(FormView):
    """Vista que se encarga de registrar un usuario en el servidor de llaves y crear al usuario
    settings para que los pueda usar en los accesos a funcionalidades
    """

    template_name = 'registro.html'
    form_class = RegistroForm

    def get_success_url(self):
        return reverse('registrar_usuario')

    def get_context_data(self, **kwargs):
        context = super(RegistroFormView, self).get_context_data(**kwargs)
        registered = (config_constance.CLIENT_NAME != '' and config_constance.CLIENT_KEY != '')
        context['registered'] = registered
        return context

    def _create_credentials(self, form):
        create_url = '{0}/retrieve_key/'.format(config_constance.KEYS_SERVER_HOST)
        try:
            client = form.cleaned_data['nombre']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            telefono = form.cleaned_data['telefono']
        except AttributeError:
            msg = _('No tiene settings de conexion configurados')
            logger.error(msg)
            return {'status': 'ERROR', 'msg': msg}
        post_data = {'client': client, 'password': password, 'email': email, 'phone': telefono}
        try:
            result = requests.post(
                create_url, json=post_data, verify=config_constance.SSL_CERT_FILE)
        except requests.exceptions.RequestException as e:
            msg = _('Error en el intento de conexion a: {0} debido {1}'.format(create_url, e))
            logger.error(msg)
            return {'status': 'ERROR', 'msg': msg}
        return result.json()

    def form_valid(self, form):
        result = self._create_credentials(form)
        if result['status'] == 'ERROR':
            message = result['msg']
            messages.error(self.request, message)
            return render(self.request, 'registro.html', {'form': form})
        message = _('Registro exitoso, se le ha enviado un e-mail con su llave de registro.')
        messages.success(self.request, message)
        config_constance.CLIENT_NAME = result['user_name']
        config_constance.CLIENT_PASSWORD = form.cleaned_data['password']
        config_constance.CLIENT_KEY = result['user_key']
        config_constance.CLIENT_EMAIL = result['user_email']
        config_constance.CLIENT_PHONE = result['user_phone']
        return super(RegistroFormView, self).form_valid(form)


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


class AddonsInfoView(TemplateView):
    """Vista que se muestra todos los addons disponibles
    """

    template_name = 'addons.html'

    def _obtener_datos_addons(self):
        addons_info_url = '{0}/addons/info'.format(config_constance.KEYS_SERVER_HOST)
        try:
            info_addons = requests.get(addons_info_url, verify=config_constance.SSL_CERT_FILE)
        except requests.RequestException as e:
            logger.info(_("No se pudo acceder a la url debido a: {0}".format(e)))
            return []
        else:
            info_addons_list = info_addons.json()['data']
            return info_addons_list

    def get_context_data(self, **kwargs):
        context = super(AddonsInfoView, self).get_context_data(**kwargs)
        context['addons_info'] = self._obtener_datos_addons()
        return context
