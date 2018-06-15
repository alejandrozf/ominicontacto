# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

R_ALFANUMERICO = r'^[ \wáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜçÇ-]+$'
R_DIAL_OPT = r'^[\w]+$'
R_MATCH_PATTERN = r'^[\w]+$'


class TroncalSIP(models.Model):
    """Configuración de Troncal SIP."""
    nombre = models.CharField(
        max_length=128, unique=True, validators=[RegexValidator(R_ALFANUMERICO)])
    canales_maximos = models.PositiveIntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(1)])
    caller_id = models.CharField(max_length=100, validators=[RegexValidator(R_ALFANUMERICO)])
    register_string = models.CharField(max_length=100, validators=[RegexValidator(R_ALFANUMERICO)])
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
        validators=[MaxValueValidator(3600), MinValueValidator(1)])
    dial_options = models.CharField(max_length=512, validators=[RegexValidator(R_DIAL_OPT)])

    def __unicode__(self):
        return self.nombre


class PatronDeDiscado(models.Model):
    """Configuración de Patron de Discado para una Ruta Saliente"""
    ruta_saliente = models.ForeignKey(RutaSaliente, related_name='patrones_de_discado')
    prepend = models.PositiveIntegerField(blank=True)
    prefix = models.PositiveIntegerField(blank=True)
    match_pattern = models.CharField(max_length=100, validators=[RegexValidator(R_MATCH_PATTERN)])

    def __unicode__(self):
        return "Patrón de ruta saliente {0}, prepend:{1}, prefix:{2}, match_pattern: {3}".format(
            self.ruta_saliente.nombre, self.prepend, self.match_pattern)


class OrdenTroncal(models.Model):
    """Posición ordenada de un Troncal Sip en una Ruta Saliente"""
    ruta_saliente = models.ForeignKey(RutaSaliente, related_name='secuencia_troncales')
    orden = models.PositiveIntegerField()
    troncal = models.ForeignKey(TroncalSIP, related_name='orden_en_ruta_saliente')

    class Meta:
        unique_together = ('orden', 'ruta_saliente')

    def __unicode__(self):
        return "Troncal {0} con orden {1} para ruta saliente {2}".format(
            self.troncal.nombre, self.orden, self.ruta_saliente.nombre)
