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

from __future__ import unicode_literals
import calendar

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils.translation import ugettext_lazy as _

from ominicontacto_app.models import ArchivoDeAudio, Campana

import os
import re
import uuid
SUBSITUTE_REGEX = re.compile(r'[^a-z\._-]')
R_DECIMAL = r'^\d+$'
R_ALFANUMERICO = r'^[\w]+$'
R_DIAL_OPT = r'^[HhKkRrL():MATtWw]+$'
R_MATCH_PATTERN = r'^[\w|\.|\[|\]|-]+$'
R_CONTEXT_DIALPLAN = r'^(\w+,\w+,\w+|\w+,\w+|\w+)$'


class TroncalSIP(models.Model):
    """Configuración de Troncal SIP."""
    CHANSIP = 0
    PJSIP = 1
    OPCIONES_TECNOLOGIA = (
        (CHANSIP, _('chansip')),
        (PJSIP, _('pjsip')),
    )

    nombre = models.CharField(
        max_length=128, unique=True, validators=[RegexValidator(R_ALFANUMERICO)],
        verbose_name=_('Nombre'))
    canales_maximos = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)], default=1000,
        verbose_name=_('Canales máximos'))
    caller_id = models.CharField(
        max_length=100, validators=[RegexValidator(R_ALFANUMERICO)], blank=True, null=True,
        verbose_name=_('Caller id'))
    register_string = models.CharField(max_length=100, blank=True, null=True,
                                       verbose_name=_('Register string'))
    text_config = models.TextField(verbose_name=_('Text config'))
    tecnologia = models.PositiveIntegerField(choices=OPCIONES_TECNOLOGIA, default=CHANSIP)

    def __str__(self):
        return self.nombre

    @property
    def tecnologia_astdb(self):
        if self.tecnologia == self.CHANSIP:
            return 'SIP'
        if self.tecnologia == self.PJSIP:
            return 'PJSIP'


def max_orden_ruta_saliente():
    max = RutaSaliente.objects.aggregate(models.Max('orden'))['orden__max']
    if max is None:
        return 1
    return max + 1


class RutaSaliente(models.Model):
    """
    Configuración de Ruta Saliente.
    Debe tener al menos un patron de discado y un troncal en su secuencia de troncales.
    """
    nombre = models.CharField(
        max_length=128, unique=True, validators=[RegexValidator(R_ALFANUMERICO)])
    ring_time = models.PositiveIntegerField(
        validators=[MaxValueValidator(3600), MinValueValidator(1)], default=25)
    dial_options = models.CharField(
        max_length=512, validators=[RegexValidator(R_DIAL_OPT)], default='Tt')
    orden = models.PositiveIntegerField(unique=True, default=max_orden_ruta_saliente)

    def __str__(self):
        return self.nombre


class PatronDeDiscado(models.Model):
    """Configuración de Patron de Discado para una Ruta Saliente"""
    ruta_saliente = models.ForeignKey(RutaSaliente, related_name='patrones_de_discado',
                                      on_delete=models.CASCADE)
    prepend = models.CharField(
        max_length=32, blank=True, null=True, validators=[RegexValidator(R_DECIMAL)])
    prefix = models.CharField(
        max_length=32, blank=True, null=True, validators=[RegexValidator(R_DECIMAL)])
    match_pattern = models.CharField(max_length=100, validators=[RegexValidator(R_MATCH_PATTERN)])
    orden = models.PositiveIntegerField()

    class Meta:
        unique_together = ('orden', 'ruta_saliente')
        ordering = ['orden']

    def __str__(self):
        return "Patrón de ruta saliente {0} con match_pattern: {1}".format(
            self.ruta_saliente.nombre, self.match_pattern)


