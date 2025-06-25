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

import threading
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.utils.timezone import now

from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from constance import config as config_constance

from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from ominicontacto_app.services.wombat_service import WombatReloader


class ReiniciarWombat(APIView):
    """Reinicia el servicio de Wombat"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        state = config_constance.WOMBAT_DIALER_STATE
        msg = _('Refrescando. Espere al menos 15 segundos mientras finaliza el proceso.')
        if state in [WombatReloader.STATE_DOWN, WombatReloader.STATE_STARTING]:
            return Response(data={
                'status': 'ERROR',
                'OML-state': state,
                'message': msg
            })

        # Hilo para efectuar el restart
        reloader = WombatReloader()
        thread_restart = threading.Thread(
            target=reloader.reload,
            # args=[key_task, ]
        )
        thread_restart.setDaemon(True)
        thread_restart.start()
        return Response(data={
            'status': 'OK',
            'OML-state': WombatReloader.STATE_STARTING,
            'message': msg,
        })


class WombatState(APIView):
    """ Informa el estado del servicio de Wombat """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        service = WombatReloader()
        wd_state, real_state, uptime = service.synchronize_local_state()
        response_data = {
            'status': 'OK',
            'OML-state': config_constance.WOMBAT_DIALER_STATE,
            'state': real_state if real_state else 'ERROR',
        }
        if wd_state is not None:
            response_data['uptime'] = wombat_uptime_str()
        else:
            msg = _('Refrescando. Espere al menos 15 segundos mientras finaliza el proceso.')
            response_data['message'] = msg

        return Response(data=response_data)


class WombatStart(APIView):
    """ Envía orden de Start a Wombat """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        service = WombatReloader()
        response = service.force_start_dialer()
        response['OML-state'] = config_constance.WOMBAT_DIALER_STATE
        if response and 'state' in response:
            response['uptime'] = wombat_uptime_str()
            return Response(data=response)

        return Response({'state': 'ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WombatStop(APIView):
    """ Informa el estado del servicio de Wombat """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        if not config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
            raise PermissionDenied
        service = WombatReloader()
        state = service.stop_dialer()
        if state is None:
            return Response({'state': 'ERROR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            'status': 'OK',
            'state': state,
            'OML-state': state,
            'uptime': wombat_uptime_str()
        }

        return Response(data=response_data)


def wombat_uptime_str():
    uptime = now() - config_constance.WOMBAT_DIALER_UPDATE_DATETIME
    return str(uptime).split('.')[0]
