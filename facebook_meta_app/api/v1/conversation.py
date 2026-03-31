# -*- coding: utf-8 -*-
import mimetypes
import operator
from dataclasses import dataclass
from functools import reduce
from django.utils import timezone
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.utils.translation import ugettext as _
from rest_framework import serializers, response, status, viewsets, decorators
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from api_app.authentication import ExpiringTokenAuthentication
from api_app.services.media_url import build_public_media_url
from api_app.views.permissions import TienePermisoOML
from facebook_meta_app.api.permissions import TienePermisoCanalFacebookAgente

from facebook_meta_app.api.utils import HttpResponseStatus, get_response_data
from facebook_meta_app.api.v1.message import (
    MessageMessengerMetaAppSerializer, MessageMessengerMetaAppAttachmentSerializer
)
from facebook_meta_app.api.v1.contact import ListSerializer as ContactoSerializer

from facebook_meta_app.models import (
    ConversationMessengerMetaApp, MessageMessengerMetaApp, PlantillaMessenger
)
from ominicontacto_app.models import Campana, AgenteProfile, CalificacionCliente, Contacto
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia

from ominicontacto_app.services.redis.connection import create_redis_connection
from notification_app.notification import AgentNotifier

# Orquestador para envío via Messenger (ADAPTAR: implementar send_text_message etc)
from orquestador_app.core.facebook.send_message import (
    send_text_message, upload_media_to_meta, send_media_message
)

redis_2 = create_redis_connection(db=2)

mimetypes.init()

MESSAGE_SENDERS = {
    'AGENT': 0,
    'CLIENT': 1
}
MESSAGE_STATUS = {
    'SENDING': 0,
    'SENT': 1,
    'DELIVERED': 2,
    'READ': 3,
    'ERROR': 4
}
MESSAGE_LIMIT = 2


@dataclass
class ConversationFilterParams:
    start_date: object = None
    end_date: object = None
    phone: str = None
    agents: list = None


class ConversationFilterParamsSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    agents = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if bool(start_date) != bool(end_date):
            raise serializers.ValidationError(
                _('Debe indicar fecha desde y fecha hasta para aplicar el filtro.')
            )
        return attrs

    def create(self, validated_data):
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        if start_date and end_date:
            validated_data['start_date'] = datetime_hora_minima_dia(start_date)
            validated_data['end_date'] = datetime_hora_maxima_dia(end_date)
        return ConversationFilterParams(**validated_data)


def get_report_conversations_queryset(campaing, params):
    chats_of_campaing = ConversationMessengerMetaApp.objects.filter(
        campana=campaing
    ).select_related(
        "conversation_disposition__opcion_calificacion",
        "client__bd_contacto",
        "agent__user",
        "page",
        "campana",
    ).annotate(
        message_number=Count('messages', distinct=True)
    ).order_by('-date_last_interaction', '-timestamp')
    list_of_Q = []
    if params.agents:
        agents = list(params.agents)
        if -1 in agents:
            list_of_Q.append(Q(agent__isnull=True))
            agents.remove(-1)
        if agents:
            list_of_Q.append(Q(agent__in=agents))
    if list_of_Q:
        chats_of_campaing = chats_of_campaing.filter(reduce(operator.or_, list_of_Q))
    list_of_Q = []
    if params.start_date and params.end_date:
        list_of_Q.append(
            Q(date_last_interaction__range=[params.start_date, params.end_date])
        )
    if params.phone:
        list_of_Q.append(Q(page_client_id__contains=params.phone))
    if list_of_Q:
        chats_of_campaing = chats_of_campaing.filter(reduce(operator.and_, list_of_Q))
    return chats_of_campaing


def get_type(fileName):
    mimestart = mimetypes.guess_type(fileName)[0]
    if mimestart is not None:
        type_file = mimestart.split('/')[0]
        return type_file if type_file not in ['application', 'text'] else 'file'
    return 'file'


class ConversacionMessengerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing_id = serializers.PrimaryKeyRelatedField(
        source='campana', queryset=Campana.objects.all())
    campaing_name = serializers.CharField(source='campana.nombre', default=None)
    # En Messenger usamos page_client_id en lugar de destination (id del usuario en la página)
    destination = serializers.CharField(source='page_client_id', allow_null=True)
    client = serializers.SerializerMethodField()
    agent = serializers.PrimaryKeyRelatedField(
        queryset=AgenteProfile.objects.all(), allow_null=True)
    is_active = serializers.BooleanField(default=True)
    is_disposition = serializers.BooleanField()
    expire = serializers.DateTimeField(allow_null=True)
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField(allow_null=True)
    message_number = serializers.SerializerMethodField()
    message_unread = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    page = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)
    error_ex = serializers.JSONField()
    client_alias = serializers.CharField(default="")

    def get_page(self, obj):
        page = obj.page
        if not page:
            return None
        return {
            'id': page.id,
            'page_id': getattr(page, 'page_id', None),
            'name': getattr(page, 'name', getattr(page, 'page_name', None))
        }

    def get_message_number(self, obj):
        return obj.messages.count()\
            if hasattr(obj, 'messages') else 0

    def get_message_unread(self, obj):
        try:
            return obj.messages.mensajes_recibidos().filter(status='delivered').count()
        except Exception:
            return 0

    def get_messages(self, obj):
        try:
            msgs = obj.messages.all().order_by('timestamp', 'id')
            return MessageMessengerMetaAppSerializer(msgs, many=True).data
        except Exception:
            return []

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            return serializer.data
        return None


class ConversacionMessengerFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaign = serializers.SerializerMethodField()
    destination = serializers.CharField(source='page_client_id', allow_null=True)
    was_closed_by_system = serializers.SerializerMethodField()
    disposition = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    expire = serializers.DateTimeField(allow_null=True)
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField(allow_null=True)
    message_number = serializers.IntegerField()
    photo = serializers.CharField(default="")
    line = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)

    def get_line(self, obj):
        page = obj.page
        if not page:
            return {}
        return {
            'id': page.id,
            'name': page.name,
            'number': page.page_id,
        }

    def get_campaign(self, obj):
        if obj.campana:
            return {
                'id': obj.campana.id,
                'name': obj.campana.nombre,
                'type': obj.campana.type,
            }
        return {}

    def get_agent(self, obj):
        if obj.agent:
            return {
                'id': obj.agent.user.id,
                'name': obj.agent.user.get_full_name() or obj.agent.user.username,
            }
        return None

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            if 'disposition' in serializer.fields:
                del serializer.fields['disposition']
            return serializer.data
        return None

    def get_disposition(self, obj):
        try:
            if obj.is_disposition and obj.conversation_disposition:
                return {
                    'id': obj.conversation_disposition.opcion_calificacion.id,
                    'name': obj.conversation_disposition.opcion_calificacion.nombre,
                }
            return {}
        except Exception:
            return {}

    def get_was_closed_by_system(self, obj):
        return obj.is_disposition and not obj.conversation_disposition


class ContactoSerializerEx(serializers.Serializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(source='telefono')
    page_client_id = serializers.CharField(source='facebook', allow_blank=True)
    disposition = serializers.IntegerField(source='last_disposition_id', allow_null=True)
    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        return obj.obtener_datos()


class ConversacionMessengerSerializerEx(serializers.Serializer):
    id = serializers.IntegerField()
    campaing_id = serializers.IntegerField(source='campana_id', allow_null=True)
    campaing_name = serializers.CharField(source='campana.nombre', default=None)
    destination = serializers.CharField(source='page_client_id', allow_null=True)
    client = serializers.SerializerMethodField()
    agent = serializers.IntegerField(source='agent_id', allow_null=True)
    is_active = serializers.BooleanField(default=True)
    is_disposition = serializers.BooleanField()
    expire = serializers.DateTimeField(allow_null=True)
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField(allow_null=True)
    message_number = serializers.IntegerField(allow_null=True)
    message_unread = serializers.IntegerField(allow_null=True)
    photo = serializers.CharField(default="")
    page = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)
    error_ex = serializers.JSONField()
    client_alias = serializers.CharField(default="")

    def get_page(self, obj):
        page = obj.page
        if not page:
            return None
        return {
            'id': page.id,
            'page_id': getattr(page, 'page_id', None),
            'name': getattr(page, 'name', getattr(page, 'page_name', None))
        }

    def get_client(self, obj):
        if obj.client:
            return ContactoSerializerEx(obj.client).data
        return None


