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
import uuid
from asgiref.sync import async_to_sync
from django.db import transaction
from django.utils import timezone
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
from whatsapp_app.models import ConfiguracionWhatsappCampana, ConversacionWhatsapp, MensajeWhatsapp
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


def _build_agent_snapshot(agent):
    if not agent:
        return None
    username = agent.user.username
    full_name = agent.user.get_full_name()
    return {
        'id': agent.user_id,
        'username': username,
        'name': full_name or username,
    }


def _build_campaign_snapshot(campaign):
    if not campaign:
        return None
    return {
        'id': campaign.id,
        'name': campaign.nombre,
    }


def _create_transfer_event_message(conversation, event_type, by_agent=None, to_agent=None,
                                   to_campaign=None):
    timestamp = timezone.now().astimezone(timezone.get_current_timezone())
    MensajeWhatsapp.objects.create(
        message_id='transfer-event-{}'.format(uuid.uuid4()),
        conversation=conversation,
        origen='system',
        timestamp=timestamp,
        sender={
            'name': by_agent.user.username if by_agent else 'system',
            'agent_id': by_agent.user_id if by_agent else None,
            'internal': True,
        },
        content={
            'event_type': event_type,
            'by_agent': _build_agent_snapshot(by_agent),
            'from_agent': _build_agent_snapshot(conversation.agent),
            'from_campaign': _build_campaign_snapshot(conversation.campana),
            'to_agent': _build_agent_snapshot(to_agent),
            'to_campaign': _build_campaign_snapshot(to_campaign),
        },
        type='transfer_event',
        status='read',
        fail_reason='',
    )


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def _eligible_campaigns_for_conversation(self, conversation):
        eligible_campaign_ids = ConfiguracionWhatsappCampana.objects.filter(
            is_active=True,
            linea_id=conversation.line_id,
            campana__estado=Campana.ESTADO_ACTIVA,
            campana__whatsapp_habilitado=True,
        ).exclude(
            campana_id=conversation.campana_id,
        ).values_list('campana_id', flat=True)
        return Campana.objects.filter(
            id__in=eligible_campaign_ids,
            estado=Campana.ESTADO_ACTIVA,
            whatsapp_habilitado=True,
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
            transfer_by = request.user.get_agente_profile()
            conversacion = ConversacionWhatsapp.objects.select_related(
                'agent__user', 'campana'
            ).get(id=chat_id)
            agent = AgenteProfile.objects.select_related('user').get(user__id=agent_id)
            with transaction.atomic():
                _create_transfer_event_message(
                    conversacion,
                    event_type='agent_transfer',
                    by_agent=transfer_by,
                    to_agent=agent,
                )
                success = conversacion.otorgar_conversacion(agent, attended=False)
                if not success:
                    raise Exception(_('Error al tranferir conversacion'))
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
            transfer_by = request.user.get_agente_profile()
            conversation = ConversacionWhatsapp.objects.select_related(
                'line', 'campana', 'agent__user'
            ).get(id=chat_id)
            campaign = self._eligible_campaigns_for_conversation(conversation).get(id=campaign_id)
            ConfiguracionWhatsappCampana.objects.get(
                campana=campaign,
                linea=conversation.line,
                is_active=True,
            )
            with transaction.atomic():
                _create_transfer_event_message(
                    conversation,
                    event_type='campaign_transfer',
                    by_agent=transfer_by,
                    to_campaign=campaign,
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
