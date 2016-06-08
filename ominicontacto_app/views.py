# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from services.sms_services import SmsManager
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


def mensajes_recibidos_view(request):

    service_sms = SmsManager()
    mensajes = service_sms.obtener_ultimo_mensaje_por_numero()
    response = JsonResponse(service_sms.armar_json_mensajes_recibidos(mensajes))
    return response


def index_view(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))
