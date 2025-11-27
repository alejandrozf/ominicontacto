# -*- coding: utf-8 -*-
import mimetypes

from django.utils import timezone
from django.utils.translation import ugettext as _
from orquestador_app.core.whatsapp.gupshup_code_error import GUPSHUP_CODE_ERROR
from rest_framework import serializers, response, status, viewsets, decorators
from rest_framework.authentication import SessionAuthentication

from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication

from facebook_meta_app.api.utils import HttpResponseStatus, get_response_data
from facebook_meta_app.api.v1.message import (
    MessageMessengerMetaAppSerializer, MenssageAtachmentCreateSerializer
)
from facebook_meta_app.api.v1.contact import ListSerializer as ContactoSerializer
from facebook_meta_app.api.v1.disposition import OpcionCalificacionSerializer

# Modelos: ADAPTAR nombres/ubicaciones si difieren
from facebook_meta_app.models import (
    ConversationMessengerMetaApp, MessageMessengerMetaApp
)
from ominicontacto_app.models import Campana, AgenteProfile, Contacto

from ominicontacto_app.services.redis.connection import create_redis_connection
from notification_app.notification import AgentNotifier

# Orquestador para envío via Messenger (ADAPTAR: implementar send_text_message etc)
from orquestador_app.core.facebook.send_message import send_text_message

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
        # Serializo la página (PaginaMetaFacebook). ADAPTAR si el serializer de página existe.
        page = obj.page
        if not page:
            return None
        return {
            'id': page.id,
            'page_id': getattr(page, 'page_id', None),
            'name': getattr(page, 'name', getattr(page, 'page_name', None))
        }

    def get_message_number(self, obj):
        return obj.messagemessengermetaapp_set.count()\
            if hasattr(obj, 'messagemessengermetaapp_set') else 0

    def get_message_unread(self, obj):
        # Asumimos que MessageMessengerMetaApp tiene manager/filtrado similar
        try:
            return obj.messages.mensajes_recibidos().filter(status='delivered').count()
        except Exception:
            return 0

    def get_messages(self, obj):
        msgs = getattr(obj, 'messages', None)
        if msgs is None:
            msgs = MessageMessengerMetaApp.objects.filter(
                conversation=obj).order_by('timestamp', 'id')
        return MessageMessengerMetaAppSerializer(msgs, many=True).data

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            return serializer.data
        return None


class ConversacionMessengerFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaign = serializers.SerializerMethodField()
    destination = serializers.CharField(source='page_client_id')
    was_closed_by_system = serializers.SerializerMethodField()
    disposition = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    expire = serializers.DateTimeField(allow_null=True)
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField(allow_null=True)
    message_number = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    page = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)

    def get_page(self, obj):
        page = obj.page
        if not page:
            return None
        return {
            'id': page.id,
            'name': getattr(page, 'name', getattr(page, 'page_name', None)),
            'page_id': getattr(page, 'page_id', None),
        }

    def get_campaign(self, obj):
        if obj.campana:
            campana = obj.campana
            return {
                'id': campana.id,
                'name': campana.nombre,
                'type': getattr(campana, 'type', None),
            }
        return {}

    def get_agent(self, obj):
        if obj.agent:
            return {
                'id': obj.agent.user.id,
                'name': obj.agent.user.get_full_name(),
            }
        return None

    def get_message_number(self, obj):
        return obj.messagemessengermetaapp_set.count()\
            if hasattr(obj, 'messagemessengermetaapp_set') else 0

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            # quitamos disposition si existe
            try:
                del serializer.fields['disposition']
            except Exception:
                pass
            return serializer.data
        return None

    def get_disposition(self, obj):
        try:
            if obj.is_disposition and obj.conversation_disposition:
                serializer = OpcionCalificacionSerializer(
                    obj.conversation_disposition.opcion_calificacion)
                return serializer.data
            return {}
        except Exception as e:
            print(e)

    def get_was_closed_by_system(self, obj):
        return obj.is_disposition and not obj.conversation_disposition


