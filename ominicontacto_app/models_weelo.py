# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.db import models
from ominicontacto_app.models import Contacto, Campana

logger = logging.getLogger(__name__)


class FormularioDatoVenta(models.Model):
    NIVEL_PRIMARIO_INCOMPLETO = 1
    """Nivel de estudio primario incompleto"""

    NIVEL_PRIMARIO = 2
    """Nivel de estudio primario"""

    NIVEL_SECUNDARIO_INCOMPLETO = 3
    """Nivel de estudio secundario incompleto"""

    NIVEL_SECUNDARIO = 4
    """Nivel de estudio secundario"""

    NIVEL_TERCIARIO_INCOMPLETO = 5
    """Nivel de estudio terciario incompleto"""

    NIVEL_TERCIARIO = 6
    """Nivel de estudio terciario"""

    NIVEL_UNIVERSITARIO_INCOMPLETO = 7
    """Nivel de estudio universitario incompleto"""

    NIVEL_UNIVERSITARIO = 8
    """Nivel de estudio universitario"""

    NIVEL_ESTUDIO_CHOICES = (
        (NIVEL_PRIMARIO_INCOMPLETO, 'Primario incompleto'),
        (NIVEL_PRIMARIO, 'Primario'),
        (NIVEL_SECUNDARIO_INCOMPLETO, 'Secuandario incompleto'),
        (NIVEL_SECUNDARIO, 'Secundario'),
        (NIVEL_TERCIARIO_INCOMPLETO, 'Terciario incompleto'),
        (NIVEL_TERCIARIO, 'Terciario'),
        (NIVEL_UNIVERSITARIO_INCOMPLETO, 'Universitario incompleto'),
        (NIVEL_UNIVERSITARIO, 'Universitario')
    )

    VIVIENDA_PROPIA = 1
    """vivienda propia"""

    VIVIENDA_ALQUILADA = 2
    """vivienda alquilada"""

    VIVIENDA_FAMILIA = 3
    """vivienda familiar"""

    VIVIENDA_OTRA = 4
    """vivienda otra"""

    VIVIENDA_CHOICES = (
        (VIVIENDA_PROPIA, 'Propia'),
        (VIVIENDA_ALQUILADA, 'Alquilada'),
        (VIVIENDA_FAMILIA, 'Familia'),
        (VIVIENDA_OTRA, 'Otra')

    )

    SITUACION_DEPENDENCIA = 1
    """relacion laboral en dependencia"""

    SITUACION_INDEPENDIENTE = 2
    """relacion laboral dependencia"""

    SITUACION_LABORAL_CHOICES = (
        (SITUACION_DEPENDENCIA, 'Relacion de dependencia'),
        (SITUACION_INDEPENDIENTE, 'Independiente')
    )

    TIPO_PYME = 1
    """tipo de empresa pyme"""

    TIPO_MICRO = 2
    """tipo de empresa micro"""

    TIPO_PUBLICO = 3
    """tipo de empresa organismo publico"""

    TIPO_GRANDE = 4
    """tipo de empresa grande"""

    TIPO_EMPRESA_CHOICES = (
        (TIPO_PYME, 'Pyme'),
        (TIPO_MICRO, 'Micro'),
        (TIPO_PUBLICO, 'Organismo Publico'),
        (TIPO_GRANDE, 'Grande')

    )

    campana = models.ForeignKey(Campana, related_name="formularios")
    contacto = models.OneToOneField(Contacto, on_delete=models.CASCADE)
    calle = models.CharField(max_length=128)
    numero = models.models.PositiveIntegerField()
    depto = models.CharField(max_length=8, blank=True, null=True)
    localidad = models.CharField(max_length=128, blank=True, null=True)
    codigo_postal = models.CharField(max_length=128, blank=True, null=True)
    empresa_celular = models.CharField(max_length=128, blank=True, null=True)
    telefono_celular = models.CharField(max_length=128)
    telefono_fijo = models.CharField(max_length=128)
    email = models.EmailField()
    nivel_estudio = models.PositiveIntegerField(choices=NIVEL_ESTUDIO_CHOICES,
                                                blank=True, null=True)
    vivienda = models.PositiveIntegerField(choices=VIVIENDA_CHOICES, blank=True,
                                           null=True)
    gastos_mensuales = models.CharField(max_length=128)
    nombre_padre = models.CharField(max_length=128,
                                    verbose_name="Nombre y Apellido del Padre")
    nombre_madre = models.CharField(max_length=128,
                                    verbose_name="Nombre y Apellido de la Madre"
                                    )
    situacion_laboral = models.PositiveIntegerField(
        choices=SITUACION_LABORAL_CHOICES)
    nombre_empresa = models.CharField(max_length=128,
                                      verbose_name="Nombre de la empresa")
    tipo_empresa = models.PositiveIntegerField(choices=TIPO_EMPRESA_CHOICES)
    domicilio_labral = models.CharField(max_length=128)
    cargo = models.CharField(max_length=128, verbose_name="Cargo o Funcion")

    def __unicode__(self):
        return "Formulario dato venta para campana{0} para el contacto " \
               "{1} ".format(self.campana, self.contacto)

