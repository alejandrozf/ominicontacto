from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_agente = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)

    def get_agente_profile(self):
        agente_profile = None
        if hasattr(self, 'agenteprofile'):
            agente_profile = self.agenteprofile
        return agente_profile

#     def get_patient_profile(self):
#         patient_profile = None
#         if hasattr(self, 'patientprofile'):
#             patient_profile = self.patientprofile
#         return patient_profile
#
#     def get_physiotherapist_profile(self):
#         physiotherapist_profile = None
#         if hasattr(self, 'physiotherapistprofile'):
#             physiotherapist_profile = self.physiotherapistprofile
#         return physiotherapist_profile
#
#     class Meta:
#         db_table = 'auth_user'
#
#


class Modulo(models.Model):
    nombre = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nombre


class Grupo(models.Model):
    nombre = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nombre


class AgenteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    sip_password = models.CharField(max_length=128, blank=True, null=True)
    modulos = models.ManyToManyField(Modulo)
    grupo = models.ForeignKey(Grupo)

    def get_modulos(self):
        return "\n".join([modulo.nombre for modulo in self.modulos.all()])

#
# class PatientProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     active = models.BooleanField(default=True)
#     name = models.CharField(max_length=64)
#
#
# class PhysiotherapistProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     active = models.BooleanField(default=True)
#     name = models.CharField(max_length=64)


class Queue(models.Model):
    """
    Clase cola para el servidor de kamailio
    """

    RINGALL = 'ringall'
    """ring all available channels until one answers (default)"""

    ROUNDROBIN = 'roundrobin'
    """take turns ringing each available interface (deprecated in 1.4,
    use rrmemory)"""

    LEASTRECENT = 'leastrecent'
    """ring interface which was least recently called by this queue"""

    FEWESTCALLS = 'fewestcalls'
    """ring the one with fewest completed calls from this queue"""

    RANDOM = 'random'
    """ring random interface"""

    RRMEMORY = 'rrmemory'
    """round robin with memory, remember where we left off last ring pass"""

    STRATEGY_CHOICES = (
        (RINGALL, 'Ringall'),
        (ROUNDROBIN, 'Roundrobin'),
        (LEASTRECENT, 'Leastrecent'),
        (FEWESTCALLS, 'Fewestcalls'),
        (RANDOM, 'Random'),
        (RRMEMORY, 'Rremory'),
    )

    name = models.CharField(max_length=128, primary_key=True)
    timeout = models.IntegerField()
    retry = models.IntegerField()
    maxlen = models.IntegerField()
    wrapuptime = models.IntegerField()
    servicelevel = models.IntegerField()
    strategy = models.CharField(max_length=128, choices=STRATEGY_CHOICES)
    eventmemberstatus = models.BooleanField()
    eventwhencalled = models.BooleanField()
    weight = models.IntegerField()
    ringinuse = models.BooleanField()
    setinterfacevar = models.BooleanField()

    def __unicode__(self):
        return self.name
