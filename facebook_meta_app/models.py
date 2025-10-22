from django.db import models
from django.utils.translation import gettext as _

from ominicontacto_app.models import AgenteProfile, Contacto, HistoricalCalificacionCliente
from django.utils import timezone
from django.db.models import JSONField
from whatsapp_app.models import PlantillaMensaje


class PaginaMetaFacebook(models.Model):
    """Modelo que representa una configuración de messenger de Meta a través de una página."""
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    # Channel data (Meta App)
    access_token = models.CharField(max_length=500)   # Page Access Token
    verify_token = models.CharField(max_length=255)   # Used for webhook verification
    app_id = models.CharField(max_length=255)     # App Secret from Meta App
    page_id = models.CharField(max_length=255)        # Facebook Page ID
    destination = models.ForeignKey(
        'configuracion_telefonia_app.DestinoEntrante', on_delete=models.PROTECT,
        related_name="pages", blank=True, null=True)
    schedule = models.ForeignKey(
        'configuracion_telefonia_app.GrupoHorario', on_delete=models.PROTECT,
        related_name="pages", blank=True, null=True)
    welcome_message = models.ForeignKey(
        PlantillaMensaje, blank=True, null=True,
        on_delete=models.PROTECT, related_name="pages_welcome_message")
    goodbye_message = models.ForeignKey(
        PlantillaMensaje, blank=True, null=True,
        on_delete=models.PROTECT, related_name="pages_goodbye_message")
    out_of_hours_message = models.ForeignKey(
        PlantillaMensaje, blank=True, null=True,
        on_delete=models.PROTECT, related_name="pages_out_of_hours_message")

    # Settings
    allow_reply_comments = models.BooleanField(default=False)

    # Metadata
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Meta Page Configuration"
        verbose_name_plural = "Meta Page Configurations"

    def __str__(self):
        return f"{self.name} (Page: {self.page_id})"


class PlantillaMessenger(models.Model):
    TIPO_TEXT = 0
    MENSAJE_TIPOS = (
        (TIPO_TEXT, _('Texto')),
    )
    nombre = models.CharField(max_length=100)
    tipo = models.IntegerField(choices=MENSAJE_TIPOS)
    configuracion = JSONField(default=dict)


class GrupoPlantillaMessenger(models.Model):
    nombre = models.CharField(max_length=100)
    plantillas = models.ManyToManyField(PlantillaMessenger, related_name="grupos")

    class Meta:
        verbose_name = "Grupo de Plantillas de Messenger"
        verbose_name_plural = "Grupos de Plantillas de Messenger"
    
    def __str__(self):
        return self.nombre

class ConfiguracionMetaFacebookCampana(models.Model):
    """Modelo que representa la configuración de Messenger de Meta asociada a una campaña."""
    campana = models.OneToOneField(
        'ominicontacto_app.Campana', on_delete=models.CASCADE, related_name='configuracion_meta_facebook')
    pagina = models.ForeignKey(
        PaginaMetaFacebook, on_delete=models.PROTECT, related_name='campanas')
    grupo_plantilla_facebook = models.ForeignKey(
        GrupoPlantillaMessenger, related_name="configuracion_facebook",
        blank=True, null=True, on_delete=models.PROTECT)
    nivel_servicio = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Configuración Meta Facebook Campaña"
        verbose_name_plural = "Configuraciones Meta Facebook Campaña"

    def __str__(self):
        return f"Configuración de {self.campana.nombre} - Página: {self.pagina.name}"   

# class MessengerMetaAppConversation(models.Model):
#     """Modelo que representa una conversación entre un usuario y una página de Facebook a través de Messenger de Meta."""
#     conversation_id = models.CharField(max_length=255, unique=True)  # Unique ID for the conversation
#     client = models.ForeignKey(
#         Contacto, null=True, related_name="conversations_messenger", on_delete=models.CASCADE)
#     agent = models.ForeignKey(
#         AgenteProfile, null=True, related_name="conversations_messenger", on_delete=models.CASCADE)
#     is_disposition = models.BooleanField(default=False)
#     conversation_disposition = models.ForeignKey(
#         HistoricalCalificacionCliente, related_name="conversations_messenger",
#         null=True, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=False)
#     page = models.ForeignKey(MessengerMetaAppPageConfiguration, on_delete=models.CASCADE, related_name='conversations_messenger')
#     last_message = models.ForeignKey('MessengerMetaAppMessage', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
#     updated_at = models.DateTimeField(auto_now=True)

