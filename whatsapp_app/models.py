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

from django.db import models
from .mixins import AuditableModelMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from configuracion_telefonia_app.models import DestinoEntrante, GrupoHorario
from ominicontacto_app.models import AgenteProfile, Campana, Contacto
from django.utils import timezone


class ConfiguracionProveedor(AuditableModelMixin, models.Model):
    TIPO_TWILIO = 0
    TIPO_META = 1
    TIPO_GUPSHUP = 2
    PROVEEDOR_TIPOS = (
        (TIPO_TWILIO, _('Twilio')),
        (TIPO_META, _('Meta')),
        (TIPO_GUPSHUP, _('GupShup'))
    )
    nombre = models.CharField(max_length=100)
    tipo_proveedor = models.IntegerField(choices=PROVEEDOR_TIPOS)
    configuracion = JSONField(default=dict)  # gupshup: Apikey


class Linea(AuditableModelMixin):
    nombre = models.CharField(max_length=100)  # appname requerido y unico
    proveedor = models.ForeignKey(
        ConfiguracionProveedor, on_delete=models.CASCADE, related_name="lineas")
    numero = models.CharField(max_length=100)  # sender
    configuracion = JSONField(default=dict)  # appname, appid
    destino = models.ForeignKey(
        DestinoEntrante, on_delete=models.CASCADE, related_name="lineas", blank=True, null=True)
    horario = models.ForeignKey(
        GrupoHorario, on_delete=models.CASCADE, related_name="lineas", blank=True, null=True)
    mensaje_bienvenida = models.ForeignKey(
        "PlantillaMensaje", blank=True, null=True,
        on_delete=models.CASCADE, related_name="linea_mensaje_bienvenida")
    mensaje_despedida = models.ForeignKey(
        "PlantillaMensaje", blank=True, null=True,
        on_delete=models.CASCADE, related_name="linea_mensaje_despedida")
    mensaje_fueradehora = models.ForeignKey(
        "PlantillaMensaje", blank=True, null=True,
        on_delete=models.CASCADE, related_name="linea_mensaje_fueradehora")

    def __str__(self) -> str:
        return f"Linea: {self.nombre}"


class PlantillaMensaje(AuditableModelMixin):
    TIPO_TEXT = 0
    TIPO_IMAGE = 1
    MENSAJE_TIPOS = (
        (TIPO_TEXT, _('Texto')),
        (TIPO_IMAGE, _('Imagen')),
    )
    nombre = models.CharField(max_length=100)
    tipo = models.IntegerField(choices=MENSAJE_TIPOS)
    configuracion = JSONField(default=dict)


class TemplateWhatsapp(models.Model):
    linea = models.ForeignKey(
        Linea, on_delete=models.CASCADE, related_name="templates_whatsapp")
    nombre = models.CharField(max_length=100)
    identificador = models.CharField(max_length=100)  # id gupshup
    texto = models.TextField(blank=True, null=True)
    idioma = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    creado = models.CharField(max_length=100)
    modificado = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['linea_id', 'identificador'], name='identificador_unico')
        ]


class GrupoTemplateWhatsapp(AuditableModelMixin):
    nombre = models.CharField(max_length=100)
    templates = models.ManyToManyField(TemplateWhatsapp)

    def __str__(self):
        return f"Grupo Template: {self.nombre}"


class GrupoPlantillaMensaje(AuditableModelMixin):
    nombre = models.CharField(max_length=100)
    plantillas = models.ManyToManyField(PlantillaMensaje)

    def __str__(self):
        return f"Grupo Plantilla: {self.nombre}"


class ConfiguracionWhatsappCampana(AuditableModelMixin):
    campana = models.ForeignKey(
        Campana, related_name="configuracionwhatsapp", on_delete=models.CASCADE)
    linea = models.ForeignKey(Linea, related_name="configuracionwhatsapp",
                              on_delete=models.CASCADE, blank=True, null=True)
    grupo_template_whatsapp = models.ForeignKey(
        GrupoTemplateWhatsapp, related_name="configuracionwhatsapp", on_delete=models.CASCADE)
    grupo_plantilla_whatsapp = models.ForeignKey(
        GrupoPlantillaMensaje, related_name="configuracionwhatsapp", on_delete=models.CASCADE)
    nivel_servicio = models.IntegerField()


class ConversacionWhatsapp(models.Model):
    # conversation_id = models.CharField(max_length=100)
    campana = models.ForeignKey(
        Campana, related_name="conversaciones", on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    client = models.ForeignKey(
        Contacto, null=True, related_name="conversaciones", on_delete=models.CASCADE)
    agent = models.ForeignKey(
        AgenteProfile, null=True, related_name="conversaciones", on_delete=models.CASCADE)
    conversation_type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    is_disposition = models.BooleanField(default=False)
    expire = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)

    def otorgar_conversacion(self, agent):
        if self.agent:
            return False
        else:
            self.agent = agent
            self.save()
            return True


class MensajeWhatsapp(models.Model):
    message_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    origen = models.CharField(max_length=100)
    sender = JSONField(default=dict)
    conversation = models.ForeignKey(
        ConversacionWhatsapp, related_name="mensajes", on_delete=models.CASCADE, null=True)
    content = JSONField(default=dict)
    type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
