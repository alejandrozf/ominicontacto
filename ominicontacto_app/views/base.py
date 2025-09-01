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

"""En este modulo se encuentran las vistas basicas del sistema,
"""

from __future__ import unicode_literals

import logging
import json

from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, datetime, make_aware
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.generic import TemplateView

from constance import config as config_constance

from defender import utils
from defender import config

from ominicontacto_app.models import (
    AgenteProfile, Pausa, AgendaContacto, User,
    ClienteWebPhoneProfile, ContactoListaRapida
)
from ominicontacto_app.services.agent.presence import AgentPresenceManager
from ominicontacto_app.services.kamailio_service import KamailioService
from ominicontacto_app.services.authentication.ldap import authenticate_in_ldap
from ominicontacto_app.utiles import fecha_local
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
        admin_registered = (
            config_constance.CLIENT_NAME != '' and config_constance.CLIENT_KEY != '')
        showRegisterPopUp = False
        if 'showRegisterPopUp' not in request.session.keys():
            if not admin_registered:
                showRegisterPopUp = True and config_constance.SUGGEST_REGISTER
            request.session['showRegisterPopUp'] = showRegisterPopUp
        else:
            showRegisterPopUp = False
        context = {
            'isAdmin': request.user.get_is_administrador(),
            'showRegisterPopUp': showRegisterPopUp,
            'registered': admin_registered,
        }
        return TemplateResponse(request, template_name, context)


def custom_authenticate(username, password):
    # Ver si corresponde usar django authenticate o ldap autenticate
    user = User.objects.filter(username=username).first()
    authentication = {
        'user': user,
        'ok': False,
        'service_error': False,
        'ldap': False,
    }
    if user is None or not user.is_active:
        user = None
    elif user.autenticar_con_ldap:
        authentication['ldap'] = True
        authentication_ok, service_error = authenticate_in_ldap(username, password)
        authentication['ok'] = authentication_ok
        authentication['service_error'] = service_error
        if not authentication_ok:
            user = None
    else:
        user = authenticate(username=username, password=password)
        authentication['ok'] = user is not None

    authentication['user'] = user
    return authentication


def login_view(request):
    detail = None
    user_is_blocked = False
    login_unsuccessful = False
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
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

        authentication = custom_authenticate(username=username, password=password)
        user = authentication['user']

        form = AuthenticationForm(request, data=request.POST)
        if not authentication['ldap']:
            if not authentication['ok'] or not form.is_valid():
                login_unsuccessful = True
        else:
            login_unsuccessful = not authentication['ok']

        user_not_blocked = True
        if not authentication['service_error']:
            utils.add_login_attempt_to_db(request, login_valid=not login_unsuccessful,
                                          username=username)
            user_not_blocked = utils.check_request(request, login_unsuccessful=login_unsuccessful,
                                                   username=username)
        else:
            messages.error(
                request, _('usuario/contraseña inválidos. Consulte con su administrador LDAP'))

        # TODO: Si es cliente webphone lo bloqueo
        if ClienteWebPhoneProfile.objects.filter(user__username=username).exists():
            user_is_blocked = True
            detail = _("Este tipo de usuario no puede loguearse en este momento.")

        if user_not_blocked and not user_is_blocked and not login_unsuccessful:
            if authentication['ok'] or form.is_valid():
                primer_log = user.last_login is None
                login(request, user)
                # Si es agente, se ignora el parámetro 'next'
                if user.is_agente:
                    presence_manager = AgentPresenceManager()
                    agente_profile = user.get_agente_profile()
                    presence_manager.fix_previous_open_session_logs(user, agente_profile)
                    user.set_session_key(request.session.session_key)
                    presence_manager.login(agente_profile)
                    return HttpResponseRedirect(reverse('consola_de_agente'))
                user.set_session_key(request.session.session_key)
                if user.get_supervisor_profile() is not None and primer_log:
                    return HttpResponseRedirect(reverse('user_change_password'))
                if 'next' in request.GET and request.GET.get('next') != reverse(
                        'api_agente_logout'):
                    return redirect(request.GET.get('next'))
                else:
                    return HttpResponseRedirect(reverse('index'))

    else:
        if request.user.is_authenticated and not request.user.borrado:
            if request.user.is_agente and request.user.get_agente_profile().is_inactive:
                form = AuthenticationForm(request)
                presence_manager = AgentPresenceManager()
                presence_manager.logout(user.get_agente_profile())
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
                if request.user.is_agente:
                    presence_manager = AgentPresenceManager()
                    presence_manager.logout(user.get_agente_profile())
                logout(request)
    context = {
        'form': form,
        'detail': detail,
        'user_is_blocked': user_is_blocked,
        'login_unsuccessful': login_unsuccessful,
    }
    template_name = 'registration/login.html'
    return TemplateResponse(request, template_name, context)