class ConversacionMessengerNuevaSerializer(ConversacionMessengerSerializer):
    is_transfer_campaing = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ConversacionMessengerEnCursoSerializer(ConversacionMessengerSerializer):
    is_transfer_agent = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ViewSet(viewsets.ModelViewSet):
    """ViewSet para manejar las conversaciones de Messenger Meta App."""
    queryset = ConversationMessengerMetaApp.objects.all()
    serializer_class = ConversacionMessengerSerializer
    authentication_classes = (ExpiringTokenAuthentication, SessionAuthentication)
    permission_classes = (TienePermisoOML,)

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversacionMessengerFilterSerializer
        return super().get_serializer_class()

    def list(self, request):
        try:
            agente = request.user.get_agente_profile()
            agente_campanas = agente.get_campanas_activas_miembro().values_list(
                'queue_name__campana_id', flat=True)

            conversaciones = ConversationMessengerMetaApp.objects.filter(
                is_disposition=False)
            conversaciones_nuevas = conversaciones.filter(
                agent=None, campana__id__in=agente_campanas).order_by('-date_last_interaction')
            conversaciones_en_curso = conversaciones.filter(
                agent=agente).order_by('-date_last_interaction')
            conversaciones_nuevas =\
                ConversacionMessengerSerializer(conversaciones_nuevas, many=True)
            conversaciones_en_curso =\
                ConversacionMessengerSerializer(conversaciones_en_curso, many=True)
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
            queryset = ConversationMessengerMetaApp.objects.all()
            instance = queryset.get(pk=pk)
            instance.mensajes.mensajes_recibidos().update(status='read')
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
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def agent_chats_lists(self, request):
        agente = request.user.get_agente_profile()
        conversaciones_asignadas = agente.conversaciones.all()
        conversaciones_en_curso =\
            ConversacionMessengerSerializer(conversaciones_asignadas, many=True)
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
                mensajes = conversacion.mensajes.all()
                serializer_conversacion = ConversacionMessengerSerializer(conversacion)
                serializer_mensajes = MessageMessengerMetaApp(mensajes, many=True)
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
                    agent_notifier.notify_whatsapp_chat_attended(agente.user_id, message)
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
            if ConversationMessengerMetaApp.objects.conversaciones_en_curso()\
                    .filter(client_id=contact.pk, line_id=conversacion.line.pk).exists():
                return response.Response(
                    data=get_response_data(
                        message=_('El contacto ya tiene una conversación activa')),
                    status=status.HTTP_400_BAD_REQUEST)
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
        except Exception as e:
            print("Error al asignar el contacto a la conversación")
            print(e)
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
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        destination = conversation.destination
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
                                type="text",
                            )
                            serializer = MessageMessengerMetaApp(mensaje)
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
                return response.Response(data=get_response_data(
                    message=_('La conversacion ha expirado. Inicie una nueva conversacion.')),
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
    def send_message(self, request, pk=None):
        """Envía un mensaje a través de la conversación específica."""
        try:
            conversation = self.get_object()
            message_text = request.data.get('message', '')

            if not message_text:
                return response.Response(
                    {'error': 'Message text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Lógica para enviar el mensaje usando el orquestador
            send_text_message(
                page_access_token=conversation.page.access_token,
                recipient_id=conversation.page_client_id,
                message_text=message_text
            )

            return response.Response(
                {'status': 'message sent'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return response.Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @decorators.action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Agrega un attachment a la conversación específica."""
        try:
            conversation = self.get_object()
            serializer = MenssageAtachmentCreateSerializer(data=request.data)
            if serializer.is_valid():
                attachment = serializer.save(conversation=conversation)
                return response.Response(
                    {'status': 'attachment added', 'attachment_id': attachment.id},
                    status=status.HTTP_201_CREATED
                )
            else:
                return response.Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return response.Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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