class OrdenTroncal(models.Model):
    """Posición ordenada de un Troncal Sip en una Ruta Saliente"""
    ruta_saliente = models.ForeignKey(RutaSaliente, related_name='secuencia_troncales',
                                      on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    troncal = models.ForeignKey(TroncalSIP, related_name='ordenes_en_rutas_salientes',
                                on_delete=models.PROTECT)

    class Meta:
        unique_together = ('orden', 'ruta_saliente')
        ordering = ['orden']

    def __str__(self):
        return "Troncal {0} con orden {1} para ruta saliente {2}".format(
            self.troncal.nombre, self.orden, self.ruta_saliente.nombre)


class IVR(models.Model):
    """Representa la información de un nodo de Respuesta de Voz Interactiva en la ruta de una
    llamada entrante
    """

    VALOR_TIME_OUT = 'time_out'
    VALOR_DESTINO_INVALIDO = 'invalid_destination'

    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=30)
    audio_principal = models.ForeignKey(
        ArchivoDeAudio, on_delete=models.PROTECT, related_name="audio_principal_ivrs")
    time_out = models.PositiveIntegerField()
    time_out_retries = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)])
    time_out_audio = models.ForeignKey(
        ArchivoDeAudio, on_delete=models.PROTECT, blank=True, null=True,
        related_name="audio_time_out_ivrs")
    invalid_retries = models.PositiveIntegerField()
    invalid_audio = models.ForeignKey(
        ArchivoDeAudio, on_delete=models.PROTECT, blank=True, null=True,
        related_name="audio_invalid_ivrs")

    def __str__(self):
        return "IVR {0}".format(self.nombre)