####################
# PAUSAS
####################
class PausaListView(TemplateView):
    """Vista para listar pausa"""
    template_name = 'pausa_list.html'


class ConjuntosDePausaListView(TemplateView):
    """Vista para listar los conjuntos de pausa"""
    template_name = 'conjuntos_de_pausas_list.html'


##################
# Vista de Agente
##################
class ConsolaAgenteView(AddSettingsContextMixin, TemplateView):
    template_name = "agente/base_agente.html"

    def dispatch(self, request, *args, **kwargs):
        agente_profile = request.user.get_agente_profile()
        presence_manager = AgentPresenceManager()
        if agente_profile is None:
            return redirect('index')
        if agente_profile.is_inactive:
            message = _("El agente con el cuál ud intenta loguearse está inactivo, contactese con"
                        " su supervisor")
            messages.warning(request, message)
            presence_manager.logout(agente_profile)
            logout(request)
            return redirect('login')

        presence_manager.enforce_login(agente_profile)
        return super(ConsolaAgenteView, self).dispatch(request, *args, **kwargs)

    def get_pausas(self, agent):
        pausas = []
        if agent.grupo.conjunto_de_pausa:
            for pause in agent.grupo.conjunto_de_pausa.pausas.all():
                if not pause.pausa.eliminada:
                    pausas.append({
                        'id': pause.pausa.id,
                        'name': pause.pausa.nombre,
                        'timeToEndPause': pause.time_to_end_pause
                    })
        else:
            for pause in Pausa.objects.activas():
                pausas.append({
                    'id': pause.id,
                    'name': pause.nombre,
                    'timeToEndPause': 0
                })
        pausas.append({
            'id': 'OW',
            'name': _('On-Whatsapp'),
            'timeToEndPause': 0
        })
        return pausas

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
        registros = LlamadaLog.objects.obtener_historico_llamadas_del_dia(agente_profile.id, hoy)
        campanas_preview_activas = \
            agente_profile.has_campanas_preview_activas_miembro()
        context['pausas'] = self.get_pausas(agente_profile)
        context['registros'] = registros
        context['tipos_salientes'] = LlamadaLog.TIPOS_LLAMADAS_SALIENTES
        context['event_fin_conexion'] = LlamadaLog.EVENTOS_FIN_CONEXION
        context['campanas_preview_activas'] = campanas_preview_activas
        context['agente_profile'] = agente_profile
        context['tiene_whatsapp'] = agente_profile.grupo.whatsapp_habilitado
        context['sip_usuario'] = sip_usuario
        context['sip_password'] = sip_password
        context['agentes'] = AgenteProfile.objects.obtener_activos().exclude(id=agente_profile.id)
        context['max_session_age'] = settings.SESSION_COOKIE_AGE
        context['video_domain'] = video_domain
        context['fechas_agendas_json'] = json.dumps(fechas_agendas)
        context['listas_rapidas'] = ContactoListaRapida.objects.all()
        context['dtmf_duration'] = settings.DTMF_DURATION
        context['dtmf_inter_tone_gap'] = settings.DTMF_INTER_TONE_GAP

        return context


class BlancoView(TemplateView):
    template_name = 'blanco.html'


class WebUI(TemplateView):
    """
    NOTICE: impl of url+view+template are hard-coded, but works for now
    """
    prefix = "webui"
    repath = f"{prefix}/(?P<name>[^/]+)/(?P<path>.+)"

    extra_context = {"prefix": prefix}
    template_name = "webui.html"
