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

# APIs para visualizar destinos
from asgiref.sync import async_to_sync
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from ominicontacto_app.models import Campana, AgenteProfile
from whatsapp_app.models import ConfiguracionWhatsappCampana, ConversacionWhatsapp
from notification_app.notification import AgentNotifier


class ListSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    campaing = serializers.IntegerField()
    destination = serializers.IntegerField()


class AgenteListSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField(source='user_id')
    agent_full_name = serializers.CharField(source='user.username')
    status = serializers.CharField(source='estado')


class CampanaListSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(source='id')
    campaign_name = serializers.CharField(source='nombre')


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def _eligible_campaigns_for_conversation(self, conversation):
        return Campana.objects.filter(
            estado=Campana.ESTADO_ACTIVA,
            whatsapp_habilitado=True,
            configuracionwhatsapp__is_active=True,
            configuracionwhatsapp__linea=conversation.line,
        ).exclude(
            id=conversation.campana_id,
        ).distinct()

    @decorators.action(detail=False, methods=["get"], url_path='(?P<campana_pk>[^/.]+)/agents')
    def agents(self, request, campana_pk):
        try:
            # filtrar por permiso de whatsapp
            queryset = Campana.objects.get(id=campana_pk).obtener_agentes()
            if request.user.is_agente:
                queryset = queryset.exclude(user_id=request.user.id)
            serializer = AgenteListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener los agentes')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(
        detail=False, methods=["get"], url_path='(?P<conversation_pk>[^/.]+)/campaigns')
    def campaigns(self, request, conversation_pk):
        try:
            conversation = ConversacionWhatsapp.objects.select_related(
                'line'
            ).get(id=conversation_pk)
            serializer = CampanaListSerializer(
                self._eligible_campaigns_for_conversation(conversation),
                many=True,
            )
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except ConversacionWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion inválida')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las campañas')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(
        detail=False, methods=["post"])
    def to_agent(self, request):
        try:
            print("---->", request.data)
            chat_id = request.data.get('conversationId')
            agent_id = request.data.get('to')
            conversacion = ConversacionWhatsapp.objects.get(id=chat_id)
            agent = AgenteProfile.objects.get(user__id=agent_id)
            success = conversacion.otorgar_conversacion(agent, attended=False)
            if success:
                AgentNotifier().notify_whatsapp_chat_transfered(
                    request.user.username, agent_id, conversacion)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS),
                    status=status.HTTP_200_OK)
            return response.Response(
                data=get_response_data(
                    message=_('Error al tranferir conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al tranferir conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["post"])
    def to_campaign(self, request):
        try:
            chat_id = request.data.get('conversationId')
            campaign_id = request.data.get('to')
            conversation = ConversacionWhatsapp.objects.select_related(
                'line', 'campana'
            ).get(id=chat_id)
            campaign = self._eligible_campaigns_for_conversation(conversation).get(id=campaign_id)
            ConfiguracionWhatsappCampana.objects.get(
                campana=campaign,
                linea=conversation.line,
                is_active=True,
            )
            conversation.campana = campaign
            conversation.agent = None
            conversation.atendida = False
            conversation.is_active = True
            conversation.client = campaign.bd_contacto.contactos.filter(
                telefono=conversation.destination,
            ).last()
            conversation.save()
            for agent in AgenteProfile.objects.all():
                async_to_sync(AgentNotifier().notify_whatsapp_new_chat)(
                    agent.user_id,
                    conversation=conversation,
                )
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS),
                status=status.HTTP_200_OK)
        except ConversacionWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion inválida')),
                status=status.HTTP_404_NOT_FOUND)
        except (Campana.DoesNotExist, ConfiguracionWhatsappCampana.DoesNotExist):
            return response.Response(
                data=get_response_data(
                    message=_('Campaña inválida')),
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al tranferir conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
