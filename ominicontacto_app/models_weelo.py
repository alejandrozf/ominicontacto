# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.db import models
from ominicontacto_app.models import Contacto, Campana

logger = logging.getLogger(__name__)


class FormularioDatoVenta(models.Model):

    campana = models.ForeignKey(Campana, related_name="formularios")
    contacto = models.OneToOneField(Contacto, on_delete=models.CASCADE)
    calle = models.CharField(max_length=128)
    numero = models.models.PositiveIntegerField()
    extra_3 = models.CharField(max_length=128, blank=True, null=True)
    extra_4 = models.TextField(blank=True, null=True)
    extra_5 = models.CharField(max_length=128, blank=True, null=True)
    extra_6 = models.CharField(max_length=128, blank=True, null=True)
    extra_7 = models.CharField(max_length=128, blank=True, null=True)
    extra_8 = models.CharField(max_length=128, blank=True, null=True)
    extra_9 = models.CharField(max_length=128, blank=True, null=True)
    extra_10 = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return "Formulario dato venta para campana{0} para el contacto " \
               "{1} ".format(self.campana, self.contacto)