class GrupoHorario(models.Model):
    """Representa un grupo de condiciones de tiempo que debe cumplir un nodo de
    ruta entrante de tipo validación de fecha horario
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))

    def __str__(self):
        return self.nombre


class ValidacionTiempo(models.Model):
    """Representa una condición unitaria de tiempo para un grupo horario"""
    (LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO, DOMINGO) = range(7)
    (ENERO, FEBRERO, MARZO, ABRIL, MAYO, JUNIO, JULIO, AGOSTO, SEPTIEMBRE, OCTUBRE, NOVIEMBRE,
     DICIEMBRE) = range(1, 13)

    DIAS_SEMANA = (
        (LUNES, _('Lunes')),
        (MARTES, _('Martes')),
        (MIERCOLES, _('Miércoles')),
        (JUEVES, _('Jueves')),
        (VIERNES, _('Viernes')),
        (SABADO, _('Sábado')),
        (DOMINGO, _('Domingo')),
    )

    DIAS_MES = [(dia, str(dia)) for dia in range(1, 32)]

    MESES = (
        (ENERO, _('Enero')),
        (FEBRERO, _('Febrero')),
        (MARZO, _('Marzo')),
        (ABRIL, _('Abril')),
        (MAYO, _('Mayo')),
        (JUNIO, _('Junio')),
        (JULIO, _('Julio')),
        (AGOSTO, _('Agosto')),
        (SEPTIEMBRE, _('Septiembre')),
        (OCTUBRE, _('Octubre')),
        (NOVIEMBRE, _('Noviembre')),
        (DICIEMBRE, _('Diciembre')),
    )
    grupo_horario = models.ForeignKey(
        GrupoHorario, related_name='validaciones_tiempo', on_delete=models.CASCADE)
    tiempo_inicial = models.TimeField(help_text=_('Tiempo inicio'))
    tiempo_final = models.TimeField(help_text=_('Tiempo final'))
    dia_semana_inicial = models.PositiveIntegerField(
        choices=DIAS_SEMANA, help_text=_('Día de la semana inicio'), blank=True, null=True)
    dia_semana_final = models.PositiveIntegerField(
        choices=DIAS_SEMANA, help_text=_('Día de la semana final'), blank=True, null=True)
    dia_mes_inicio = models.PositiveIntegerField(
        choices=DIAS_MES, help_text=_('Día del mes inicio'), blank=True, null=True)
    dia_mes_final = models.PositiveIntegerField(
        choices=DIAS_MES, help_text=_('Día del mes final'), blank=True, null=True)
    mes_inicio = models.PositiveIntegerField(
        choices=MESES, help_text=_('Mes inicio'), blank=True, null=True)
    mes_final = models.PositiveIntegerField(
        choices=MESES, help_text=_('Mes final'), blank=True, null=True)

    # Notar que todos los campos de validación temporal, excepto 'tiempo_inicial' no son requeridos
    # si se guardan vacíos esto significa por defecto TODOS (los días de la semana, los meses, etc.)

    def __str__(self):
        return "Validación fecha/hora id:{0} para {1}".format(self.id, self.grupo_horario)

    @property
    def dia_semana_inicial_str(self):
        return self.dia_semana_str(self.dia_semana_inicial)

    @property
    def dia_semana_final_str(self):
        return self.dia_semana_str(self.dia_semana_final)

    def dia_semana_str(self, dia):
        if dia in range(7):
            return calendar.day_abbr[dia]
        return '*'

    @property
    def dia_mes_inicio_str(self):
        return self.dia_mes_str(self.dia_mes_inicio)

    @property
    def dia_mes_final_str(self):
        return self.dia_mes_str(self.dia_mes_final)

    def dia_mes_str(self, dia):
        if dia in range(1, 32):
            return str(dia)
        return '*'

    @property
    def mes_inicio_str(self):
        return self.mes_str(self.mes_inicio)

    @property
    def mes_final_str(self):
        return self.mes_str(self.mes_final)

    def mes_str(self, mes):
        if mes in range(1, 13):
            return calendar.month_abbr[mes]
        return '*'


class ValidacionFechaHora(models.Model):
    """Representa la información de un nodo de Validación Fecha/Hora de una ruta entrante"""
    DESTINO_MATCH = 'True'
    DESTINO_NO_MATCH = 'False'
    nombre = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))
    grupo_horario = models.ForeignKey(
        GrupoHorario, related_name='validaciones_fecha_hora', on_delete=models.PROTECT,
        verbose_name=_('Grupo horario'))


# TODO: implementar el resto de los modelos de los nodos entrantes según sean especificados
# class Extension(models.Model):
#     pass

class IdentificadorCliente(models.Model):
    """Representa una forma de identificar a un contacto a partir de los datos ingresados
    por un usuario en una llamada
    """
    DESTINO_MATCH = 'True'
    DESTINO_NO_MATCH = 'False'
    # el propio código de dialplan determina a partir de la entrada del usuario
    # qué acción tomar
    SIN_INTERACCION_EXTERNA = 1

    # el dialplan consultará al sitio externo especificado por 'url' pasandole como
    # parámetro la entrada del usuario y de acuerdo a la respuesta recibida ("True" o "False")
    # determinará que acción tomar
    INTERACCION_EXTERNA_1 = 2

    # el dialplan consultará al sitio externo especificado por 'url' pasandole como
    # parámetro la entrada del usuario y de acuerdo a la respuesta recibida ((X, Y) o "False")
    # donde X es el tipo de node destino y Y el id del objeto dentro del nodo destino
    # determinará que acción tomar
    INTERACCION_EXTERNA_2 = 3

    TIPOS_INTERACCIONES = (
        (SIN_INTERACCION_EXTERNA, _('Sin interacción externa')),
        (INTERACCION_EXTERNA_1, _('Interacción externa tipo 1')),
        (INTERACCION_EXTERNA_2, _('Interacción externa tipo 2')),
    )

    nombre = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))
    tipo_interaccion = models.PositiveIntegerField(
        choices=TIPOS_INTERACCIONES, help_text=_('Tipo de interacción'),
        default=SIN_INTERACCION_EXTERNA, verbose_name=_('Tipo de interacción'))
    url = models.CharField(
        max_length=128, blank=True, null=True,
        verbose_name=_('Url servicio identificación'))
    audio = models.ForeignKey(
        ArchivoDeAudio, on_delete=models.PROTECT, related_name="identificadores_cliente")
    longitud_id_esperado = models.PositiveIntegerField(validators=[MaxValueValidator(30)],
                                                       blank=True, null=True,
                                                       verbose_name=_('Longitud de id esperado'))
    timeout = models.PositiveIntegerField(default=5,
                                          validators=[MaxValueValidator(60)],
                                          verbose_name=_('Timeout'))
    intentos = models.PositiveIntegerField(default=1,
                                           validators=[MinValueValidator(1),
                                                       MaxValueValidator(20)],
                                           verbose_name=_('Intentos'))

    def __str__(self):
        return str(_("{0}: {1}".format(self.nombre, self.url)))


class DestinoEntrante(models.Model):
    """Representa un nodo de la configuración de una ruta de una llamada entrante en el sistema"""
    CAMPANA = 1
    VALIDACION_FECHA_HORA = 2
    IVR = 3
    EXTENSION = 4
    HANGUP = 5
    SURVEY = 6
    CUSTOM_DST = 7
    VOICEMAIL = 8
    IDENTIFICADOR_CLIENTE = 9

    TIPOS_DESTINOS = (
        (CAMPANA, _('Campaña entrante')),
        (VALIDACION_FECHA_HORA, _('Validación de fecha/hora')),
        (IVR, _('IVR')),
        (HANGUP, _('HangUp')),
        (IDENTIFICADOR_CLIENTE, _('Identificador cliente')),
        (CUSTOM_DST, _('Destino personalizado')),
    )
    nombre = models.CharField(max_length=128)
    tipo = models.PositiveIntegerField(choices=TIPOS_DESTINOS)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    destinos = models.ManyToManyField('DestinoEntrante', through='OpcionDestino')

    class Meta:
        unique_together = ('tipo', 'object_id')

    def __str__(self):
        return str(_("{0}: {1}".format(self.get_tipo_display(), self.nombre)))

    @classmethod
    def crear_nodo_ruta_entrante(cls, info_nodo_entrante, commit=True):
        # el campo 'tipo' debe corresponderse con los campos 'content_type' y
        # 'content_object'
        if isinstance(info_nodo_entrante, Campana):
            tipo = cls.CAMPANA
        elif isinstance(info_nodo_entrante, IVR):
            tipo = cls.IVR
        elif isinstance(info_nodo_entrante, ValidacionFechaHora):
            tipo = cls.VALIDACION_FECHA_HORA
        elif isinstance(info_nodo_entrante, IdentificadorCliente):
            tipo = cls.IDENTIFICADOR_CLIENTE
        elif isinstance(info_nodo_entrante, DestinoPersonalizado):
            tipo = cls.CUSTOM_DST
        elif isinstance(info_nodo_entrante, HangUp):
            raise(_('Error: El nodo HangUp es único.'))
        kwargs = {
            'nombre': info_nodo_entrante.nombre,
            'tipo': tipo,
            'content_object': info_nodo_entrante
        }
        if not commit:
            return DestinoEntrante(**kwargs)
        return cls.objects.create(**kwargs)

    @classmethod
    def get_nodo_ruta_entrante(cls, content_object):
        return cls.objects.get(object_id=content_object.pk,
                               content_type=ContentType.objects.get_for_model(content_object))

    @classmethod
    def get_destinos_por_tipo(cls, tipo):
        """Devuelve un queryset con los nodos destinos de un tipo determinado"""
        return cls.objects.filter(tipo=tipo)

    def _es_destino_siguiente(self):
        return self.destinos_anteriores.count() > 0

    def _es_destino_de_ruta_entrante(self):
        return RutaEntrante.objects.filter(destino=self).count() > 0

    def es_destino_en_flujo_de_llamada(self):
        return self._es_destino_siguiente() or self._es_destino_de_ruta_entrante()

    def get_opcion_destino_por_valor(self, valor):
        """ Obtiene el nodo destino correspondiente al valor de una relacion entre dos nodos """
        return self.destinos_siguientes.get(valor=valor)

    def es_destino_failover(self):
        """Determina si el nodo destino es usado como failover de alguna campaña
        """
        return self.campanas_destino_failover.exists()


class OpcionDestino(models.Model):
    """Representa una relación entre dos nodos de una ruta entrante de una llamada"""
    valor = models.CharField(max_length=30)
    destino_anterior = models.ForeignKey(DestinoEntrante, related_name='destinos_siguientes',
                                         on_delete=models.CASCADE)
    destino_siguiente = models.ForeignKey(DestinoEntrante, related_name='destinos_anteriores',
                                          on_delete=models.CASCADE)

    def __str__(self):
        return str(_("Desde nodo {0} a nodo {1}".format(
            self.destino_anterior.nombre, self.destino_siguiente.nombre)))

    @classmethod
    def crear_opcion_destino(cls, destino_anterior, destino_siguiente, valor):
        kwargs = {'destino_anterior': destino_anterior,
                  'destino_siguiente': destino_siguiente,
                  'valor': valor}
        cls.objects.create(**kwargs)

    class Meta:
        unique_together = ('destino_anterior', 'valor')


class RutaEntrante(models.Model):
    """Representa el nodo inicial de la ruta de una llamada entrante"""
    EN = 1
    ES = 2

    TIPOS_IDIOMAS = (
        (EN, _('Inglés')),
        (ES, _('Español')),)

    SIGLAS_IDIOMAS = {
        EN: 'en',
        ES: 'es',
    }

    nombre = models.CharField(max_length=30, unique=True)
    telefono = models.CharField(
        max_length=30, unique=True, validators=[RegexValidator(R_MATCH_PATTERN)])
    prefijo_caller_id = models.CharField(max_length=30, blank=True, null=True)
    idioma = models.PositiveIntegerField(choices=TIPOS_IDIOMAS)
    destino = models.ForeignKey(DestinoEntrante, related_name='rutas_entrantes',
                                on_delete=models.CASCADE)

    @property
    def sigla_idioma(self):
        return RutaEntrante.SIGLAS_IDIOMAS[self.idioma]


class HangUp(models.Model):

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return str(_("HangUp"))


class DestinoPersonalizado(models.Model):
    nombre = models.CharField(
        max_length=50, unique=True, verbose_name=_('Nombre'),
        validators=[RegexValidator(R_ALFANUMERICO)])
    custom_destination = models.CharField(
        max_length=50, unique=True, verbose_name=_('Localización destino'),
        validators=[RegexValidator(R_CONTEXT_DIALPLAN)])


class Playlist(models.Model):
    nombre = models.CharField(
        max_length=50, unique=True, verbose_name=_('Nombre'),
        validators=[RegexValidator(R_ALFANUMERICO)])

    def __str__(self):
        return self.nombre


def upload_to_musicas_originales(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    filename = "{0}-{1}".format(str(uuid.uuid4()), filename)[:95]
    return os.path.join('musicas_originales', instance.playlist.nombre, filename)


def upload_to_musicas_asterisk(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    filename = "{0}-{1}".format(instance.id, filename)[:95]
    return os.path.join(MusicaDeEspera._DIR_AUDIO_PREDEFINIDO, instance.playlist.nombre, filename)


class MusicaDeEspera(models.Model):
    """Representa una Musica de espera de una Playlist"""

    @property
    def DIR_AUDIO_PREDEFINIDO(self):
        return os.path.join(self._DIR_AUDIO_PREDEFINIDO, self.playlist.nombre)

    _DIR_AUDIO_PREDEFINIDO = "musicas_asterisk"
    # Directorio relativo a MEDIA_ROOT donde se guardan los archivos convertidos para
    # audios globales / predefinidos

    @property
    def OML_AUDIO_PATH_ASTERISK(self):
        return os.path.join(settings.OML_PLAYLIST_PATH_ASTERISK, self.playlist.nombre)

    nombre = models.CharField(
        max_length=100, unique=True, validators=[RegexValidator(R_ALFANUMERICO)],
        verbose_name=_('Nombre')
    )
    audio_original = models.FileField(
        upload_to=upload_to_musicas_originales,
        max_length=100,
        null=True, blank=True,
    )
    # Archivo de audio .wav ya procesado con el ConversorDeAudioService, apto para asterisk.
    audio_asterisk = models.FileField(
        upload_to=upload_to_musicas_asterisk,
        max_length=100,
        null=True, blank=True,
    )
    playlist = models.ForeignKey(Playlist, related_name='musicas', on_delete=models.CASCADE)

    @property
    def descripcion(self):
        return '{0}-{1}'.format(self.id, self.nombre)


class AmdConf(models.Model):
    """
    Representa la configuración AMD del sistema (toma prioridad por encima de amd.conf)
    """
    initial_silence = models.PositiveIntegerField(default=2500)

    greeting = models.PositiveIntegerField(default=1500)
    after_greeting_silence = models.PositiveIntegerField(default=800)

    total_analysis_time = models.PositiveIntegerField(default=5000)

    min_word_length = models.PositiveIntegerField(default=100)
    between_words_silence = models.PositiveIntegerField(default=50)

    maximum_number_of_words = models.PositiveIntegerField(default=3)

    maximum_word_length = models.PositiveIntegerField(default=5000)
    silence_threshold = models.PositiveIntegerField(default=256)


class EsquemaGrabaciones(models.Model):
    """
    Representa la estructura del nombre del archivo que van a tener
    las grabaciones que se generan en el sistema
    Ejemplo:
    Si se define una configuracion con el siguiente esquema:
    id_contacto=True
    id_campana=True
    id_agente=True
    Los archivos generados tendrian el siguiente nombre
    call-1611759898.143-1122-3-1
    """
    id_contacto = models.BooleanField(default=False)
    fecha = models.BooleanField(default=False)
    telefono_contacto = models.BooleanField(default=False)
    id_campana = models.BooleanField(default=False)
    id_externo_contacto = models.BooleanField(default=False)
    id_externo_campana = models.BooleanField(default=False)
    id_agente = models.BooleanField(default=False)