#     expire = models.DateTimeField(null=True)
#     timestamp = models.DateTimeField(default=timezone.now, db_index=True)
#     saliente = models.BooleanField(default=False)
#     atendida = models.BooleanField(default=False)
#     error = models.BooleanField(default=False)
#     error_ex = models.JSONField(default=dict)
#     date_last_interaction = models.DateTimeField(null=True)
#     client_alias = models.CharField(max_length=100, null=True)

#     def __str__(self):
#         return f"Conversation between {self.user.first_name} and Page ID: {self.page.page_id}"

#     class Meta:
#         verbose_name = "Messenger Meta App Conversation"
#         verbose_name_plural = "Messenger Meta App Conversations"
#         ordering = ['-updated_at']   # Order conversations by most recent update first


# class MessengerMetaAppMessage(models.Model):
#     """Modelo que representa un mensaje enviado o recibido a través de Messenger de Meta."""
#     conversation = models.ForeignKey(MessengerMetaAppConversation, on_delete=models.CASCADE, related_name='messages')
#     message_id = models.CharField(max_length=255, unique=True)  # Unique ID for the message
#     sender = models.JSONField()                           # JSON field to store sender info
#     text = models.TextField(blank=True, default="")
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_from_user = models.BooleanField(default=True)  # True if message is from user, False if from page

#     def __str__(self):
#         direction = "From User" if self.is_from_user else "From Page"
#         return f"{direction} - {self.text[:30]}... (Message ID: {self.message_id})"

#     class Meta:
#         verbose_name = "Messenger Meta App Message"
#         verbose_name_plural = "Messenger Meta App Messages"
#         ordering = ['-timestamp']   # Order messages by most recent first


# class MessengerMetaAppAttachment(models.Model):
#     """Modelo que representa un archivo adjunto en un mensaje de Messenger de Meta."""
#     message = models.ForeignKey(MessengerMetaAppMessage, on_delete=models.CASCADE, related_name='attachments')
#     attachment_type = models.CharField(max_length=50)  # e.g., image, video, audio, file
#     url = models.URLField()                             # URL to the attachment
#     name = models.CharField(max_length=255, blank=True, default="")  # Optional name for the attachment

#     def __str__(self):
#         return f"Attachment ({self.attachment_type}) for Message ID: {self.message.message_id}"

#     class Meta:
#         verbose_name = "Messenger Meta App Attachment"
#         verbose_name_plural = "Messenger Meta App Attachments"  
#         ordering = ['-id']   # Order attachments by most recent first


# class MessengerMetaAppComment(models.Model):
#     """Modelo que representa un comentario en una publicación de Facebook gestionada a través de Messenger de Meta."""
#     conversation = models.ForeignKey(MessengerMetaAppConversation, on_delete=models.CASCADE, related_name='comments')
#     comment_id = models.CharField(max_length=255, unique=True)  # Unique ID for the comment
#     page = models.ForeignKey(MessengerMetaAppPageConfiguration, on_delete=models.CASCADE, related_name='comments')
#     sender = models.JSONField()                           # JSON field to store sender info
#     post_id = models.CharField(max_length=255)                  # ID of the Facebook post
#     message = models.TextField()                                 # Content of the comment
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Comment by {self.user.first_name} on Post ID: {self.post_id}"
    
#     class Meta:
#         verbose_name = "Messenger Meta App Comment"
#         verbose_name_plural = "Messenger Meta App Comments"
#         ordering = ['-timestamp']   # Order comments by most recent first


# class MessengerMetaAppCommentReply(models.Model):
#     """Modelo que representa una respuesta a un comentario en una publicación de Facebook gestionada a través de Messenger de Meta."""
#     reply_id = models.CharField(max_length=255, unique=True)    # Unique ID for the reply
#     comment = models.ForeignKey(MessengerMetaAppComment, on_delete=models.CASCADE, related_name='replies')
#     page = models.ForeignKey(MessengerMetaAppPageConfiguration, on_delete=models.CASCADE, related_name='comment_replies')
#     message = models.TextField()                                 # Content of the reply
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Reply to Comment ID: {self.comment.comment_id}"

#     class Meta:
#         verbose_name = "Messenger Meta App Comment Reply"
#         verbose_name_plural = "Messenger Meta App Comment Replies"
#         ordering = ['-timestamp']   # Order replies by most recent first

