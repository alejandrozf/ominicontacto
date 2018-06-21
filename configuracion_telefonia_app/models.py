# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils.translation import ugettext as _

from ominicontacto_app.models import ArchivoDeAudio

R_ALFANUMERICO = r'^[\w]+$'
R_DIAL_OPT = r'^[HhKkRrL():MATtWw]+$'
R_MATCH_PATTERN = r'^[\w|\.|\[|\]|-]+$'


class TroncalSIP(models.Model):
    """Configuración de Troncal SIP."""
    nombre = models.CharField(
        max_length=128, unique=True, validators=[RegexValidator(R_ALFANUMERICO)])
    canales_maximos = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)], default=1000)
    caller_id = models.CharField(
        max_length=100, validators=[RegexValidator(R_ALFANUMERICO)], blank=True, null=True)
    register_string = models.CharField(max_length=100, blank=True, null=True)
    text_config = models.TextField()

    def __unicode__(self):
        return self.nombre


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

    def __unicode__(self):
        return self.nombre


class PatronDeDiscado(models.Model):
    """Configuración de Patron de Discado para una Ruta Saliente"""
    ruta_saliente = models.ForeignKey(RutaSaliente, related_name='patrones_de_discado',
                                      on_delete=models.CASCADE)
    prepend = models.PositiveIntegerField(blank=True, null=True)
    prefix = models.PositiveIntegerField(blank=True, null=True)
    match_pattern = models.CharField(max_length=100, validators=[RegexValidator(R_MATCH_PATTERN)])
    orden = models.PositiveIntegerField()

    class Meta:
        unique_together = ('orden', 'ruta_saliente')
        ordering = ['orden']

    def __unicode__(self):
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

    def __unicode__(self):
        return "Troncal {0} con orden {1} para ruta saliente {2}".format(
            self.troncal.nombre, self.orden, self.ruta_saliente.nombre)


class RutaEntrante(models.Model):
    """Representa el nodo inicial de la ruta de una llamada entrante"""
    # solo tiene un único destino
    # no puede ser destino de ningún nodo
    EN = 1
    ES = 2

    TIPOS_IDIOMAS = (
        (EN, _('Inglés')),
        (ES, _('Español')),)

    nombre = models.CharField(max_length=30)
    telefono = models.CharField(max_length=30)
    prefijo_caller_id = models.CharField(max_length=30)
    idioma = models.PositiveIntegerField(choices=TIPOS_IDIOMAS)


class IVR(models.Model):
    """Representa un nodo de Respuesta de Voz Interactiva en la ruta de una llamada
    entrante
    """
    nombre = models.CharField(max_length=30)
    audio_principal = models.ForeignKey(ArchivoDeAudio, related_name="audio_principal_ivrs")
    time_out = models.PositiveIntegerField()
    time_out_retries = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)])
    time_out_audio = models.ForeignKey(ArchivoDeAudio, related_name="audio_time_out_ivrs")
    invalid_retries = models.PositiveIntegerField()
    invalid_audio = models.ForeignKey(ArchivoDeAudio, related_name="audio_invalid_ivrs")
    # hay que definir un nodo destino para cuando ocurre el time-out
    # hay que definir un nodo destino para cuando ocurre una entrada inválida
    # hay que validar que los valores de los nodos destinos desde los DMFs de los IVR sean [0-9|-#*]


class ValidacionFechaHora(models.Model):
    """Representa un nodo de validación por fecha y/o hora
    """
    (LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO, DOMINGO) = range(7)
    (ENERO, FEBRERO, MARZO, ABRIL, MAYO, JUNIO, JULIO, AGOSTO, SEPTIEMBRE, OCTUBRE, NOVIEMBRE,
     DICIEMBRE) = range(1, 13)

    DIAS_SEMANA = (
        (LUNES, 0),
        (MARTES, 1),
        (MIERCOLES, 2),
        (JUEVES, 3),
        (VIERNES, 4),
        (SABADO, 5),
        (DOMINGO, 6),
    )

    MESES = (
        (ENERO, 1),
        (FEBRERO, 2),
        (MARZO, 3),
        (ABRIL, 4),
        (MAYO, 5),
        (JUNIO, 6),
        (JULIO, 7),
        (AGOSTO, 8),
        (SEPTIEMBRE, 9),
        (OCTUBRE, 10),
        (NOVIEMBRE, 11),
        (DICIEMBRE, 12),
    )

    nombre = models.CharField(max_length=30)
    tiempo_inicial = models.TimeField(_('Tiempo inicio'))
    fecha_final = models.TimeField(_('Tiempo final'))
    dia_semana_inicial = models.PositiveIntegerField(
        choices=DIAS_SEMANA, help_text=_('Día de la semana inicio'))
    dia_semana_final = models.PositiveIntegerField(
        choices=DIAS_SEMANA, help_text=_('Día de la semana final'))
    dia_mes_inicio = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)], help_text=_('Día del mes inicio'))
    dia_mes_final = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text=_('Día de la mes final'))
    mes_inicio = models.PositiveIntegerField(choices=MESES, help_text=_('Mes inicio'))
    mes_final = models.PositiveIntegerField(choices=MESES, help_text=_('Mes final'))


class Extension(models.Model):
    pass


class Hangup(models.Model):
    pass


class Encuesta(models.Model):
    pass


class DestinoEntrante(models.Model):
    """Representa un nodo de la configuración de una ruta de una llamada entrante en el sistema"""
    CAMPANA = 1
    VALIDACION_FECHA_HORA = 2
    IVR = 3
    EXTENSION = 4
    HANGUP = 5
    SURVEY = 6
    VOICEMAIL = 7

    TIPOS_DESTINOS = (
        (CAMPANA, _('Campaña entrante')),
        (VALIDACION_FECHA_HORA, _('Validación de fecha/hora')),
        (IVR, _('IVR')),
        (EXTENSION, _('Extensión')),
        (HANGUP, _('Colgar')),
        (SURVEY, _('Encuesta')),
    )
    nombre = models.CharField(max_length=30)
    tipo = models.PositiveIntegerField(choices=TIPOS_DESTINOS)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    destinos = models.ManyToManyField('DestinoEntrante', through='OpcionDestino')

    def __unicode__(self):
        return _("Nodo de ruta entrante: {0}".format(self.nombre))


class OpcionDestino(models.Model):
    """Representa una relación entre dos nodos de una ruta entrante de una llamada"""
    valor = models.CharField(max_length=30)
    destino_anterior = models.ForeignKey(DestinoEntrante, related_name='destinos_siguientes')
    destino_siguiente = models.ForeignKey(DestinoEntrante, related_name='destinos_anteriores')

    def __unicode__(self):
        return _("OpcionDestino de nodo {0} a nodo {1}".format(
            self.destino_anterior.nombre, self.destino_siguiente.nombre))
