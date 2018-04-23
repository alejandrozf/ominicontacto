from __future__ import unicode_literals

from django.db import models


class LlamadasLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con una llamada
    """
    time = models.DateTimeField(db_index=True)
    callid = models.CharField(max_length=32, blank=True, null=True)
    queuename = models.CharField(max_length=32, blank=True, null=True)
    campana_id = models.IntegerField(db_index=True, blank=True, null=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    data1 = models.CharField(max_length=128, blank=True, null=True)
    data2 = models.CharField(max_length=128, blank=True, null=True)
    data3 = models.CharField(max_length=128, blank=True, null=True)
    data4 = models.CharField(max_length=128, blank=True, null=True)
    data5 = models.CharField(max_length=128, blank=True, null=True)


class ActividadAgenteLog(models.Model):
    """
    Define la estructura de un evento de log de cola relacionado con la actividad de un agente
    """
    time = models.DateTimeField(db_index=True)
    agente_id = models.IntegerField(db_index=True, blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    data1 = models.CharField(max_length=128, blank=True, null=True)