class ConversacionMessengerNuevaSerializer(ConversacionMessengerSerializer):
    is_transfer_campaing = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ConversacionMessengerEnCursoSerializer(ConversacionMessengerSerializer):
    is_transfer_agent = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ReportConversationAPIView(APIView):
    permission_classes = [TienePermisoOML]
    authentication_classes = (ExpiringTokenAuthentication, SessionAuthentication)

    def post(self, request, campaing_id):
        try:
            campaing = Campana.objects.get(id=campaing_id)
            params_serializer = ConversationFilterParamsSerializer(
                data={
                    'start_date': request.data.get('start_date'),
                    'end_date': request.data.get('end_date'),
                    'phone': request.data.get('phone'),
                    'agents': request.data.get('agents'),
                }
            )
            params_serializer.is_valid(raise_exception=True)
            params = params_serializer.save()
            chats_of_campaing = get_report_conversations_queryset(campaing, params)
            serializer = ConversacionMessengerFilterSerializer(chats_of_campaing, many=True)
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={}, message=_(str(e))
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ViewSet(viewsets.ModelViewSet):
    """ViewSet para manejar las conversaciones de Messenger Meta App."""
    queryset = ConversationMessengerMetaApp.objects.all()
    serializer_class = ConversacionMessengerSerializer
    authentication_classes = (ExpiringTokenAuthentication, SessionAuthentication)
    permission_classes = (TienePermisoCanalFacebookAgente,)

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversacionMessengerSerializerEx
        return super().get_serializer_class()

    def get_list_queryset(self):
        return ConversationMessengerMetaApp.objects.filter(
            is_disposition=False
        ).only(
            'id',
            'agent_id',
            'campana_id',
            'client_id',
            'page_id',
            'page_client_id',
            'client_alias',
            'date_last_interaction',
            'error',
            'error_ex',
            'expire',
            'is_active',
            'is_disposition',
            'timestamp',
        ).select_related(
            'campana',
            'page',
        ).prefetch_related(
            Prefetch(
                lookup='client',
                queryset=Contacto.objects.only(
                    'id',
                    'telefono',
                    'facebook',
                    'datos',
                    'id_externo',
                    'bd_contacto',
                ).annotate(
                    last_disposition_id=Subquery(
                        CalificacionCliente.objects.filter(
                            contacto=OuterRef('id'),
                        ).order_by('-id').values('id')[:1]
                    ),
                ).select_related('bd_contacto'),
            ),
        ).annotate(
            message_number=Subquery(
                MessageMessengerMetaApp.objects.filter(
                    conversation_id=OuterRef('id'),
                ).values('conversation_id').annotate(
                    count=Count('id')
                ).values('count')[:1]
            ),
            message_unread=Subquery(
                MessageMessengerMetaApp.objects.filter(
                    conversation_id=OuterRef('id'),
                    status='delivered',
                ).exclude(
                    origen=OuterRef('page_client_id'),
                ).values('conversation_id').annotate(
                    count=Count('id')
                ).values('count')[:1]
            ),
        ).order_by('-date_last_interaction')

    def get_detail_queryset(self):
        return ConversationMessengerMetaApp.objects.select_related(
            'campana',
            'client__bd_contacto',
            'page',
            'agent',
        ).prefetch_related(
            Prefetch(
                'messages',
                queryset=MessageMessengerMetaApp.objects.order_by('timestamp', 'id')
            ),
        )

    def list(self, request):
        try:
            agente = request.user.get_agente_profile()
            agente_campanas = agente.get_campanas_activas_miembro().values_list(
                'queue_name__campana_id', flat=True)
            conversaciones = self.get_list_queryset()
            conversaciones_nuevas = conversaciones.filter(
                agent=None, campana__id__in=agente_campanas).order_by('-date_last_interaction')
            conversaciones_en_curso = conversaciones.filter(
                agent=agente).order_by('-date_last_interaction')
            conversaciones_nuevas =\
                ConversacionMessengerSerializerEx(conversaciones_nuevas, many=True)
            conversaciones_en_curso =\
                ConversacionMessengerSerializerEx(conversaciones_en_curso, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las conversaciones de forma exitosa'),
                    data={
                        "new_conversations": conversaciones_nuevas.data,
                        "inprogress_conversations": conversaciones_en_curso.data}),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las conversaciones')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = self.get_detail_queryset()
            instance = queryset.get(pk=pk)
            instance.messages.mensajes_recibidos().update(status='read')
            serializer = ConversacionMessengerSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo la conversacion de forma exitosa')),
                status=status.HTTP_200_OK)
        except ConversationMessengerMetaApp.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Conversacion no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def agent_chats_lists(self, request):
        agente = request.user.get_agente_profile()
        conversaciones_asignadas = self.get_list_queryset().filter(agent=agente)
        conversaciones_en_curso =\
            ConversacionMessengerSerializerEx(conversaciones_asignadas, many=True)
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                data=conversaciones_en_curso.data),
            status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"])
    def attend_chat(self, request, pk):
        try:
            conversacion = ConversationMessengerMetaApp.objects.get(pk=pk)
            agente = request.user.get_agente_profile()
            if not conversacion.agent or conversacion.agent == agente:
                conversation_granted = conversacion.otorgar_conversacion(agente),
                mensajes = conversacion.messages.all()
                serializer_conversacion = ConversacionMessengerSerializer(conversacion)
                serializer_mensajes = MessageMessengerMetaAppSerializer(mensajes, many=True)
                data = {
                    "conversation_granted": conversation_granted,
                    "conversation_data": serializer_conversacion.data,
                    "messages": serializer_mensajes.data
                }
                agentes = conversacion.campana.obtener_agentes()
                agent_notifier = AgentNotifier()
                for agente in agentes:
                    print("attend_chat...")
                    message = {
                        'chat_id': conversacion.id,
                        'campaign_id': conversacion.campana.pk,
                        'campaign_name': conversacion.campana.nombre,
                        'agent': agente.user.pk
                    }
                    agent_notifier.notify_facebook_chat_attended(agente.user_id, message)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS, data=data,
                        message=_('Se asignó la conversación de forma exitosa')),
                    status=status.HTTP_200_OK
                )
            return response.Response(
                data=get_response_data(
                    message=_('Esta conversación ya está siendo atendida por otro agente')),
                status=status.HTTP_401_UNAUTHORIZED)
        except ConversationMessengerMetaApp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No se puede asignar una conversación que no existe')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error al asignar la conversación >>>", e)
            return response.Response(
                data=get_response_data(message=_('Error al asignar la conversación')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def assign_contact(self, request, pk):
        try:
            contact_pk = request.data.get('contact_pk')
            conversacion = ConversationMessengerMetaApp.objects.get(pk=pk)
            contact = Contacto.objects.get(pk=contact_pk)
            if contact.bd_contacto != conversacion.campana.bd_contacto:
                return response.Response(
                    data=get_response_data(
                        message=_('El contacto no pertenece a la base de datos de la campaña')),
                    status=status.HTTP_400_BAD_REQUEST)
            if contact.facebook and contact.facebook != conversacion.page_client_id:
                return response.Response(
                    data=get_response_data(
                        message=_(
                            'El contacto ya está asociado a otro identificador de Facebook'
                        )),
                    status=status.HTTP_400_BAD_REQUEST)
            if ConversationMessengerMetaApp.objects.filter(is_disposition=False)\
                    .filter(client_id=contact.pk, page_id=conversacion.page_id)\
                    .exclude(pk=conversacion.pk).exists():
                return response.Response(
                    data=get_response_data(
                        message=_('El contacto ya tiene una conversación activa')),
                    status=status.HTTP_400_BAD_REQUEST)
            if not contact.facebook:
                contact.facebook = conversacion.page_client_id
                contact.save(update_fields=['facebook'])
            conversacion.client = contact
            conversacion.save()
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se asigno el contacto a la conversacion de forma satisfactoria')),
                status=status.HTTP_200_OK)
        except ConversationMessengerMetaApp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No se puede asignar una conversación que no existe')),
                status=status.HTTP_404_NOT_FOUND)
        except Contacto.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No existe el contacto que se quiere asignar')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            print("Error al asignar el contacto a la conversación")
            return response.Response(
                data=get_response_data(
                    message=_('Error al asignar el contacto a la conversación')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            pass

    @decorators.action(detail=True, methods=["get"])
    def messages(self, request, pk):
        conversation = ConversationMessengerMetaApp.objects.get(pk=pk)
        if 'message_id' in self.request.GET:
            last_message = MessageMessengerMetaApp.objects.get(id=self.request.GET['message_id'])
            mensajes = MessageMessengerMetaApp.objects.filter(
                conversation=pk, timestamp__gte=last_message.timestamp).order_by('timestamp')
        else:
            mensajes = MessageMessengerMetaApp.objects.filter(conversation=pk).order_by('timestamp')
        serializer_mensajes = MessageMessengerMetaApp(mensajes, many=True)
        data = {
            "messages": serializer_mensajes.data,
            "conversation_info": ConversacionMessengerSerializer(conversation).data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_text(self, request, pk):
        try:
            conversation = ConversationMessengerMetaApp.objects.get(pk=pk)
            if not conversation.error:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.is_active:
                    destination = conversation.page_client_id
                    sender = request.user.get_agente_profile()
                    if not conversation.agent or conversation.agent != sender:
                        raise Exception(
                            _('Esta conversación ya está siendo atendida por otro agente'))
                    data = request.data.copy()
                    page = conversation.page
                    message = {"text": data['message'], "type": "text"}
                    print('>>> send_message_text')
                    message_id = send_text_message(
                        page, destination, message)  # orquestador
                    if message_id:
                        mensaje = MessageMessengerMetaApp.objects.create(
                            message_id=message_id,
                            conversation=conversation,
                            origen=page.page_id,
                            timestamp=timestamp,
                            sender={"name": sender.user.username, "agent_id": sender.user.id},
                            content=message,
                            type="message",
                        )
                        serializer = MessageMessengerMetaAppSerializer(mensaje)
                        print('>>> send_message_text - mensaje enviado')
                        print(serializer.data)
                        return response.Response(
                            data=get_response_data(
                                status=HttpResponseStatus.SUCCESS,
                                data=serializer.data),
                            status=status.HTTP_200_OK)
                    else:
                        raise Exception(
                            _('Este mensaje no se pudo enviar'))
                return response.Response(
                    data=get_response_data(
                        message=_(
                            'La conversacion esta inactiva hasta que el cliente responda')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion es erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={},
                    errors=str(e), message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=['post'])
    def close_conversation(self, request, pk=None):
        """Cierra una conversación específica."""
        try:
            conversation = self.get_object()
            conversation.is_active = False
            conversation.save()
            return response.Response(
                {'status': 'conversation closed'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return response.Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @decorators.action(detail=True, methods=['post'])
    def send_message_template(self, request, pk=None):
        try:
            conversation = ConversationMessengerMetaApp.objects.get(pk=pk)
            if not conversation.error:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.is_active:
                    destination = conversation.page_client_id
                    sender = request.user.get_agente_profile()
                    if not conversation.agent or conversation.agent != sender:
                        raise Exception(
                            _('Esta conversación ya está siendo atendida por otro agente'))
                    data = request.data.copy()
                    page = conversation.page
                    template_data = PlantillaMessenger.objects.get(pk=data['template_id'])
                    print(">>> template_data", template_data)
                    message = template_data.configuracion
                    message_id = send_text_message(
                        page, destination, message)  # orquestador
                    if message_id:
                        mensaje = MessageMessengerMetaApp.objects.create(
                            message_id=message_id,
                            conversation=conversation,
                            origen=page.page_id,
                            timestamp=timestamp,
                            sender={"name": sender.user.username, "agent_id": sender.user.id},
                            content=message,
                            type="message",
                        )
                        serializer = MessageMessengerMetaAppSerializer(mensaje)
                        print('>>> send_message_template - mensaje enviado')
                        print(serializer.data)
                        return response.Response(
                            data=get_response_data(
                                status=HttpResponseStatus.SUCCESS,
                                data=serializer.data),
                            status=status.HTTP_200_OK)
                    else:
                        raise Exception(
                            _('Este mensaje no se pudo enviar'))
                return response.Response(
                    data=get_response_data(
                        message=_(
                            'La conversacion esta inactiva hasta que el cliente responda')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion es erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={},
                    errors=str(e), message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=['post'])
    def send_message_attachment(self, request, pk):
        try:
            conversation = ConversationMessengerMetaApp.objects.get(pk=pk)
            if not conversation.error:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.is_active:
                    sender = request.user.get_agente_profile()
                    if not conversation.agent or conversation.agent != sender:
                        raise Exception(
                            _('Esta conversación ya está siendo atendida por otro agente'))
                    page = conversation.page
                    data = request.data.copy()
                    data.update({"conversation": pk,
                                 "sender": MESSAGE_SENDERS['AGENT']})
                    serializer = MessageMessengerMetaAppAttachmentSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    mensaje = serializer.save()
                    filename = data['file'].name[:100]
                    file_type = get_type(filename)
                    media_path = mensaje.file.path
                    media_url = build_public_media_url(request, mensaje.file.url)
                    attachment_id = upload_media_to_meta(page, file_type, media_path)
                    if not attachment_id:
                        mensaje.delete()
                        raise Exception(
                            _('No se pudo subir el archivo a Meta'))
                    page_client_id = conversation.page_client_id
                    message_id = send_media_message(page, page_client_id, file_type, attachment_id)

                    if message_id:
                        mensaje.message_id = message_id
                        mensaje.origen = page.page_id
                        mensaje.timestamp = timestamp
                        mensaje.sender = {
                            "name": sender.user.username,
                            "agent_id": sender.user.id
                        }
                        mensaje.content = {
                            file_type: {
                                "url": media_url,
                            }
                        }
                        mensaje.type = file_type
                        mensaje.save()
                        serializer = MessageMessengerMetaAppSerializer(mensaje)
                    else:
                        mensaje.delete()
                        raise Exception(
                            _('Este mensaje no se pudo enviar'))
                    return response.Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            data=serializer.data),
                        status=status.HTTP_200_OK)
                return response.Response(
                    data=get_response_data(
                        message=_(
                            'La conversacion esta inactiva hasta que el cliente responda')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion es erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(">>>>>>>>", e)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={},
                    errors=str(e), message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=['get'])
    def active_conversations(self, request):
        """Obtiene todas las conversaciones activas."""
        try:
            active_convs = self.queryset.filter(is_active=True).order_by('-updated_at')
            serializer = self.get_serializer(active_convs, many=True)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return response.Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @decorators.action(detail=False, methods=['get'])
    def closed_conversations(self, request):
        """Obtiene todas las conversaciones cerradas."""
        try:
            closed_convs = self.queryset.filter(is_active=False).order_by('-updated_at')
            serializer = self.get_serializer(closed_convs, many=True)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return response.Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
