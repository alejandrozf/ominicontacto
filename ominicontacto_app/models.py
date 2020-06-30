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

import datetime
import json
import logging
import os
import random
import re
import uuid


from ast import literal_eval

from django.contrib.auth.models import AbstractUser, _user_has_perm
from django.contrib.sessions.models import Session
from django.db import (models,
                       # connection
                       )

from django.db.models import Max, Q, Count, Sum
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError, SuspiciousOperation, ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now, timedelta

from django_extensions.db.models import TimeStampedModel

from simple_history.models import HistoricalRecords

from ominicontacto_app.utiles import (
    ValidadorDeNombreDeCampoExtra, fecha_local, datetime_hora_maxima_dia,
    datetime_hora_minima_dia, remplace_espacio_por_guion, dividir_lista)
from ominicontacto_app.permisos import PermisoOML
PermisoOML

logger = logging.getLogger(__name__)

SUBSITUTE_REGEX = re.compile(r'[^a-z\._-]')
R_ALFANUMERICO = r'^[\w]+$'
SUBSITUTE_ALFANUMERICO = re.compile(r'[^\w]')


class User(AbstractUser):

    # Roles predefinidos
    ADMINISTRADOR = 'Administrador'
    GERENTE = 'Gerente'
    SUPERVISOR = 'Supervisor'
    REFERENTE = 'Referente'
    AGENTE = 'Agente'
    CLIENTE_WEBPHONE = 'Cliente Webphone'

    is_agente = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_cliente_webphone = models.BooleanField(default=False)
    last_session_key = models.CharField(blank=True, null=True, max_length=40)
    borrado = models.BooleanField(default=False, editable=False)

    @property
    def rol(self):
        # Se asume que tiene un solo grupo
        rol = self.groups.first()
        return rol

    def get_agente_profile(self):
        agente_profile = None
        if hasattr(self, 'agenteprofile'):
            agente_profile = self.agenteprofile
        return agente_profile

    def get_is_agente(self):
        if self.is_agente and self.get_agente_profile():
            return True
        return False

    def get_supervisor_profile(self):
        supervisor_profile = None
        if hasattr(self, 'supervisorprofile'):
            supervisor_profile = self.supervisorprofile
        return supervisor_profile

    def get_is_administrador(self):
        supervisor = self.get_supervisor_profile()
        if supervisor and supervisor.is_administrador:
            return True
        # TODO: Tal vez no deberían incluirse los usuarios is_staff porque pueden llegar a crearse
        # sin SupervisorProfile asociado
        elif self.is_staff:
            return True
        return False

    def get_is_supervisor_customer(self):
        supervisor = self.get_supervisor_profile()
        if supervisor and supervisor.is_customer:
            return True
        return False

    def get_is_supervisor_normal(self):
        supervisor = self.get_supervisor_profile()
        if supervisor and not supervisor.is_customer and not supervisor.is_administrador:
            return True
        return False

    def get_cliente_webphone_profile(self):
        cliente_webphone_profile = None
        if hasattr(self, 'clientewebphoneprofile'):
            cliente_webphone_profile = self.clientewebphoneprofile
        return cliente_webphone_profile

    def get_is_cliente_webphone(self):
        if self.is_cliente_webphone and self.get_cliente_webphone_profile():
            return True
        return False

    def get_tiene_permiso_administracion(self):
        """Funcion devuelve true si tiene permiso de acceso a la pagina
        de adminstracion del sistema"""
        # Indica si tiene SupervisorProfile asociado. (Tiene permisos de Gestión)
        return hasattr(self, 'supervisorprofile')

    def get_es_administrador_o_supervisor_normal(self):
        """Funcion devuelve true si el usuario es Administrador o Supervisor Normal"""
        if self.get_is_administrador():
            return True
        elif self.get_is_supervisor_normal():
            return True
        return False

    def tiene_permiso_oml(self, nombre_permiso):
        if PermisoOML.objects.filter(codename=nombre_permiso).exists():
            full_name = 'permiso_oml.{0}'.format(nombre_permiso)
            return _user_has_perm(self, full_name, None)
        # Si no existe el permiso la vista no esta restringida
        return True

    def set_session_key(self, key):
        if self.last_session_key and not self.last_session_key == key:
            try:
                # TODO: Revisar por que está este codigo.
                #       Si se hace logout normal, no se esta limpiando last_session_key
                #       Pero Django borra la session automaticamente
                Session.objects.get(session_key=self.last_session_key).delete()
            except Session.DoesNotExist:
                # TODO: Este log aparece toda vez que se loggee un usuario y la key sea otra
                #       O no exista sesion
                logger.exception(_("Excepcion detectada al obtener session "
                                   "con el key {0} no existe".format(self.last_session_key)))
        self.last_session_key = key
        self.save()

    def borrar(self):
        """
        Setea Usuario como BORRADO y is_active como False.
        """
        logger.info(_("Seteando Usuario {0} como BORRADO".format(self.id)))

        self.borrado = True
        self.is_active = False
        self.save()

    def force_logout(self):
        if self.last_session_key:
            try:
                Session.objects.get(session_key=self.last_session_key).delete()
            except Session.DoesNotExist:
                pass


class Grupo(models.Model):
    nombre = models.CharField(max_length=20, unique=True, verbose_name=_('Nombre'))
    auto_attend_inbound = models.BooleanField(default=False, verbose_name=_(
        'Auto atender entrantes'))
    auto_attend_dialer = models.BooleanField(default=False, verbose_name=_('Auto atender dailer'))
    auto_unpause = models.PositiveIntegerField(verbose_name=_('Despausar automaticamente'))

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _('Grupo')
        verbose_name_plural = _('Grupos')


class AgenteProfileManager(models.Manager):

    def obtener_activos(self):
        return self.filter(is_inactive=False, borrado=False, user__borrado=False)

    def obtener_agentes_campana(self, campana):
        """
        Obtiene todos los agentes que estan asignados a una campana
        """
        return self.filter(queue__campana=campana)

    def get_agent_sip_extension(self, agent_id):
        return self.filter(id=agent_id).values_list('sip_extension', flat=True)

    def obtener_agentes_supervisor(self, supervisor):
        """
        Obtiene todos los agentes que estan asignados a las campanas
        que un supervisor tiene asignadas
        """
        if supervisor.is_administrador:
            return self.obtener_activos()
        elif supervisor.is_customer:
            campanas = supervisor.user.campanasupervisors.all()
        # TODO: Definir cuando se diferencie el rol de Gerente del de Supervisor Normal.
        # elif supervisor.is_gerente:
        # Agentes en: Campañas propias + Campañas asignadas + Campañas de sus supervisores
        else:
            # Supervisor Normal / Comun: Agentes en campañas propias y asignadas.
            campanas = Campana.objects.filter(
                Q(reported_by=supervisor.user) | Q(supervisors__in=[supervisor.user, ]))

        return self.obtener_activos().filter(queue__campana__in=campanas).distinct()


class AgenteProfile(models.Model):
    ESTADO_OFFLINE = 1
    """Agente en estado offline"""

    ESTADO_ONLINE = 2
    """Agente en estado online"""

    ESTADO_PAUSA = 3
    """Agente en estado pausa"""

    ESTADO_CHOICES = (
        (ESTADO_OFFLINE, 'OFFLINE'),
        (ESTADO_ONLINE, 'ONLINE'),
        (ESTADO_PAUSA, 'PAUSA'),
    )

    objects = AgenteProfileManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    sip_password = models.CharField(max_length=128, blank=True, null=True)
    grupo = models.ForeignKey(Grupo, related_name='agentes', verbose_name=_("Grupo"),
                              on_delete=models.CASCADE)
    # TODO: Revisar si esta variable se esta usando para algo
    estado = models.PositiveIntegerField(choices=ESTADO_CHOICES, default=ESTADO_OFFLINE)
    reported_by = models.ForeignKey(User, related_name="reportedby", on_delete=models.CASCADE)
    is_inactive = models.BooleanField(default=False)
    borrado = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.user.get_full_name()

    def get_campanas_activas_miembro(self):
        campanas_member = self.campana_member.all()
        return campanas_member.filter(queue_name__campana__estado=Campana.ESTADO_ACTIVA)

    def has_campanas_preview_activas_miembro(self):
        campanas_preview_activas = self.campana_member.filter(
            queue_name__campana__estado=Campana.ESTADO_ACTIVA,
            queue_name__campana__type=Campana.TYPE_PREVIEW)
        return campanas_preview_activas.exists()

    def get_campanas_preview_activas_miembro(self):
        campanas_preview_activas = self.campana_member.filter(
            queue_name__campana__estado=Campana.ESTADO_ACTIVA,
            queue_name__campana__type=Campana.TYPE_PREVIEW)
        return campanas_preview_activas

    def esta_asignado_a_campana(self, campana):
        return self.campana_member.filter(queue_name__campana_id=campana.id).exists()

    # TODO verificar si se puede eliminar esta funcion
    def get_id_nombre_agente(self):
        return "{0}_{1}".format(self.id, self.user.get_full_name())

    def get_asterisk_caller_id(self):
        nombre_agente = remplace_espacio_por_guion(self.user.get_full_name())
        return "{0}_{1}".format(self.id, nombre_agente)

    def desactivar(self):
        self.is_inactive = True
        self.save()

    def activar(self):
        self.is_inactive = False
        self.save()

    def borrar(self):
        """
        Setea Agente como BORRADO y is_inactive True .
        """
        logger.info(_("Seteando Agente {0} como BORRADO".format(self.id)))

        self.borrado = True
        self.is_inactive = True
        self.save()

    def force_logout(self):
        self.user.force_logout()


class SupervisorProfile(models.Model):

    ROL_ADMINISTRADOR = '1'
    ROL_GERENTE = '2'
    ROL_SUPERVISOR = '3'
    ROL_CLIENTE = '4'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    sip_password = models.CharField(max_length=128, blank=True, null=True)
    is_administrador = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    borrado = models.BooleanField(default=False, editable=False)
    timestamp = models.CharField(max_length=64, blank=True, null=True)
    # TODO: OML-1448 eliminar los campos timestamp y sip_password

    def __str__(self):
        return self.user.get_full_name()

    def borrar(self):
        """
        Setea Supervisor como BORRADO .
        """
        logger.info(_("Seteando Supervisor {0} como BORRADO".format(self.id)))

        self.borrado = True
        self.save()

    def campanas_asignadas_actuales(self):
        """
        Devuelve las campañas NO BORRADAS a las que esta asignado el Supervisor.
        """
        estados = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                   Campana.ESTADO_INACTIVA, Campana.ESTADO_FINALIZADA]
        return self.user.campanasupervisors.filter(estado__in=estados)

    def campanas_asignadas_actuales_no_finalizadas(self):
        """
        Devuelve las campañas NO BORRADAS a las que esta asignado el Supervisor.
        """
        estados = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                   Campana.ESTADO_INACTIVA]
        return self.user.campanasupervisors.filter(estado__in=estados)

    def obtener_campanas_asignadas_activas(self):
        return self.user.campanasupervisors.filter(estado=Campana.ESTADO_ACTIVA)

    def esta_asignado_a_campana(self, campana):
        return self.user.campanasupervisors.filter(id=campana.id).exists()


class ClienteWebPhoneProfileManager(models.Manager):
    def obtener_activos(self):
        return self.exclude(is_inactive=True)


class ClienteWebPhoneProfile(models.Model):
    objects = ClienteWebPhoneProfileManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    is_inactive = models.BooleanField(default=False)
    borrado = models.BooleanField(default=False)

    def toggle_is_inactive(self):
        self.is_inactive = not self.is_inactive
        self.save()

    def borrar(self):
        """
        Setea Cliente Webphone como BORRADO .
        """
        logger.info(_("Seteando Cliente Webphone {0} como BORRADO".format(self.id)))

        self.is_inactive = True
        self.borrado = True
        self.save()


class NombreCalificacionManager(models.Manager):
    def usuarios(self):
        """
        Devuelve todas las calificaciones excepto la restringida de sistema
        para agenda
        """
        return self.exclude(nombre=settings.CALIFICACION_REAGENDA)


class NombreCalificacion(models.Model):
    nombre = models.CharField(max_length=50, verbose_name=_('Nombre'))
    objects = NombreCalificacionManager()

    def es_reservada(self):
        return self.nombre == settings.CALIFICACION_REAGENDA

    def __str__(self):
        return self.nombre


class Formulario(models.Model):
    nombre = models.CharField(max_length=64)
    descripcion = models.TextField()
    oculto = models.BooleanField(default=False)

    def tiene_campana_asignada(self):
        return self.campana_set.all().exists()

    def __str__(self):
        return self.nombre


class FieldFormularioManager(models.Manager):

    def obtener_siguiente_orden(self, formulario_id):
        try:
            field_formulario = self.filter(formulario=formulario_id).latest(
                'orden')
            return field_formulario.orden + 1
        except FieldFormulario.DoesNotExist:
            return 1


class FieldFormulario(models.Model):

    objects = FieldFormularioManager()

    ORDEN_SENTIDO_UP = 0
    ORDEN_SENTIDO_DOWN = 1

    TIPO_TEXTO = 1
    """Tipo de campo texto"""

    TIPO_FECHA = 2
    """Tipo de campo fecha"""

    TIPO_LISTA = 3
    """Tipo de campo lista"""

    TIPO_TEXTO_AREA = 4
    """Tipo de campo text area"""

    TIPO_CHOICES = (
        (TIPO_TEXTO, _('Texto')),
        (TIPO_FECHA, _('Fecha')),
        (TIPO_LISTA, _('Lista')),
        (TIPO_TEXTO_AREA, _('Caja de Texto de Area')),
    )

    formulario = models.ForeignKey(Formulario, related_name="campos", on_delete=models.CASCADE)
    nombre_campo = models.CharField(max_length=64)
    orden = models.PositiveIntegerField()
    tipo = models.PositiveIntegerField(choices=TIPO_CHOICES)
    values_select = models.TextField(blank=True, null=True)
    is_required = models.BooleanField()

    class Meta:
        ordering = ['orden']
        unique_together = ("orden", "formulario")

    def __str__(self):
        return str(_("campo {0} del formulario {1}".format(self.nombre_campo,
                                                           self.formulario)))

    def obtener_campo_anterior(self):
        """
        Este método devuelve el field del formulario anterior a self,
         teniendo en cuenta que pertenezca a la mismo formulario que self.
        """
        return FieldFormulario.objects.filter(formulario=self.formulario,
                                              orden__lt=self.orden).last()

    def obtener_campo_siguiente(self):
        """
        Este método devuelve el field del formulario siguiente a self,
         teniendo en cuenta que pertenezca a la mismo formulario que self.
        """
        return FieldFormulario.objects.filter(formulario=self.formulario,
                                              orden__gt=self.orden).first()


# aplica lo que está en la doc
# https://docs.djangoproject.com/en/1.11/topics/migrations/#serializing-values
def upload_to_audio_original(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    return "audios_reproduccion/{0}-{1}".format(
        str(uuid.uuid4()), filename)[:95]


def upload_to_audio_asterisk(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    return "audios_asterisk/{0}-{1}".format(
        str(uuid.uuid4()), filename)[:95]


class ArchivoDeAudioManager(models.Manager):
    """Manager para ArchivoDeAudio"""

    def get_queryset(self):
        return super(ArchivoDeAudioManager, self).get_queryset().exclude(
            borrado=True)


class ArchivoDeAudio(models.Model):
    """
    Representa una ArchivoDeAudio
    """
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = ArchivoDeAudioManager()

    DIR_AUDIO_PREDEFINIDO = "audio_asterisk_predefinido"
    """Directorio relativo a MEDIA_ROOT donde se guardan los archivos
    convertidos para audios globales / predefinidos
    """
    OML_AUDIO_PATH_ASTERISK = settings.OML_AUDIO_PATH_ASTERISK

    descripcion = models.CharField(
        max_length=100, unique=True, validators=[RegexValidator(R_ALFANUMERICO)]
    )
    audio_original = models.FileField(
        upload_to=upload_to_audio_original,
        max_length=100,
        null=True, blank=True,
    )
    # Archivo de audio .wav ya procesado con el ConversorDeAudioService, apto para asterisk.
    audio_asterisk = models.FileField(
        upload_to=upload_to_audio_asterisk,
        max_length=100,
        null=True, blank=True,
    )
    borrado = models.BooleanField(
        default=False,
        editable=False,
    )

    def __str__(self):
        if self.borrado:
            return _(u'(Eliminado) {0}').format(self.descripcion)
        return self.descripcion

    def borrar(self):
        """
        Setea la ArchivoDeAudio como BORRADO.
        """
        if self.usado_en_ivr():
            raise ValidationError(_(u'No se puede borrar un Archivo de Audio en uso por IVR'))
        if self.usado_en_queue():
            raise ValidationError(_(u'No se puede borrar un Archivo de Audio en uso en Campañas'))

        logger.info(_("Seteando ArchivoDeAudio %s como BORRADO"), self.id)

        self.borrado = True
        self.save()

    def get_filename_audio_asterisk(self):
        """
        Returna el filename del audio asterisl
        """
        if self.audio_asterisk:
            filepath = self.audio_asterisk.path
            return os.path.splitext(os.path.basename(filepath))[0]
        return None

    @classmethod
    def crear_archivo(cls, descripcion, audio_original):
        return cls.objects.create(descripcion=descripcion, audio_original=audio_original)

    @classmethod
    def calcular_descripcion(cls, descripcion):
        """
        Devuelve una descripcion válida y sin repetir. En caso de que ya exista agrega
        un sufijo.
        """
        descripcion = SUBSITUTE_ALFANUMERICO.sub('', descripcion)
        if cls._base_manager.filter(descripcion=descripcion).count() > 0:
            ultimo = 0
            copias = cls._base_manager.filter(descripcion__startswith=descripcion + '_')
            for archivo in copias:
                sufijo = archivo.descripcion.replace(descripcion + '_', '', 1)
                if sufijo.isdigit():
                    ultimo = max(ultimo, int(sufijo))
            descripcion = descripcion + '_' + str(ultimo + 1)

        return descripcion

    def usado_en_ivr(self):
        # Si esta usado en IVR no se puede borrar (si solo es usado en campañas si)
        return self.audio_principal_ivrs.exists() or \
            self.audio_time_out_ivrs.exists() or \
            self.audio_invalid_ivrs.exists()

    def usado_en_queue(self):
        # Si esta usado en alguna Queue no se puede borrar.

        # TODO: OML-496 - Asumo que el valor de announce es el path del anuncio periodico (audios)
        #       En caso de q no sea asi, agregar las siguientes lineas
        # if Queue.objects.filter(announce=self.audio_asterisk).exists():
        #    return True
        return self.queues_contestadores.exists() or \
            self.queues_ingreso.exists() or \
            self.queues_anuncio_periodico.exists()


class CampanaManager(models.Manager):

    def obtener_pausadas(self):
        """
        Devuelve campañas en estado pausadas.
        """
        return self.filter(estado=Campana.ESTADO_PAUSADA)

    def obtener_inactivas(self):
        """
        Devuelve campañas en estado pausadas.
        """
        return self.filter(estado=Campana.ESTADO_INACTIVA)

    def obtener_activas(self):
        """
        Devuelve campañas en estado activas.
        """
        return self.filter(estado=Campana.ESTADO_ACTIVA)

    def obtener_borradas(self):
        """
        Devuelve campañas en estado borradas.
        """
        return self.filter(estado=Campana.ESTADO_BORRADA)

    def obtener_all_except_borradas(self):
        """
        Devuelve campañas excluyendo las campanas borradas
        """
        return self.exclude(estado=Campana.ESTADO_BORRADA)

    def obtener_all_dialplan_asterisk(self):
        """
        Devuelve campañas excluyendo las campanas borradas
        """
        campanas_include = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                            Campana.ESTADO_INACTIVA]
        return self.filter(estado__in=campanas_include)

    def obtener_actuales(self):
        """
        Devuelve campañas excluyendo las campanas borradas
        """
        campanas_include = [Campana.ESTADO_ACTIVA, Campana.ESTADO_PAUSADA,
                            Campana.ESTADO_INACTIVA, Campana.ESTADO_FINALIZADA]
        return self.filter(estado__in=campanas_include)

    def get_objects_for_user(self, user):
        """
        Devuelve todos los objectos por cual tiene acceso este user.
        """
        return self.filter(reported_by=user)

    def obtener_campanas_dialer(self):
        """
        Devuelve campañas de tipo dialer
        """
        return self.filter(type=Campana.TYPE_DIALER)

    def obtener_campanas_entrantes(self):
        """
        Devuelve campañas de tipo entrantes
        """
        return self.filter(type=Campana.TYPE_ENTRANTE)

    def obtener_campanas_manuales(self):
        """
        Devuelve campañas de tipo manuales
        """
        return self.filter(type=Campana.TYPE_MANUAL)

    def obtener_campanas_preview(self):
        """
        Devuelve campañas de tipo preview
        """
        return self.filter(type=Campana.TYPE_PREVIEW)

    def obtener_campanas_asignadas_o_creadas_by_user(self, campanas, user):
        """
        IMPORTANTE: Unicamente para ser usado en AMB de campañas !!
        Devuelve las campanas creadas o a las que fue asignado como supervisor el user
        Incluye las BORRADAS
        :param campanas: queryset de campanas a filtrar
        :param user: usuario con supervisor_profile
        :return: campanas filtradas por usuaro
        """
        return campanas.filter(
            Q(supervisors=user) | Q(reported_by=user)).distinct()

    def obtener_ultimo_id_campana(self):
        last = self.last()
        if last:
            return last.pk
        return 0

    def obtener_templates_activos(self):
        """
        Devuelve templates campañas en estado activo.
        """
        return self.filter(estado=Campana.ESTADO_TEMPLATE_ACTIVO)

    def obtener_templates_activos_entrantes(self):
        """
        Devuelve templates de campañas entrantes en estado activo.
        """
        return self.obtener_campanas_entrantes().filter(estado=Campana.ESTADO_TEMPLATE_ACTIVO)

    def obtener_templates_activos_dialer(self):
        """
        Devuelve templates de campañas dialer en estado activo.
        """
        return self.obtener_campanas_dialer().filter(estado=Campana.ESTADO_TEMPLATE_ACTIVO)

    def obtener_templates_activos_manuales(self):
        """
        Devuelve templates de campañas manuales en estado activo.
        """
        return self.obtener_campanas_manuales().filter(estado=Campana.ESTADO_TEMPLATE_ACTIVO)

    def obtener_templates_activos_preview(self):
        """
        Devuelve templates de campañas preview en estado activo.
        """
        return self.obtener_campanas_preview().filter(estado=Campana.ESTADO_TEMPLATE_ACTIVO)

    def replicar_campana(self, campana, nombre_campana=None, bd_contacto=None):
        """
        Este método se encarga de replicar una campana existente, creando una
        campana nueva de iguales características.
        """
        assert isinstance(campana, Campana)

        ultimo_id = Campana.objects.obtener_ultimo_id_campana()
        nombre_sugerido = "CAMPANA_CLONADA_{0}".format(ultimo_id + 1)
        if nombre_campana:
            nombre_sugerido = nombre_campana

        base_datos_sugerida = campana.bd_contacto

        if bd_contacto:
            base_datos_sugerida = bd_contacto

        # Replica Campana.
        campana_replicada = self.create(
            nombre=nombre_sugerido,
            fecha_inicio=campana.fecha_inicio,
            fecha_fin=campana.fecha_fin,
            bd_contacto=base_datos_sugerida,
            type=campana.type,
            sitio_externo=campana.sitio_externo,
            tipo_interaccion=campana.tipo_interaccion,
            reported_by=campana.reported_by,
            objetivo=campana.objetivo,
        )

        # Se replican las opciones de calificación
        opciones_calificacion = []
        for opcion_calificacion in campana.opciones_calificacion.all():
            if not opcion_calificacion.es_agenda():
                # no se replica la opcion de calificación de agenda pues
                # debe crearse cuando se crea la campaña desde el wizard
                opcion_calificacion_replicada = OpcionCalificacion(
                    campana=campana_replicada, nombre=opcion_calificacion.nombre,
                    tipo=opcion_calificacion.tipo, formulario=opcion_calificacion.formulario)
                opciones_calificacion.append(opcion_calificacion_replicada)
        OpcionCalificacion.objects.bulk_create(opciones_calificacion)

        # se replican los parámetros para crm
        parametros_crm = []
        for parametro_crm in campana.parametros_crm.all():
            tipo = parametro_crm.tipo
            nombre = parametro_crm.nombre
            valor = parametro_crm.valor
            parametro_replicado = ParametrosCrm(
                campana=campana_replicada, tipo=tipo, nombre=nombre, valor=valor)
            parametros_crm.append(parametro_replicado)
        ParametrosCrm.objects.bulk_create(parametros_crm)

        # Replica Cola
        Queue.objects.create(
            campana=campana_replicada,
            name=campana_replicada.nombre,
            timeout=campana.queue_campana.timeout,
            retry=campana.queue_campana.retry,
            maxlen=campana.queue_campana.maxlen,
            wrapuptime=campana.queue_campana.wrapuptime,
            servicelevel=campana.queue_campana.servicelevel,
            strategy=campana.queue_campana.strategy,
            eventmemberstatus=campana.queue_campana.eventmemberstatus,
            eventwhencalled=campana.queue_campana.eventwhencalled,
            weight=campana.queue_campana.weight,
            ringinuse=campana.queue_campana.ringinuse,
            setinterfacevar=campana.queue_campana.setinterfacevar,
            wait=campana.queue_campana.wait,
            auto_grabacion=campana.queue_campana.auto_grabacion,
            detectar_contestadores=campana.queue_campana.detectar_contestadores,
            # TODO: OML-496
            announce=campana.queue_campana.announce,
            announce_frequency=campana.queue_campana.announce_frequency,
            audio_para_contestadores=campana.queue_campana.audio_para_contestadores,
            audio_de_ingreso=campana.queue_campana.audio_de_ingreso,
            initial_predictive_model=campana.queue_campana.initial_predictive_model,
            initial_boost_factor=campana.queue_campana.initial_boost_factor,

        )

        # Replica Actuacion Vigente
        ActuacionVigente.objects.create(
            campana=campana_replicada,
            domingo=campana.actuacionvigente.domingo,
            lunes=campana.actuacionvigente.lunes,
            martes=campana.actuacionvigente.martes,
            miercoles=campana.actuacionvigente.miercoles,
            jueves=campana.actuacionvigente.jueves,
            viernes=campana.actuacionvigente.viernes,
            sabado=campana.actuacionvigente.sabado,
            hora_desde=campana.actuacionvigente.hora_desde,
            hora_hasta=campana.actuacionvigente.hora_hasta,
        )

        # Replica Reglas Incidentes
        reglas = campana.reglas_incidencia.all()
        for regla in reglas:
            ReglasIncidencia.objects.create(
                campana=campana_replicada,
                estado=regla.estado,
                estado_personalizado=regla.estado_personalizado,
                intento_max=regla.intento_max,
                reintentar_tarde=regla.reintentar_tarde,
                en_modo=regla.en_modo,
            )

        return campana_replicada

    def obtener_activo_para_eliminar_crear_ver(self, campana_id):
        """Devuelve la campaña pasada por ID, siempre que dicha
        campaña pueda ser eliminada.

        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.filter(
                estado=Campana.ESTADO_TEMPLATE_ACTIVO).get(pk=campana_id)
        except Campana.DoesNotExist:
            raise(SuspiciousOperation("No se encontro campana/template %s en "
                                      "estado ESTADO_TEMPLATE_ACTIVO"))

    def replicar_campana_queue(self, campana):
        # TODO: No se esta usando
        """
        En este metodo vamos a crear una nueva cola y se la vamos a reasginar a la
        campana para eso vamos a crear un objecto Queue con los datos de actuales
        y vamos a eliminar la quueue de la campana asignada y vamos asiganar esta nueva
        creado
        :param campana: campana a asignar nueva cola
        """
        # Replica Cola
        queue_replicada = Queue(
            campana=campana,
            name=campana.nombre,
            timeout=campana.queue_campana.timeout,
            retry=campana.queue_campana.retry,
            maxlen=campana.queue_campana.maxlen,
            wrapuptime=campana.queue_campana.wrapuptime,
            servicelevel=campana.queue_campana.servicelevel,
            strategy=campana.queue_campana.strategy,
            eventmemberstatus=campana.queue_campana.eventmemberstatus,
            eventwhencalled=campana.queue_campana.eventwhencalled,
            weight=campana.queue_campana.weight,
            ringinuse=campana.queue_campana.ringinuse,
            setinterfacevar=campana.queue_campana.setinterfacevar,
            wait=campana.queue_campana.wait,
            auto_grabacion=campana.queue_campana.auto_grabacion,
            detectar_contestadores=campana.queue_campana.detectar_contestadores,
        )
        # Eliminamos queuue de la campana asignada
        queue_a_eliminar = Queue.objects.get(campana=campana)
        queue_a_eliminar.delete()
        # guardarmos la nueva queue
        queue_replicada.save()

    def obtener_canales_dialer_en_uso(self):
        campanas = self.obtener_activas() & self.obtener_campanas_dialer()
        canales_en_uso = campanas.aggregate(suma=Sum('queue_campana__maxlen'))['suma']
        return 0 if canales_en_uso is None else canales_en_uso

    def reciclar_campana(self, campana, bd_contacto):
        """
        Este método replica la campana pasada por parámetro con fin de
        reciclar la misma.
        """
        ultimo_id = Campana.objects.obtener_ultimo_id_campana()
        nombre = "CAMPANA_CLONADA_{0}_(reciclada)".format(ultimo_id + 1)
        campana_reciclada = self.replicar_campana(campana, nombre, bd_contacto)
        return campana_reciclada


class Campana(models.Model):
    """Una campaña del call center"""

    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = CampanaManager()

    ESTADO_ACTIVA = 2
    """La campaña esta activa, o sea, EN_CURSO o PROGRAMADA
    A nivel de modelos, solo queremos registrar si está ACTIVA, y no nos
    importa si esta EN_CURSO (o sea, si en este momento el daemon está
    generando llamadas asociadas a la campaña) o PROGRAMADA (si todavia no
    estamos en el rango de dias y horas en los que se deben generar
    las llamadas)
    """

    ESTADO_FINALIZADA = 3
    """La campaña fue finalizada, automatica o manualmente.
    Para mas inforacion, ver `finalizar()`"""

    ESTADO_BORRADA = 4
    """La campaña ya fue borrada"""

    ESTADO_PAUSADA = 5
    """La campaña pausada"""

    ESTADO_INACTIVA = 6
    """La campaña inactiva"""

    ESTADO_TEMPLATE_ACTIVO = 8
    """La campaña se creo como template y esta activa, en condición de usarse
    como tal."""

    ESTADO_TEMPLATE_BORRADO = 9
    """La campaña se creo como template y esta borrada, ya no puede usarse
    como tal."""

    ESTADOS = (
        (ESTADO_ACTIVA, _('Activa')),
        (ESTADO_FINALIZADA, _('Finalizada')),
        (ESTADO_BORRADA, _('Borrada')),
        (ESTADO_PAUSADA, _('Pausada')),
        (ESTADO_INACTIVA, _('Inactiva')),

        (ESTADO_TEMPLATE_ACTIVO, _('Template Activo')),
        (ESTADO_TEMPLATE_BORRADO, _('Template Borrado')),
    )

    TYPE_MANUAL = 1
    TYPE_MANUAL_DISPLAY = _('Manual')
    TYPE_DIALER = 2
    TYPE_DIALER_DISPLAY = _('Dialer')
    TYPE_ENTRANTE = 3
    TYPE_ENTRANTE_DISPLAY = _('Entrante')
    TYPE_PREVIEW = 4
    TYPE_PREVIEW_DISPLAY = _('Preview')

    TYPES_CAMPANA = (
        (TYPE_ENTRANTE, TYPE_ENTRANTE_DISPLAY),
        (TYPE_DIALER, TYPE_DIALER_DISPLAY),
        (TYPE_MANUAL, TYPE_MANUAL_DISPLAY),
        (TYPE_PREVIEW, TYPE_PREVIEW_DISPLAY),
    )

    FORMULARIO = 1
    "El tipo de interaccion es por formulario"

    SITIO_EXTERNO = 2
    "El tipo de interaccion es por sitio externo"

    TIPO_FORMULARIO_DISPLAY = _('Formulario')
    TIPO_SITIO_EXTERNO_DISPLAY = _('Url externa')

    TIPO_INTERACCION = (
        (FORMULARIO, TIPO_FORMULARIO_DISPLAY),
        (SITIO_EXTERNO, TIPO_SITIO_EXTERNO_DISPLAY)
    )

    TIEMPO_ACTUALIZACION_CONTACTOS = 1

    estado = models.PositiveIntegerField(
        choices=ESTADOS,
        default=ESTADO_INACTIVA,
    )
    nombre = models.CharField(max_length=128, unique=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    bd_contacto = models.ForeignKey(
        'BaseDatosContacto',
        null=True, blank=True,
        related_name="%(class)ss",
        on_delete=models.CASCADE
    )
    # Listas en formato JSON con los nombres de los campos
    campos_bd_no_editables = models.CharField(max_length=2052, default='')
    campos_bd_ocultos = models.CharField(max_length=2052, default='')

    oculto = models.BooleanField(default=False)
    # TODO: Sacar este campo
    campaign_id_wombat = models.IntegerField(null=True, blank=True)
    type = models.PositiveIntegerField(choices=TYPES_CAMPANA)
    sistema_externo = models.ForeignKey("SistemaExterno", null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='campanas')
    id_externo = models.CharField(max_length=128, null=True, blank=True)
    sitio_externo = models.ForeignKey("SitioExterno", null=True, blank=True,
                                      on_delete=models.CASCADE)
    tipo_interaccion = models.PositiveIntegerField(
        choices=TIPO_INTERACCION,
        default=FORMULARIO,
    )
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)

    outcid = models.CharField(max_length=128, null=True, blank=True)
    outr = models.ForeignKey('configuracion_telefonia_app.RutaSaliente', blank=True, null=True,
                             on_delete=models.CASCADE)

    # TODO: 'supervisors' debería referenciar a SupervisorProfile no a User
    supervisors = models.ManyToManyField(User, related_name="campanasupervisors")
    es_template = models.BooleanField(default=False)
    nombre_template = models.CharField(max_length=128, null=True, blank=True)
    es_manual = models.BooleanField(default=False)
    objetivo = models.PositiveIntegerField(default=0)

    # para uso en campañas preview
    tiempo_desconexion = models.PositiveIntegerField(default=0)
    campo_desactivacion = models.CharField(max_length=128, null=True, blank=True)

    mostrar_nombre = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def guardar_campaign_id_wombat(self, campaign_id_wombat):
        self.campaign_id_wombat = campaign_id_wombat
        self.save()

    def play(self):
        """Setea la campaña como ESTADO_ACTIVA"""
        logger.info(_("Seteando campana {0} como ESTADO_ACTIVA".format(self.id)))
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_ACTIVA
        self.save()

    def pausar(self):
        """Setea la campaña como ESTADO_PAUSADA"""
        logger.info("Seteando campana {0} como ESTADO_PAUSADA".format(self.id))
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_PAUSADA
        self.save()

    def activar(self):
        """Setea la campaña como ESTADO_ACTIVA"""
        logger.info(_("Seteando campana {0} como ESTADO_ACTIVA".format(self.id)))
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_ACTIVA
        self.save()

    def remover(self):
        """Setea la campaña como ESTADO_BORRADA"""
        logger.info(_("Seteando campana {0} como ESTADO_BORRADA".format(self.id)))
        if self.type == Campana.TYPE_PREVIEW:
            # eliminamos todos las entradas de AgenteEnContacto relativas a la campaña
            AgenteEnContacto.objects.filter(campana_id=self.pk).delete()
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_BORRADA
        self.save()

    def finalizar(self):
        """Setea la campaña como ESTADO_FINALIZADA"""
        logger.info(_("Seteando campana {0} como ESTADO_FINALIZADA".format(self.id)))
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_FINALIZADA
        self.save()

    def ocultar(self):
        """setea la campana como oculta"""
        self.oculto = True
        self.save()

    def desocultar(self):
        """setea la campana como visible"""
        self.oculto = False
        self.save()

    def valida_reglas_incidencia(self, regla_incidencia):
        """
        Este metodo valida si es posible agrega nueva regla de incidencia
        :param regla_incidencia: en una ReglaIncidencia
        :return: si es valida agregar
        """
        reglas_incidencia = [regla.estado for regla in self.reglas_incidencia.all()]

        valida = False
        for regla in reglas_incidencia:
            if regla is regla_incidencia.estado:
                valida = True
                break
        return valida

    def borrar_template(self):
        """
        Setea la campaña como BORRADA
        """
        logger.info(_("Seteando campana-->template {0} como BORRADA".format(self.id)))
        assert self.estado == Campana.ESTADO_TEMPLATE_ACTIVO

        self.estado = Campana.ESTADO_TEMPLATE_BORRADO
        self.save()

    def _crear_agente_en_contacto(self, contacto, agente_id, campos_contacto, estado, orden):
        datos_contacto = literal_eval(contacto.datos)
        datos_contacto = dict(zip(campos_contacto, datos_contacto))
        datos_contacto_json = json.dumps(datos_contacto)
        agente_en_contacto = AgenteEnContacto(
            agente_id=agente_id, contacto_id=contacto.pk, datos_contacto=datos_contacto_json,
            telefono_contacto=contacto.telefono, campana_id=self.pk, estado=estado, orden=orden)
        return agente_en_contacto

    def establecer_valores_iniciales_agente_contacto(
            self, asignacion_proporcional, asignacion_aleatoria):
        """
        Rellena con valores iniciales la tabla que informa el estado de los contactos
        en relación con los agentes
        """
        # obtenemos todos los contactos de la campaña
        campana_contactos = list(self.bd_contacto.contactos.all())

        # obtenemos los campos de la BD del contacto
        metadata = self.bd_contacto.get_metadata()
        campos_contacto = metadata.nombres_de_columnas_de_datos

        # creamos los objetos del modelo AgenteEnContacto a crear
        agente_en_contacto_list = []

        orden = AgenteEnContacto.ultimo_id() + 1
        if asignacion_proporcional and asignacion_aleatoria:
            random.shuffle(campana_contactos)
            agentes_campana = self.obtener_agentes()
            n_agentes_campana = agentes_campana.count()
            for agente, grupo_contactos in zip(agentes_campana,
                                               dividir_lista(campana_contactos, n_agentes_campana)):
                for contacto in grupo_contactos:
                    agente_en_contacto = self._crear_agente_en_contacto(
                        contacto, agente.pk, campos_contacto, AgenteEnContacto.ESTADO_INICIAL,
                        orden=orden)
                    orden += 1
                    agente_en_contacto_list.append(agente_en_contacto)
        elif asignacion_proporcional:
            agentes_campana = self.obtener_agentes()
            n_agentes_campana = agentes_campana.count()
            for agente, grupo_contactos in zip(agentes_campana,
                                               dividir_lista(campana_contactos, n_agentes_campana)):
                for contacto in grupo_contactos:
                    agente_en_contacto = self._crear_agente_en_contacto(
                        contacto, agente.pk, campos_contacto, AgenteEnContacto.ESTADO_INICIAL,
                        orden=orden)
                    orden += 1
                    agente_en_contacto_list.append(agente_en_contacto)
        else:
            for contacto in campana_contactos:
                agente_en_contacto = self._crear_agente_en_contacto(
                    contacto, -1, campos_contacto, AgenteEnContacto.ESTADO_INICIAL, orden=orden)
                orden += 1
                agente_en_contacto_list.append(agente_en_contacto)

        # insertamos las instancias en la BD
        AgenteEnContacto.objects.bulk_create(agente_en_contacto_list)

    def gestionar_finalizacion_relacion_agente_contacto(self, contacto_pk):
        """
        Marca como finalizada la relación entre un agente y un contacto de una campaña
        preview
        """
        try:
            agente_en_contacto = AgenteEnContacto.objects \
                .exclude(estado=AgenteEnContacto.ESTADO_FINALIZADO) \
                .get(contacto_id=contacto_pk, campana_id=self.pk)
        except AgenteEnContacto.DoesNotExist:
            # Si el contacto ya esta FINALIZADO, no hace falta actualizar.
            # para el caso cuando se llama al procedimiento luego de añadir un
            # nuevo contacto desde la consola de agentes
            pass
        else:
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_FINALIZADO
            agente_en_contacto.save()
            self.gestionar_finalizacion_por_contactos_calificados()

    def gestionar_finalizacion_por_contactos_calificados(self):
        # si todos los contactos de la campaña han sido calificados
        # o sea, tienen el valor 'estado' igual a FINALIZADO se eliminan todas
        # las entradas correspondientes a la campaña en el modelo AgenteEnContacto
        # y se marca la campaña como finalizada
        contactos_campana = AgenteEnContacto.objects.filter(campana_id=self.pk)
        n_contactos_campana = contactos_campana.count()
        n_contactos_atendidos = contactos_campana.filter(
            estado=AgenteEnContacto.ESTADO_FINALIZADO).count()
        if n_contactos_campana == n_contactos_atendidos:
            contactos_campana.delete()
            self.finalizar()

    def adicionar_agente_en_contacto(self, contacto, agente_id, es_originario=True):
        """Crea una nueva entrada para relacionar un agentes y un contacto
        nuevo a una campaña preview
        """
        metadata = self.bd_contacto.get_metadata()
        campos_contacto = metadata.nombres_de_columnas_de_datos
        datos_contacto = literal_eval(contacto.datos)
        datos_contacto = dict(zip(campos_contacto, datos_contacto))
        datos_contacto_json = json.dumps(datos_contacto)
        orden = AgenteEnContacto.ultimo_id() + 1
        AgenteEnContacto.objects.create(
            agente_id=agente_id, contacto_id=contacto.pk, datos_contacto=datos_contacto_json,
            telefono_contacto=contacto.telefono, campana_id=self.pk,
            estado=AgenteEnContacto.ESTADO_INICIAL,
            es_originario=es_originario, orden=orden)

    def get_string_queue_asterisk(self):
        if self.queue_campana:
            return self.queue_campana.get_string_queue_asterisk()

    def gestionar_opcion_calificacion_agenda(self):
        """
        Devuelve la opción de calificación de agenda para la campaña.
        En caso de no existir la crea.
        """
        OpcionCalificacion.objects.get_or_create(
            campana=self, nombre=settings.CALIFICACION_REAGENDA, tipo=OpcionCalificacion.AGENDA)

    def obtener_calificaciones(self):
        return CalificacionCliente.objects.filter(opcion_calificacion__campana_id=self.id)

    def obtener_historico_calificaciones(self):
        return CalificacionCliente.history.filter(opcion_calificacion__campana_id=self.id)

    def obtener_calificaciones_agenda(self):
        return CalificacionCliente.objects.filter(
            opcion_calificacion__campana_id=self.id,
            opcion_calificacion__tipo=OpcionCalificacion.AGENDA)

    def obtener_contactos_no_calificados(self):
        """Devuelve los contactos que no han sido calificados en la campaña"""
        contactos_calificados_ids = list(self.obtener_calificaciones().values_list(
            'contacto__pk', flat=True))
        contactos = self.bd_contacto.contactos.exclude(pk__in=contactos_calificados_ids)
        return contactos

    def update_basedatoscontactos(self, bd_nueva):
        """ Actualizar con nueva base datos de contacto"""
        self.bd_contacto = bd_nueva
        self.save()

    def save(self, *args, **kwargs):
        if self.tipo_interaccion == Campana.FORMULARIO and self.sitio_externo is not None:
            raise ValidationError(_('No se puede elegir un URL externo '
                                    'si selecciono un formulario.'))
        else:
            super(Campana, self).save(*args, **kwargs)

    def obtener_agentes(self):
        return self.queue_campana.members.all()

    def get_campos_no_editables(self):
        if self.campos_bd_no_editables:
            return json.loads(self.campos_bd_no_editables)
        return []

    def set_campos_no_editables(self, campos_no_editables, guardar=False):
        self.campos_bd_no_editables = ""
        if campos_no_editables:
            self.campos_bd_no_editables = json.dumps(campos_no_editables, separators=(',', ':'))
        if guardar:
            self.save()

    def get_campos_ocultos(self):
        if self.campos_bd_ocultos:
            return json.loads(self.campos_bd_ocultos)
        return []

    def set_campos_ocultos(self, campos_ocultos, guardar=False):
        self.campos_bd_ocultos = ""
        if campos_ocultos:
            self.campos_bd_ocultos = json.dumps(campos_ocultos, separators=(',', ':'))
        if guardar:
            self.save()

    @property
    def tiene_interaccion_con_sitio_externo(self):
        return self.tipo_interaccion == self.SITIO_EXTERNO

    @property
    def es_entrante(self):
        return self.type == self.TYPE_ENTRANTE


class OpcionCalificacion(models.Model):
    """
    Especifica el tipo de formulario al cual será redireccionada
    la gestión de un contacto en una campaña de acuerdo a la
    calificacion escogida
    """
    # no se redireccionara a ningún formulario, solo se salvará la calificación
    NO_ACCION = 0

    # será le dará tratamiento usando el formulario de gestión
    GESTION = 1

    # será le dará tratamiento usando el formulario de agenda cuando se elija la calificación
    # reservada para el sistema, no elegible por el usuario)
    AGENDA = 2

    FORMULARIO_CHOICES = (
        (GESTION, _('Gestión')),
        (NO_ACCION, _('Sin acción')),
        (AGENDA, _('Agenda')),
    )
    FORMULARIO_CHOICES_NO_AGENDA = (
        (GESTION, _('Gestión')),
        (NO_ACCION, _('Sin acción')),
    )
    campana = models.ForeignKey(
        Campana, on_delete=models.CASCADE, related_name='opciones_calificacion')
    tipo = models.IntegerField(choices=FORMULARIO_CHOICES, default=NO_ACCION)
    nombre = models.CharField(max_length=50)
    formulario = models.ForeignKey(Formulario, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(_('Opción "{0}" para campaña "{1}" de tipo "{2}"'.format(
            self.nombre, self.campana.nombre, self.get_tipo_display())))

    def es_agenda(self):
        return self.tipo == self.AGENDA

    def es_gestion(self):
        return self.tipo == self.GESTION

    def usada_en_calificacion(self):
        """
        Determina si opción de calificación está siendo usada en la campaña
        """
        return self.calificaciones_cliente.exists()

    def no_editable(self):
        """
        Determina si la opción de calificada puede ser editada/eliminada en la campaña
        """
        return self.es_agenda() or self.usada_en_calificacion()


class QueueManager(models.Manager):

    def obtener_all_except_borradas(self):
        """
        Devuelve queue excluyendo las campanas borradas
        """
        return self.exclude(campana__estado=Campana.ESTADO_BORRADA)


class Queue(models.Model):
    """
    Clase cola para el servidor de kamailio-debian
    """
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = QueueManager()

    RRORDERED = 'rrordered'
    # same as rrmemory, except the queue member order from config file is preserved

    LEASTRECENT = 'leastrecent'
    # ring interface which was least recently called by this queue"""

    FEWESTCALLS = 'fewestcalls'
    # ring the one with fewest completed calls from this queue

    RANDOM = 'random'
    # ring random interface

    RRMEMORY = 'rrmemory'
    # round robin with memory, remember where we left off last ring pass

    STRATEGY_CHOICES = (
        (RRORDERED, 'Rrordered'),
        (LEASTRECENT, 'Leastrecent'),
        (FEWESTCALLS, 'Fewestcalls'),
        (RANDOM, 'Random'),
        (RRMEMORY, 'Rremory'),
    )

    ANNOUNCE_HOLD_TIME_YES = 'yes'
    ANNOUNCE_HOLD_TIME_NO = 'no'
    ANNOUNCE_HOLD_TIME_ONCE = 'once'

    ANNOUNCE_HOLD_TIME_CHOICES = (
        (ANNOUNCE_HOLD_TIME_YES, _('Sí')),
        (ANNOUNCE_HOLD_TIME_NO, _('No')),
        (ANNOUNCE_HOLD_TIME_ONCE, _('Una sola vez')),
    )

    campana = models.OneToOneField(
        Campana,
        related_name='queue_campana', blank=True, null=True, on_delete=models.CASCADE
    )

    name = models.CharField(max_length=128, primary_key=True)
    timeout = models.BigIntegerField(verbose_name='Tiempo de Ring',
                                     null=True, blank=True)
    retry = models.BigIntegerField(verbose_name='Tiempo de Reintento',
                                   null=True, blank=True)
    maxlen = models.BigIntegerField(verbose_name='Cantidad Max de llamadas')
    wrapuptime = models.BigIntegerField(
        verbose_name='Tiempo de descanso entre llamadas')
    servicelevel = models.BigIntegerField(verbose_name='Nivel de Servicio')
    strategy = models.CharField(max_length=128, choices=STRATEGY_CHOICES,
                                verbose_name='Estrategia de distribucion')
    eventmemberstatus = models.BooleanField()
    eventwhencalled = models.BooleanField()
    weight = models.BigIntegerField(verbose_name='Importancia de campaña')
    ringinuse = models.BooleanField()
    setinterfacevar = models.BooleanField()
    members = models.ManyToManyField(AgenteProfile, through='QueueMember')

    wait = models.PositiveIntegerField(verbose_name='Tiempo de espera en cola')
    auto_grabacion = models.BooleanField(default=False,
                                         verbose_name='Grabar llamados')
    detectar_contestadores = models.BooleanField(default=False)
    ep_id_wombat = models.IntegerField(null=True, blank=True)

    # TODO: OML-496 Borrar, usar 'audios.audio_asterisk.name'
    # announcements
    announce_position = models.BooleanField(default=False)
    wait_announce_frequency = models.BigIntegerField(blank=True, null=True)
    announce = models.CharField(max_length=128, blank=True, null=True)
    announce_frequency = models.BigIntegerField(blank=True, null=True)

    audio_para_contestadores = models.ForeignKey(ArchivoDeAudio, blank=True, null=True,
                                                 on_delete=models.SET_NULL,
                                                 related_name='queues_contestadores')
    audio_de_ingreso = models.ForeignKey(ArchivoDeAudio, blank=True, null=True,
                                         on_delete=models.SET_NULL,
                                         related_name='queues_ingreso')
    audios = models.ForeignKey(ArchivoDeAudio, blank=True, null=True,
                               on_delete=models.SET_NULL,
                               related_name='queues_anuncio_periodico')
    dial_timeout = models.PositiveIntegerField(default=25, blank=True, null=True)

    # Predictiva
    initial_predictive_model = models.BooleanField(default=False)
    initial_boost_factor = models.DecimalField(
        default=1.0, max_digits=3, decimal_places=1, blank=True, null=True)

    # destino por failover
    destino = models.ForeignKey('configuracion_telefonia_app.DestinoEntrante',
                                related_name='campanas_destino_failover', blank=True, null=True,
                                on_delete=models.CASCADE)

    # para permitir al usuario especificar el tiempo promedio  que deberá
    # esperar el llamante para ser atendido
    announce_holdtime = models.CharField(max_length=128, default=ANNOUNCE_HOLD_TIME_NO,
                                         choices=ANNOUNCE_HOLD_TIME_CHOICES)
    # ivr break down
    ivr_breakdown = models.ForeignKey('configuracion_telefonia_app.DestinoEntrante',
                                      related_name='campanas_ivr_breakdown', blank=True,
                                      null=True, on_delete=True)

    musiconhold = models.ForeignKey('configuracion_telefonia_app.Playlist',
                                    related_name='campanas', blank=True, null=True,
                                    on_delete=models.SET_NULL)

    # campos que no usamos
    context = models.CharField(max_length=128, blank=True, null=True)
    monitor_join = models.NullBooleanField(blank=True, null=True)
    monitor_format = models.CharField(max_length=128, blank=True, null=True)
    queue_youarenext = models.CharField(max_length=128, blank=True, null=True)
    queue_thereare = models.CharField(max_length=128, blank=True, null=True)
    queue_callswaiting = models.CharField(max_length=128, blank=True, null=True)
    queue_holdtime = models.CharField(max_length=128, blank=True, null=True)
    queue_minutes = models.CharField(max_length=128, blank=True, null=True)
    queue_seconds = models.CharField(max_length=128, blank=True, null=True)
    queue_lessthan = models.CharField(max_length=128, blank=True, null=True)
    queue_thankyou = models.CharField(max_length=128, blank=True, null=True)
    queue_reporthold = models.CharField(max_length=128, blank=True, null=True)
    announce_round_seconds = models.BigIntegerField(blank=True, null=True)
    joinempty = models.CharField(max_length=128, blank=True, null=True)
    leavewhenempty = models.CharField(max_length=128, blank=True, null=True)
    reportholdtime = models.NullBooleanField(blank=True, null=True)
    memberdelay = models.BigIntegerField(blank=True, null=True)
    timeoutrestart = models.NullBooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    def guardar_ep_id_wombat(self, ep_id_wombat):
        self.ep_id_wombat = ep_id_wombat
        self.save()

    def get_string_initial_predictive_model(self):
        if self.initial_predictive_model:
            return "ADAPTIVE"
        return "OFF"

    class Meta:
        db_table = 'queue_table'


class QueueMemberManager(models.Manager):

    def obtener_member_por_queue(self, queue):
        """Devuelve el quemeber filtrando por queue
        """
        return self.filter(queue_name=queue)

    def obtener_queue_por_agent(self, agent_id):
        """Devuelve el queue filtrando por agent_id
        """
        return self.filter(member_id=agent_id).values_list('id_campana', flat=True)

    def obtener_penalty_por_agent(self, agent_id):
        """Devuelve el penalty de queue filtrando por agent_id
        """
        return self.filter(member_id=agent_id).values_list('penalty', flat=True)

    def existe_member_queue(self, member, queue):
        return self.obtener_member_por_queue(queue).filter(
            member=member).exists()

    def get_campanas_activas(self):
        return self.filter(queue_name__campana__estado=Campana.ESTADO_ACTIVA)

    def borrar_member_queue(self, member):
        return self.filter(member=member).delete()


class QueueMember(models.Model):
    """
    Clase cola por miembro, agente en cada cola
    """

    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = QueueMemberManager()

    """Considero opciones solo del 0 a 9"""
    (CERO, UNO, DOS, TRES, CUATRO,
     CINCO, SEIS, SIETE, OCHO, NUEVE) = range(0, 10)
    DIGITO_CHOICES = (
        (CERO, '0'),
        (UNO, '1'),
        (DOS, '2'),
        (TRES, '3'),
        (CUATRO, '4'),
        (CINCO, '5'),
        (SEIS, '6'),
        (SIETE, '7'),
        (OCHO, '8'),
        (NUEVE, '9'),
    )
    member = models.ForeignKey(AgenteProfile, on_delete=models.CASCADE,
                               related_name='campana_member')
    queue_name = models.ForeignKey(Queue, on_delete=models.CASCADE,
                                   db_column='queue_name',
                                   related_name='queuemember')
    membername = models.CharField(max_length=128)
    interface = models.CharField(max_length=128)
    penalty = models.IntegerField(choices=DIGITO_CHOICES)
    paused = models.IntegerField()
    id_campana = models.CharField(max_length=128)

    def __str__(self):
        return str(_("agente: {0} para la campana {1} ".format(
            self.member.user.get_full_name(), self.queue_name)))

    @classmethod
    def get_defaults(cls, agente, campana):
        """Devuelve los valores por defecto que se asigan al momento de adicionar
        un agente a una campaña
        """
        return {'membername': agente.user.get_full_name(),
                'interface': """Local/{0}@from-queue/n""".format(
                    agente.sip_extension),
                'penalty': 0,
                'paused': 0,
                'id_campana': "{0}_{1}".format(campana.id, campana.nombre)}

    class Meta:
        db_table = 'queue_member_table'
        unique_together = ('queue_name', 'member',)


class PausaManager(models.Manager):
    def activas(self):
        return self.filter(eliminada=False)

    def eliminadas(self):
        return self.filter(eliminada=True)

    def activa_by_pauseid(self, pause_id):
        return self.get(eliminada=False, id=pause_id)


class Pausa(models.Model):
    objects = PausaManager()

    TIPO_PRODUCTIVA = 'P'
    CHOICE_PRODUCTIVA = _('Productiva')
    TIPO_RECREATIVA = 'R'
    CHOICE_RECREATIVA = _('Recreativa')
    TIPO_CHOICES = ((TIPO_PRODUCTIVA, CHOICE_PRODUCTIVA), (TIPO_RECREATIVA, CHOICE_RECREATIVA))
    nombre = models.CharField(max_length=20, unique=True, verbose_name=_('Nombre'))
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=TIPO_PRODUCTIVA,
                            verbose_name=_('Tipo'))
    eliminada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def es_productiva(self):
        return self.tipo == self.TIPO_PRODUCTIVA

    def get_tipo(self):
        if self.es_productiva():
            return self.CHOICE_PRODUCTIVA
        return self.CHOICE_RECREATIVA

# ==============================================================================
# Base Datos Contactos
# ==============================================================================


class BaseDatosContactoManager(models.Manager):
    """Manager para BaseDatosContacto"""

    def obtener_definidas(self):
        """
        Este método filtra lo objetos BaseDatosContacto que
        esté definidos no mostrando ocultas.
        """
        definidas = [BaseDatosContacto.ESTADO_DEFINIDA,
                     BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA]
        return self.filter(estado__in=definidas, oculto=False).order_by(
            'fecha_alta')

    def obtener_definidas_ocultas(self):
        """
        Este método filtra lo objetos BaseDatosContacto que
        esté definidos mostrando ocultas
        """
        definidas = [BaseDatosContacto.ESTADO_DEFINIDA,
                     BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA]
        return self.filter(estado__in=definidas).order_by('fecha_alta')

    def obtener_en_definicion_para_editar(self, base_datos_contacto_id):
        """Devuelve la base datos pasada por ID, siempre que pueda ser editada.
        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.filter(
                estado=BaseDatosContacto.ESTADO_EN_DEFINICION).get(
                pk=base_datos_contacto_id)
        except BaseDatosContacto.DoesNotExist:
            raise(SuspiciousOperation(_("No se encontro base datos en "
                                        "estado ESTADO_EN_DEFINICION")))

    def obtener_en_actualizada_para_editar(self, base_datos_contacto_id):
        """Devuelve la base datos pasada por ID, siempre que pueda ser editada.
        En caso de no encontarse, lanza SuspiciousOperation
        """
        definicion = [BaseDatosContacto.ESTADO_EN_DEFINICION,
                      BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA]
        try:
            return self.filter(
                estado__in=definicion).get(pk=base_datos_contacto_id)
        except BaseDatosContacto.DoesNotExist:
            raise(SuspiciousOperation(_("No se encontro base datos en "
                                        "estado ESTADO_EN_DEFINICION o ACTULIZADA")))

    def obtener_definida_para_depurar(self, base_datos_contacto_id):
        """Devuelve la base datos pasada por ID, siempre que pueda ser
        depurada.
        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.filter(
                estado=BaseDatosContacto.ESTADO_DEFINIDA).get(
                pk=base_datos_contacto_id)
        except BaseDatosContacto.DoesNotExist:
            raise(SuspiciousOperation(_("No se encontro base datos en "
                                        "estado ESTADO_EN_DEFINICION")))


def upload_to(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    return "archivos_importacion/%Y/%m/{0}-{1}".format(
        str(uuid.uuid4()), filename)[:95]


# upload_to_archivos_importacion = upload_to("archivos_importacion", 95)


class MetadataBaseDatosContactoDTO(object):
    """Encapsula acceso a metadatos de BaseDatosContacto"""

    def __init__(self):
        self._metadata = {}

    # -----

    @property
    def cantidad_de_columnas(self):
        try:
            return self._metadata['cant_col']
        except KeyError:
            raise(ValueError(_("La cantidad de columnas no ha sido seteada")))

    @cantidad_de_columnas.setter
    def cantidad_de_columnas(self, cant):
        assert isinstance(cant, int), ("'cantidad_de_columnas' "
                                       "debe ser int. Se encontro: {0}".format(type(cant)))

        assert cant > 0, ("'cantidad_de_columnas' "
                          "debe ser > 0. Se especifico {0}".format(cant))

        self._metadata['cant_col'] = cant

    # -----

    @property
    def columna_con_telefono(self):
        try:
            return self._metadata['col_telefono']
        except KeyError:
            raise(ValueError(_("No se ha seteado 'columna_con_telefono'")))

    @columna_con_telefono.setter
    def columna_con_telefono(self, columna):
        columna = int(columna)
        assert columna < self.cantidad_de_columnas, ("No se puede setear "
                                                     "'columna_con_telefono' = {0} porque  la BD "
                                                     "solo posee {1} columnas"
                                                     "".format(columna, self.cantidad_de_columnas))
        self._metadata['col_telefono'] = columna

    # -----

    @property
    def columnas_con_telefono(self):
        try:
            return self._metadata['cols_telefono']
        except KeyError:
            return []

    @columnas_con_telefono.setter
    def columnas_con_telefono(self, columnas):
        """
        Parametros:
        - columnas: Lista de enteros que indican las columnas con telefonos.
        """
        assert isinstance(columnas, (list, tuple)), ("'columnas_con_telefono' "
                                                     "recibe listas o tuplas. "
                                                     "Se recibio: {0}".format(type(columnas)))
        for col in columnas:
            assert isinstance(col, int), ("Los elementos de "
                                          "'columnas_con_telefono' deben ser int. "
                                          "Se encontro: {0}".format(
                                              type(col)))
            assert col < self.cantidad_de_columnas, ("No se puede setear "
                                                     "'columnas_con_telefono' = {0} porque  la BD "
                                                     "solo posee {1} columnas"
                                                     "".format(col, self.cantidad_de_columnas))

        self._metadata['cols_telefono'] = columnas

    # -----

    @property
    def columna_id_externo(self):
        try:
            return self._metadata['col_id_externo']
        except KeyError:
            return None

    @columna_id_externo.setter
    def columna_id_externo(self, columna_id_externo):
        """
        Parametros:
        - Un entero que indica la columna con campo id externo.
        """
        assert isinstance(columna_id_externo, int), ("'columna_id_externo' debe ser int. "
                                                     "Se recibio: {0}"
                                                     "".format(type(columna_id_externo)))
        self._metadata['col_id_externo'] = columna_id_externo

    @property
    def nombre_campo_id_externo(self):
        if self.columna_id_externo is not None:
            return self._metadata['nombres_de_columnas'][self.columna_id_externo]
        return None

    # ----

    @property
    def columnas_con_fecha(self):
        try:
            return self._metadata['cols_fecha']
        except KeyError:
            return []

    @columnas_con_fecha.setter
    def columnas_con_fecha(self, columnas):
        """
        Parametros:
        - columnas: Lista de enteros que indican las columnas con fechas.
        """
        assert isinstance(columnas, (list, tuple)), ("'columnas_con_fecha' "
                                                     "recibe listas o tuplas."
                                                     " Se recibio: {0}".format(type(columnas)))
        for col in columnas:
            assert isinstance(col, int), ("Los elementos de "
                                          "'columnas_con_fecha' deben ser int. "
                                          "Se encontro: {0}".format(type(col)))
            assert col < self.cantidad_de_columnas, ("No se puede setear "
                                                     "'columnas_con_fecha' = {0} porque  la BD"
                                                     " solo posee {1} columnas"
                                                     "".format(col, self.cantidad_de_columnas))

        self._metadata['cols_fecha'] = columnas

    # -----

    @property
    def columnas_con_hora(self):
        try:
            return self._metadata['cols_hora']
        except KeyError:
            return []

    @columnas_con_hora.setter
    def columnas_con_hora(self, columnas):
        """
        Parametros:
        - columnas: Lista de enteros que indican las columnas con horas.
        """
        assert isinstance(columnas, (list, tuple)), ("'columnas_con_hora' "
                                                     "recibe listas o tuplas. "
                                                     "Se recibio: {0}".format(type(columnas)))
        for col in columnas:
            assert isinstance(col, int), ("Los elementos de "
                                          "'columnas_con_hora' deben ser int. "
                                          "Se encontro: {0}".format(type(col)))
            assert col < self.cantidad_de_columnas, ("No se puede setear "
                                                     "'columnas_con_hora' = {0} porque  la BD solo "
                                                     "posee {1} columnas"
                                                     "".format(col, self.cantidad_de_columnas))

        self._metadata['cols_hora'] = columnas

    # -----

    @property
    def nombre_campo_telefono(self):
        try:
            indice_campo_telefono = self._metadata['cols_telefono'][0]
            return self._metadata['nombres_de_columnas'][indice_campo_telefono]
        except KeyError:
            return []

    @property
    def nombres_de_columnas(self):
        try:
            return self._metadata['nombres_de_columnas']
        except KeyError:
            return []

    @nombres_de_columnas.setter
    def nombres_de_columnas(self, columnas):
        """
        Parametros:
        - columnas: Lista de strings con nombres de las
                    columnas.
        """
        assert isinstance(columnas, (list, tuple)), ("'nombres_de_columnas' "
                                                     "recibe listas o tuplas. "
                                                     "Se recibio: {0}".format(type(columnas)))
        assert len(columnas) == self.cantidad_de_columnas, ("Se intentaron "
                                                            "setear {0} nombres de columnas, pero"
                                                            " la BD posee {1} columnas"
                                                            "".format(len(columnas),
                                                                      self.cantidad_de_columnas))

        self._metadata['nombres_de_columnas'] = columnas

    @property
    def nombres_de_columnas_de_telefonos(self):
        return [self.nombres_de_columnas[i] for i in self.columnas_con_telefono]

    @property
    def nombres_de_columnas_de_datos(self):
        if not hasattr(self, '_nombres_de_columnas_de_datos'):
            try:
                nombres_de_columnas = self._metadata['nombres_de_columnas']
                self._nombres_de_columnas_de_datos = [x for x in nombres_de_columnas
                                                      if not x == self.nombre_campo_telefono and
                                                      not x == self.nombre_campo_id_externo]
            except KeyError:
                return []

        return self._nombres_de_columnas_de_datos

    @property
    def primer_fila_es_encabezado(self):
        try:
            return self._metadata['prim_fila_enc']
        except KeyError:
            raise(ValueError(_("No se ha seteado si primer "
                               "fila es encabezado")))

    @primer_fila_es_encabezado.setter
    def primer_fila_es_encabezado(self, es_encabezado):
        assert isinstance(es_encabezado, bool)

        self._metadata['prim_fila_enc'] = es_encabezado

    def obtener_telefono_de_dato_de_contacto(self, datos_json):
        """Devuelve el numero telefonico del contacto.

        :param datos: atribuito 'datos' del contacto, o sea, valores de
                      las columnas codificadas con json
        """
        col_telefono = self._metadata['col_telefono']
        try:
            datos = json.loads(datos_json)
        except Exception as e:
            logger.exception(_("Error: {0} detectada al desserializar "
                               "datos extras. Datos extras: '{1}'"
                               "".format(e, datos_json)))
            raise

        assert len(datos) == self.cantidad_de_columnas

        telefono = datos[col_telefono]
        return telefono

    def validar_metadatos(self):
        """Valida que los datos de metadatos estan completos"""
        assert self.cantidad_de_columnas > 0, "cantidad_de_columnas es <= 0"
        assert self.columna_con_telefono >= 0, "columna_con_telefono < 0"
        assert self.columna_con_telefono < self.cantidad_de_columnas, \
            "columna_con_telefono >= cantidad_de_columnas"

        for index_columna in self.columnas_con_fecha:
            assert index_columna >= 0, "columnas_con_fecha: index_columna < 0"
            assert index_columna < self.cantidad_de_columnas, (
                ""
                "columnas_con_fecha: "
                "index_columna >= cantidad_de_columnas")

        for index_columna in self.columnas_con_hora:
            assert index_columna >= 0, "columnas_con_hora: index_columna < 0"
            assert index_columna < self.cantidad_de_columnas, (
                ""
                "columnas_con_hora: "
                "index_columna >= cantidad_de_columnas")

        assert len(self.nombres_de_columnas) == self.cantidad_de_columnas, \
            "len(nombres_de_columnas) != cantidad_de_columnas"

        validador = ValidadorDeNombreDeCampoExtra()
        for nombre_columna in self.nombres_de_columnas:
            assert validador.validar_nombre_de_columna(nombre_columna), \
                "El nombre del campo extra / columna no es valido"

        assert self.primer_fila_es_encabezado in (True, False), \
            "primer_fila_es_encabezado no es un booleano valido"

    def dato_extra_es_hora(self, nombre_de_columna):
        """
        Devuelve True si el dato extra correspondiente a la columna
        con nombre `nombre_de_columna` ha sido seteada con el
        tipo de dato `hora`.

        Este metodo no realiza ningun tipo de sanitizacion del nombre
        de columna recibido por parametro! Se supone que el nombre
        de columna es valido y existe.

        :raises ValueError: si la columna no existe
        """
        index = self.nombres_de_columnas.index(nombre_de_columna)
        return index in self.columnas_con_hora

    def dato_extra_es_fecha(self, nombre_de_columna):
        """
        Devuelve True si el dato extra correspondiente a la columna
        con nombre `nombre_de_columna` ha sido seteada con el
        tipo de dato `fecha`.

        Este metodo no realiza ningun tipo de sanitizacion del nombre
        de columna recibido por parametro! Se supone que el nombre
        de columna es valido y existe.

        :raises ValueError: si la columna no existe
        """
        index = self.nombres_de_columnas.index(nombre_de_columna)
        return index in self.columnas_con_fecha

    def dato_extra_es_telefono(self, nombre_de_columna):
        """
        Devuelve True si el dato extra correspondiente a una columna
        con numero telefonico.

        Este metodo no realiza ningun tipo de sanitizacion del nombre
        de columna recibido por parametro! Se supone que el nombre
        de columna es valido y existe.

        :raises ValueError: si la columna no existe
        """
        index = self.nombres_de_columnas.index(nombre_de_columna)
        return index in self.columnas_con_telefono

    def dato_extra_es_generico(self, nombre_de_columna):
        """
        Devuelve True si el dato extra correspondiente a la columna
        con nombre `nombre_de_columna` es de tipo generico, o sea
        debe ser tratado como texto (ej: no es el nro de telefono,
        ni hora ni fecha)

        Este metodo no realiza ningun tipo de sanitizacion del nombre
        de columna recibido por parametro! Se supone que el nombre
        de columna es valido y existe.

        :raises ValueError: si la columna no existe
        """
        index = self.nombres_de_columnas.index(nombre_de_columna)
        index_in_columnas_hora = (index in self.columnas_con_hora)
        index_in_columnas_fecha = (index in self.columnas_con_fecha)
        index_columna_telefono = (index == self.columna_con_telefono)
        return not (index_in_columnas_hora or index_in_columnas_fecha or index_columna_telefono)


class MetadataBaseDatosContacto(MetadataBaseDatosContactoDTO):
    """Encapsula acceso a metadatos de BaseDatosContacto"""

    def __init__(self, bd):
        super(MetadataBaseDatosContacto, self).__init__()
        self.bd = bd
        if bd.metadata is not None and bd.metadata != '':
            try:
                self._metadata = json.loads(bd.metadata)
            except Exception as e:
                logger.exception(_("Error: {0} detectada al desserializar "
                                   "metadata de la bd {1}".format(e, bd.id)))
                raise

    # -----

    def save(self):
        """Guardar los metadatos en la instancia de BaseDatosContacto"""
        # Primero validamos
        # FIXME Fede ahora vamos a comentar validación
        # self.validar_metadatos()

        # Ahora guardamos
        try:
            self.bd.metadata = json.dumps(self._metadata)
            self.bd.save()
        except Exception as e:
            logger.exception(_("Error: {0} detectada al serializar "
                               "metadata de la bd {1}".format(e, self.bd.id)))
            raise


class BaseDatosContacto(models.Model):
    objects = BaseDatosContactoManager()

    DATO_EXTRA_GENERICO = _('GENERICO')
    DATO_EXTRA_FECHA = _('FECHA')
    DATO_EXTRA_HORA = _('HORA')

    DATOS_EXTRAS = (
        (DATO_EXTRA_GENERICO, _('Dato Genérico')),
        (DATO_EXTRA_FECHA, _('Fecha')),
        (DATO_EXTRA_HORA, _('Hora')),
    )

    ESTADO_EN_DEFINICION = 0
    ESTADO_DEFINIDA = 1
    ESTADO_EN_DEPURACION = 2
    ESTADO_DEPURADA = 3
    ESTADO_DEFINIDA_ACTUALIZADA = 4
    ESTADOS = (
        (ESTADO_EN_DEFINICION, _('En Definición')),
        (ESTADO_DEFINIDA, _('Definida')),
        (ESTADO_EN_DEPURACION, _('En Depuracion')),
        (ESTADO_DEPURADA, _('Depurada')),
        (ESTADO_DEFINIDA_ACTUALIZADA, _('Definida en actualizacion'))
    )

    nombre = models.CharField(
        max_length=128, unique=True, verbose_name=_('Nombre')
    )
    fecha_alta = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Fecha alta')
    )
    archivo_importacion = models.FileField(
        upload_to=upload_to,
        max_length=256,
        verbose_name=_('Archivo de importación')
    )
    nombre_archivo_importacion = models.CharField(
        max_length=256, verbose_name=_('Nombre Archivo de importación')
    )
    metadata = models.TextField(null=True, blank=True)
    sin_definir = models.BooleanField(
        default=True,
    )
    cantidad_contactos = models.PositiveIntegerField(
        default=0
    )
    estado = models.PositiveIntegerField(
        choices=ESTADOS,
        default=ESTADO_EN_DEFINICION,
    )
    oculto = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Base de datos")
        verbose_name_plural = _("Base de datos")

    def __str__(self):
        return "{0}: ({1} contactos)".format(self.nombre,
                                             self.cantidad_contactos)

    def get_metadata(self):
        return MetadataBaseDatosContacto(self)

    def define(self):
        """
        Este método se encara de llevar a cabo la definición del
        objeto BaseDatosContacto. Establece el atributo sin_definir
        en False haciedo que quede disponible el objeto.
        """
        assert self.estado in (BaseDatosContacto.ESTADO_EN_DEFINICION,
                               BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA)
        logger.info(_("Seteando base datos contacto {0} como definida".format(self.id)))
        self.sin_definir = False

        self.estado = self.ESTADO_DEFINIDA
        self.save()

    def get_cantidad_contactos(self):
        """
        Devuelve la cantidad de contactos de la BaseDatosContacto.
        """

        return self.cantidad_contactos

    # def verifica_en_uso(self):
    #     """
    #     Este método se encarga de verificar si la base de datos esta siendo
    #     usada por alguna campaña que este activa o pausada.
    #     Devuelve  booleano.
    #     """
    #     estados_campanas = [campana.estado for campana in self.campanas.all()]
    #     if any(estado == Campana.ESTADO_ACTIVA for estado in estados_campanas):
    #         return True
    #     return False

    def verifica_depurada(self):
        """
        Este método se encarga de verificar si la base de datos esta siendo
        depurada o si ya fue depurada.
        Devuelve booleano.
        """
        if self.estado in (self.ESTADO_EN_DEPURACION, self.ESTADO_DEPURADA):
            return True
        return False

    def elimina_contactos(self):
        """
        Este método se encarga de eliminar todos los contactos de la
        BaseDatoContacto actual.
        El estado de la base de datos tiene que ser ESTADO_EN_DEFINICION o
        ESTADO_EN_DEPURACION, no se deberían eliminar los contactos con la
        misma en otro estado.
        """
        assert self.estado in (self.ESTADO_EN_DEFINICION,
                               self.ESTADO_EN_DEPURACION)
        self.contactos.all().delete()

    # def procesa_depuracion(self):
    #     """
    #     Este método se encarga de llevar el proceso de depuración de
    #     BaseDatoContacto invocando a los métodos que realizan las distintas
    #     acciones.
    #     """
    #
    #     if self.estado != BaseDatosContacto.ESTADO_DEFINIDA:
    #         raise(SuspiciousOperation("La BD {0} NO se puede depurar porque "
    #                                   "no esta en estado ESTADO_DEFINIDA. "
    #                                   "Estado: {1}".format(self.pk,
    #                                                        self.estado)))
    #
    #     # 1) Cambio de estado BaseDatoContacto (ESTADO_EN_DEPURACION).
    #     logger.info("Iniciando el proceso de depurado de BaseDatoContacto:"
    #                 "Seteando base datos contacto %s como"
    #                 "ESTADO_EN_DEPURACION.", self.id)
    #
    #     self.estado = self.ESTADO_EN_DEPURACION
    #     self.save()
    #
    #     # 2) Llamada a método que hace el COPY / dump.
    #     Contacto.objects.realiza_dump_contactos(self)
    #
    #     # 3) Llama el método que hace el borrado de los contactos.
    #     self.elimina_contactos()
    #
    #     # 4) Cambio de estado BaseDatoContacto (ESTADO_DEPURADA).
    #     logger.info("Finalizando el proceso de depurado de "
    #                 "BaseDatoContacto: Seteando base datos contacto %s "
    #                 "como ESTADO_DEPURADA.", self.id)
    #     self.estado = self.ESTADO_DEPURADA
    #     self.save()

    def copia_para_reciclar(self):
        """
        Este método se encarga de duplicar la base de datos de contactos
        actual.
        NO realiza la copia de los contactos de la misma.
        """
        # obtiene ultimo id de BaseDatosContacto, le suma 1 y se usa
        # para generar el nuevo nombre
        last_bd_contacto = BaseDatosContacto.objects.last()
        if last_bd_contacto:
            bd_reciclada_id = last_bd_contacto.pk + 1
        else:
            bd_reciclada_id = 0
        copia = BaseDatosContacto.objects.create(
            nombre='{0}-{1} (reciclada)'.format(self.nombre, bd_reciclada_id),
            archivo_importacion=self.archivo_importacion,
            nombre_archivo_importacion=self.nombre_archivo_importacion,
            metadata=self.metadata,
        )
        return copia

    def ocultar(self):
        """setea la base de datos como oculta"""
        self.oculto = True
        self.save()

    def desocultar(self):
        """setea la base de datos como visible"""
        self.oculto = False
        self.save()

    def genera_contactos(self, lista_contactos):
        """
        Este metodo se encarga de realizar la generación de contactos
        a partir de una lista de contactos.
        Parametros:
        - lista_contactos: lista de contactos.
        """

        for contacto in lista_contactos:
            Contacto.objects.create(
                telefono=contacto.telefono,
                datos=contacto.datos,
                bd_contacto=self,
            )
        self.cantidad_contactos = len(lista_contactos)


class ContactoManager(models.Manager):

    def contactos_by_telefono(self, telefono):
        try:
            return self.filter(telefono__contains=telefono)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "número télefonico"))

    def contactos_by_filtro_bd_contacto(self, bd_contacto, filtro):
        """ Busqueda en todos los campos relevantes """
        try:
            contactos = self.filter(Q(telefono__contains=filtro) | Q(datos__contains=filtro))
            return contactos.filter(bd_contacto=bd_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "filtro"))

    # def obtener_contacto_editar(self, id_cliente):
    #     """Devuelve el contacto pasado por ID, siempre que dicha
    #     pedido pueda ser editar
    #     FIXME: chequear que sea unico el id_cliente no está definido asi en el
    #     modelo
    #     En caso de no encontarse, lanza SuspiciousOperation
    #     """
    #     try:
    #         return self.get(id_cliente=id_cliente)
    #     except Contacto.DoesNotExist:
    #         return None

    def contactos_by_bd_contacto(self, bd_contacto):
        try:
            return self.filter(bd_contacto=bd_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con este "
                                         "base de datos de contactos")))

    def contactos_by_bds_contacto(self, bds_contacto):
        try:
            return self.filter(bd_contacto__in=bds_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontraron contactos con esas "
                                         "bases de datos de contactos")))

    # def contactos_by_bd_contacto_sin_duplicar(self, bd_contacto):
    #     try:
    #         return self.values('telefono', 'id_cliente', 'datos').\
    #             filter(bd_contacto=bd_contacto).distinct()
    #     except Contacto.DoesNotExist:
    #         raise (SuspiciousOperation("No se encontro contactos con este "
    #                                    "base de datos de contactos"))


class Contacto(models.Model):
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = ContactoManager()

    telefono = models.CharField(max_length=128)
    datos = models.TextField()
    bd_contacto = models.ForeignKey(
        'BaseDatosContacto',
        related_name='contactos', blank=True, null=True,
        on_delete=models.CASCADE
    )
    id_externo = models.CharField(max_length=128, null=True)
    es_originario = models.BooleanField(default=True)

    def obtener_datos(self):
        """ Devuelve un diccionario con todos los datos, incluido el telefono """
        if not hasattr(self, 'datos_contacto'):
            bd_metadata = self.bd_contacto.get_metadata()
            columnas = bd_metadata.nombres_de_columnas
            datos = self.lista_de_datos()
            pos_primer_telefono = bd_metadata.columnas_con_telefono[0]
            if bd_metadata.columna_id_externo is not None:
                # Inserto primero el de menor indice para que se respete el orden
                if (pos_primer_telefono < bd_metadata.columna_id_externo):
                    datos.insert(pos_primer_telefono, self.telefono)
                    datos.insert(bd_metadata.columna_id_externo, self.id_externo)
                else:
                    datos.insert(bd_metadata.columna_id_externo, self.id_externo)
                    datos.insert(pos_primer_telefono, self.telefono)
            else:
                datos.insert(pos_primer_telefono, self.telefono)

            self.datos_contacto = dict(zip(columnas, datos))
        return self.datos_contacto

    def _sincronizar_agente_en_contacto(self):
        # obtenemos los campos de la BD del contacto
        metadata = self.bd_contacto.get_metadata()
        campos_contacto = metadata.nombres_de_columnas_de_datos

        # y los hacemos en estructura json para AgenteEnContacto
        datos_contacto = literal_eval(self.datos)
        datos_contacto = dict(zip(campos_contacto, datos_contacto))
        datos_contacto_json = json.dumps(datos_contacto)
        AgenteEnContacto.objects.filter(contacto_id=self.pk).update(
            telefono_contacto=self.telefono, datos_contacto=datos_contacto_json)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self._sincronizar_agente_en_contacto()
        super(Contacto, self).save()

    def lista_de_datos(self):
        return json.loads(self.datos)

    def __str__(self):
        return '{0} >> {1}'.format(
            self.bd_contacto, self.datos)


class MensajeRecibidoManager(models.Manager):

    def mensaje_recibido_por_remitente(self):
        return self.values('remitente').annotate(Max('timestamp'))

    def mensaje_remitente_fecha(self, remitente, timestamp):
        try:
            return self.get(remitente=remitente, timestamp=timestamp)
        except MensajeRecibido.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro mensaje recibido con esa"
                                         " fecha y remitente")))


class MensajeRecibido(models.Model):
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = MensajeRecibidoManager()
    remitente = models.CharField(max_length=20)
    destinatario = models.CharField(max_length=20)
    timestamp = models.CharField(max_length=255)
    timezone = models.IntegerField()
    encoding = models.IntegerField()
    content = models.TextField()
    es_leido = models.BooleanField(default=False)

    def __str__(self):
        return "mensaje recibido del numero {0}".format(self.remitente)

    class Meta:
        db_table = 'mensaje_recibido'


class MensajeEnviado(models.Model):
    remitente = models.CharField(max_length=20)
    destinatario = models.CharField(max_length=20)
    timestamp = models.CharField(max_length=255)
    agente = models.ForeignKey(AgenteProfile, on_delete=models.CASCADE)
    content = models.TextField()
    result = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "mensaje enviado al número {0}".format(self.destinatario)

    class Meta:
        db_table = 'mensaje_enviado'


class GrabacionManager(models.Manager):

    def grabacion_by_fecha(self, fecha):
        try:
            return self.filter(fecha=fecha)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con esa "
                                         "fecha")))

    def grabacion_by_fecha_intervalo(self, fecha_inicio, fecha_fin):
        fecha_inicio = datetime_hora_minima_dia(fecha_inicio)
        fecha_fin = datetime_hora_maxima_dia(fecha_fin)
        try:
            return self.filter(fecha__range=(fecha_inicio, fecha_fin))
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con ese rango "
                                         "de fechas")))

    def grabacion_by_fecha_intervalo_campanas(self, fecha_inicio, fecha_fin, campanas):
        fecha_inicio = datetime_hora_minima_dia(fecha_inicio)
        fecha_fin = datetime_hora_maxima_dia(fecha_fin)
        try:
            return self.filter(fecha__range=(fecha_inicio, fecha_fin),
                               campana__in=campanas).order_by('-fecha')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con ese rango "
                                         "de fechas")))

    def grabacion_by_tipo_llamada(self, tipo_llamada):
        try:
            return self.filter(tipo_llamada=tipo_llamada)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con esa "
                                         "tipo llamada")))

    def grabacion_by_id_cliente(self, id_cliente):
        try:
            return self.filter(id_cliente__contains=id_cliente)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con esa "
                                         "id cliente")))

    def grabacion_by_tel_cliente(self, tel_cliente):
        try:
            return self.filter(tel_cliente__contains=tel_cliente)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro contactos con esa "
                                         "tel de cliente")))

    def grabacion_by_filtro(self, fecha_desde, fecha_hasta, tipo_llamada, tel_cliente, callid,
                            agente, campana, campanas, marcadas, duracion, gestion):
        grabaciones = self.filter(campana__in=campanas)

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
            grabaciones = grabaciones.filter(fecha__range=(fecha_desde,
                                                           fecha_hasta))
        if tipo_llamada:
            grabaciones = grabaciones.filter(tipo_llamada=tipo_llamada)
        if tel_cliente:
            grabaciones = grabaciones.filter(tel_cliente__contains=tel_cliente)
        if callid:
            grabaciones = grabaciones.filter(callid=callid)
        if agente:
            grabaciones = grabaciones.filter(agente=agente)
        if campana:
            grabaciones = grabaciones.filter(campana=campana)
        if duracion and duracion > 0:
            grabaciones = grabaciones.filter(duracion__gte=duracion)
        if marcadas:
            total_grabaciones_marcadas = Grabacion.objects.marcadas()
            grabaciones = grabaciones & total_grabaciones_marcadas
        if gestion:
            calificaciones_gestion_campanas = CalificacionCliente.obtener_califs_gestion_campanas(
                campanas)
            callids_calificaciones_gestion = list(calificaciones_gestion_campanas.values_list(
                'callid', flat=True))
            grabaciones = grabaciones.filter(callid__in=callids_calificaciones_gestion)

        return grabaciones.order_by('-fecha')

    def obtener_count_campana(self):
        try:
            return self.values('campana', 'campana__nombre').annotate(
                cantidad=Count('campana')).order_by('campana')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro grabaciones ")))

    def obtener_count_agente(self):
        try:
            return self.values('agente_id').annotate(
                cantidad=Count('agente_id')).order_by('agente_id')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro grabaciones ")))

    def marcadas(self):
        marcaciones = GrabacionMarca.objects.values_list('callid', flat=True)
        return self.filter(callid__in=marcaciones)


class Grabacion(models.Model):
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = GrabacionManager()
    TYPE_MANUAL = 1
    """Tipo de llamada manual"""

    TYPE_DIALER = 2
    """Tipo de llamada DIALER"""

    TYPE_INBOUND = 3
    """Tipo de llamada inbound"""

    TYPE_PREVIEW = 4
    """Tipo de llamada preview"""
    TYPE_LLAMADA_CHOICES = (
        (TYPE_DIALER, 'DIALER'),
        (TYPE_INBOUND, 'INBOUND'),
        (TYPE_MANUAL, 'MANUAL'),
        (TYPE_PREVIEW, 'PREVIEW'),
    )
    fecha = models.DateTimeField()
    tipo_llamada = models.PositiveIntegerField(choices=TYPE_LLAMADA_CHOICES)
    id_cliente = models.CharField(max_length=255)
    tel_cliente = models.CharField(max_length=255)
    grabacion = models.CharField(max_length=255)
    agente = models.ForeignKey(AgenteProfile, related_name='grabaciones', on_delete=models.CASCADE)
    campana = models.ForeignKey(Campana, related_name='grabaciones', on_delete=models.CASCADE)
    callid = models.CharField(max_length=45, blank=True, null=True)
    duracion = models.IntegerField(default=0)

    def __str__(self):
        return "grabacion del agente {0} con el cliente {1}".format(
            self.agente.user.get_full_name(), self.id_cliente)

    @property
    def url(self):
        hoy = fecha_local(now())
        dia_grabacion = fecha_local(self.fecha)
        filename = "/".join([settings.OML_GRABACIONES_URL,
                             dia_grabacion.strftime("%Y-%m-%d"),
                             self.grabacion])
        if dia_grabacion < hoy:
            return filename + '.' + settings.MONITORFORMAT
        else:
            return filename + '.wav'


class GrabacionMarca(models.Model):
    """
    Contiene los atributos de una grabación marcada
    """
    callid = models.CharField(max_length=45)
    descripcion = models.TextField()

    def __str__(self):
        return "Grabacion con uid={0} marcada con descripcion={1}".format(
            self.callid, self.descripcion)

    class Meta:
        db_table = 'ominicontacto_app_grabacion_marca'


class AgendaManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=fecha_local(now()))
        except Agenda.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro evenos en el dia de la "
                                         "fecha")))

    def eventos_filtro_fecha(self, fecha_desde, fecha_hasta):
        eventos = self.filter()
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
            eventos = eventos.filter(fecha__range=(fecha_desde, fecha_hasta))
        return eventos.order_by('-fecha')


class Agenda(models.Model):
    objects = AgendaManager()

    MEDIO_SMS = 1
    """Medio de comunicacion sms"""

    MEDIO_LLAMADA = 2
    """Medio de comunicacion llamada"""

    MEDIO_EMAIL = 3
    """Medio de comunicacion email"""

    MEDIO_COMUNICACION_CHOICES = (
        (MEDIO_SMS, 'SMS'),
        (MEDIO_LLAMADA, 'LLAMADA'),
        (MEDIO_EMAIL, 'EMAIL'),
    )
    agente = models.ForeignKey(AgenteProfile, blank=True, null=True,
                               related_name='eventos', on_delete=models.CASCADE)
    es_personal = models.BooleanField()
    fecha = models.DateField()
    hora = models.TimeField()
    es_smart = models.BooleanField()
    medio_comunicacion = models.PositiveIntegerField(
        choices=MEDIO_COMUNICACION_CHOICES)
    telefono = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    descripcion = models.TextField()

    def __str__(self):
        return "Evento programado para la fecha {0} a las {1} hs".format(
            self.fecha, self.hora)


class CalificacionClienteManager(models.Manager):

    def obtener_cantidad_calificacion_campana(self, campana):
        try:
            return self.values('calificacion').annotate(
                cantidad=Count('calificacion')).filter(
                    opcion_calificacion__campana=campana).order_by()
        except CalificacionCliente.DoesNotExist:
            raise (SuspiciousOperation(_("No se encontro calificaciones ")))

    def obtener_calificaciones_gestion(self):
        """
        Devuelve todas las calificaciones de tipo gestión
        """
        return self.filter(opcion_calificacion__tipo=OpcionCalificacion.GESTION)

    def obtener_calificaciones_auditadas(self):
        """
        Devuelve todas las calificaciones con auditoria asociada
        """
        return self.filter(auditoriacalificacion__isnull=False)

    def obtener_calificaciones_auditoria(self):
        """Devuelve un queryset con todas las calificaciones finales
        de gestion o que tengan una auditoria asociada
        """
        calificaciones_gestion = self.obtener_calificaciones_gestion()
        calificaciones_auditadas = self.obtener_calificaciones_auditadas()
        result = calificaciones_gestion | calificaciones_auditadas
        result = result.prefetch_related('auditoriacalificacion', 'contacto', 'agente')
        return result.order_by('-fecha')

    def calificacion_por_filtro(self, fecha_desde, fecha_hasta, agente, campana, grupo_agentes,
                                id_contacto, id_contacto_externo, telefono, callid,
                                status_auditoria):
        """Devuelve un queryset con la las calificaciones de acuerdo a los filtros aplicados"""

        calificaciones = self.obtener_calificaciones_auditoria()

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
            calificaciones = calificaciones.filter(modified__range=(fecha_desde,
                                                                    fecha_hasta))
        if agente:
            calificaciones = calificaciones.filter(agente=agente)
        if campana:
            calificaciones = calificaciones.filter(opcion_calificacion__campana=campana)
        if grupo_agentes and not agente:
            agentes_ids = list(AgenteProfile.objects.filter(grupo=grupo_agentes).values_list(
                'pk', flat=True))
            calificaciones = calificaciones.filter(agente__pk__in=agentes_ids)
        if id_contacto_externo:
            calificaciones = calificaciones.filter(contacto__id_externo=id_contacto_externo)
        if id_contacto:
            calificaciones = calificaciones.filter(contacto__pk=id_contacto)
        if telefono:
            calificaciones = calificaciones.filter(contacto__telefono__contains=telefono)
        if callid:
            calificaciones = calificaciones.filter(callid=callid)
        if status_auditoria:
            if AuditoriaCalificacion.es_pendiente(int(status_auditoria)):
                calificaciones = calificaciones.filter(
                    auditoriacalificacion__isnull=True)
            else:
                calificaciones = calificaciones.filter(
                    auditoriacalificacion__resultado=status_auditoria)

        return calificaciones


class CalificacionCliente(TimeStampedModel, models.Model):
    objects = CalificacionClienteManager()

    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE)
    opcion_calificacion = models.ForeignKey(
        OpcionCalificacion, blank=False, related_name='calificaciones_cliente',
        on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    agente = models.ForeignKey(AgenteProfile, related_name="calificaciones",
                               on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    agendado = models.BooleanField(default=False)
    callid = models.CharField(max_length=32, blank=True, null=True)

    # Campo agregado para diferenciar entre CalificacionCliente y CalificacionManual
    es_calificacion_manual = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return "Calificacion para la campana {0} para el contacto " \
               "{1} ".format(self.opcion_calificacion.campana, self.contacto)

    def _validar_unicidad_calificacion(self):
        # validamos que no exista otra calificación para este contacto en la
        # campaña
        msg_validation_error = _('Ya existe una calificación para este contacto en la campaña')
        campana = self.opcion_calificacion.campana
        contacto = self.contacto
        if self.pk is None and CalificacionCliente.objects.filter(
                contacto=contacto, opcion_calificacion__campana=campana).exists():
            raise ValidationError(msg_validation_error)
        if self.pk is not None:
            # verificamos que si se está modificando la calificación y se cambia
            # el valor de la campaña asociada o el contacto no resulte en dos
            # calificaciones para el mismo contacto en la misma campaña
            calificacion_bd = CalificacionCliente.objects.get(pk=self.pk)
            contacto_bd = calificacion_bd.contacto
            campana_bd = calificacion_bd.opcion_calificacion.campana
            if ((contacto_bd.pk != contacto.pk) or (campana_bd.pk != campana.pk)):
                if CalificacionCliente.objects.filter(
                        contacto=contacto, opcion_calificacion__campana=campana).exists():
                    raise ValidationError(msg_validation_error)

    def save(self, *args, **kwargs):
        self._validar_unicidad_calificacion()
        # gestionamos las agendas
        if self.opcion_calificacion.tipo != OpcionCalificacion.AGENDA:
            # eliminamos las agendas existentes (si hubiera alguna)
            AgendaContacto.objects.filter(
                agente=self.agente, contacto=self.contacto,
                campana=self.opcion_calificacion.campana,
                tipo_agenda=AgendaContacto.TYPE_PERSONAL).delete()
        super(CalificacionCliente, self).save(*args, **kwargs)

    def get_venta(self):
        return self.respuesta_formulario_gestion.first()

    def es_gestion(self):
        return self.opcion_calificacion.es_gestion()

    def es_agenda(self):
        # TODO: Usar metodo de OpcionCalificacion.es_agenda()
        # return self.opcion_calificacion.es_agenda()
        return self.opcion_calificacion.tipo == OpcionCalificacion.AGENDA

    def obtener_auditoria(self):
        """Devuelve el valor de la auditoria asociada o None si no tiene
        """
        try:
            auditoria = self.auditoriacalificacion
        except ObjectDoesNotExist:
            return None
        return auditoria

    def tiene_auditoria_pendiente(self):
        return self.obtener_auditoria() is None

    def tiene_auditoria_aprobada(self):
        return self.obtener_auditoria().resultado == AuditoriaCalificacion.APROBADA

    def tiene_auditoria_rechazada(self):
        return self.obtener_auditoria().resultado == AuditoriaCalificacion.RECHAZADA

    def tiene_auditoria_observada(self):
        return self.obtener_auditoria().resultado == AuditoriaCalificacion.OBSERVADA

    @classmethod
    def obtener_califs_gestion_campanas(cls, campanas):
        """Obtiene las calificaciones históricas de gestión de un conjunto de
        campañas en un rango de fechas definido
        """
        ids_campanas = list(campanas.values_list('pk', flat=True))
        calificaciones = cls.history.filter(
            opcion_calificacion__campana__pk__in=ids_campanas)
        calificaciones = calificaciones.filter(opcion_calificacion__tipo=OpcionCalificacion.GESTION)
        return calificaciones


class RespuestaFormularioGestion(models.Model):
    """Representa información del formulario de gestión completado en una Calificacion"""
    calificacion = models.ForeignKey(CalificacionCliente,
                                     related_name='respuesta_formulario_gestion',
                                     on_delete=models.CASCADE)
    metadata = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Respuesta del Formulario para el contacto {0} de la campana{1} " \
               "{1} ".format(self.calificacion.contacto,
                             self.calificacion.opcion_calificacion.campana)


class AuditoriaCalificacion(models.Model):
    """Representa el resultado de la auditoría que realiza un auditor (o backofficer)
    de un departamento
    de backoffice sobre la calificacion de un agente sobre un contacto
    """

    # el auditor aprueba la calificacion
    APROBADA = 0

    # el auditor aprueba la calificacion
    RECHAZADA = 1

    # el auditor realiza algunas observaciones al agente
    OBSERVADA = 2

    RESULTADO_CHOICES = (
        (APROBADA, _('Aprobada')),
        (RECHAZADA, _('Rechazada')),
        (OBSERVADA, _('Observada')),
    )

    calificacion = models.OneToOneField(CalificacionCliente, on_delete=models.CASCADE)
    resultado = models.IntegerField(choices=RESULTADO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)

    @classmethod
    def es_pendiente(cls, valor_resultado):
        "Determina si un valor corresponde a una auditoria aun pendiente"
        return valor_resultado not in [cls.APROBADA, cls.RECHAZADA, cls.OBSERVADA]

    @property
    def es_aprobada(self):
        return self.resultado == self.APROBADA

    @property
    def es_rechazada(self):
        return self.resultado == self.RECHAZADA

    @property
    def es_observada(self):
        return self.resultado == self.OBSERVADA

    def __str__(self):
        return str(_("Auditoría de calificacion con id={0} fue {1}".format(
            self.calificacion.pk, self.get_resultado_display())))


class Chat(models.Model):
    agente = models.ForeignKey(AgenteProfile, related_name="chatsagente", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chatsusuario", on_delete=models.CASCADE)
    fecha_hora_chat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Chat entre el agente {0} y el usuario {1} " \
               "{1} ".format(self.agente, self.user)


class MensajeChat(models.Model):
    sender = models.ForeignKey(User, related_name="chatssender", on_delete=models.CASCADE)
    to = models.ForeignKey(User, related_name="chatsto", on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_hora = models.DateTimeField(auto_now=True)
    chat = models.ForeignKey(Chat, related_name="mensajeschat", on_delete=models.CASCADE)


class AgendaContactoManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=fecha_local(now()))
        except AgendaContacto.DoesNotExist:
            raise SuspiciousOperation(_("No se encontraron eventos en el dia de la "
                                        "fecha"))

    def eventos_filtro_fecha(self, fecha_desde, fecha_hasta):
        eventos = self.filter(tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)
            eventos = eventos.filter(fecha__range=(fecha_desde, fecha_hasta))
        else:
            hoy = fecha_local(now())
            eventos = eventos.filter(fecha__gte=hoy)
        return eventos.order_by('-fecha')


class AgendaContacto(models.Model):
    objects = AgendaContactoManager()

    TYPE_PERSONAL = 1
    """Tipo de agenda Personal"""

    TYPE_GLOBAL = 2
    """Tipo de agenda Global"""

    TYPE_AGENDA_CHOICES = (
        (TYPE_PERSONAL, 'PERSONAL'),
        (TYPE_GLOBAL, 'GLOBAL'),
    )

    agente = models.ForeignKey(AgenteProfile, related_name="agendacontacto",
                               on_delete=models.CASCADE)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    tipo_agenda = models.PositiveIntegerField(choices=TYPE_AGENDA_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    campana = models.ForeignKey(Campana, related_name='agendas', null=True,
                                on_delete=models.CASCADE)

    def __str__(self):
        return "Agenda para el contacto {0} agendado por el agente {1} " \
               "para la fecha {2} a la hora {3}hs ".format(
                   self.contacto, self.agente, self.fecha, self.hora)


# ==============================================================================
# Actuaciones
# ==============================================================================


class AbstractActuacion(models.Model):
    """
    Modelo abstracto para las actuaciones de las campanas
    de audio y sms.
    """

    """Dias de la semana, compatibles con datetime.date.weekday()"""
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6

    DIA_SEMANAL_CHOICES = (
        (LUNES, 'LUNES'),
        (MARTES, 'MARTES'),
        (MIERCOLES, 'MIERCOLES'),
        (JUEVES, 'JUEVES'),
        (VIERNES, 'VIERNES'),
        (SABADO, 'SABADO'),
        (DOMINGO, 'DOMINGO'),
    )
    dia_semanal = models.PositiveIntegerField(
        choices=DIA_SEMANAL_CHOICES,
    )

    hora_desde = models.TimeField()
    hora_hasta = models.TimeField()

    class Meta:
        abstract = True

    def verifica_actuacion(self, hoy_ahora):
        """
        Este método verifica que el día de la semana y la hora
        pasada en el parámetro hoy_ahora sea válida para la
        actuación actual.
        Devuelve True o False.
        """

        assert isinstance(hoy_ahora, datetime.datetime)

        dia_semanal = hoy_ahora.weekday()
        hora_actual = datetime.time(
            hoy_ahora.hour, hoy_ahora.minute, hoy_ahora.second)

        if not self.dia_semanal == dia_semanal:
            return False

        if not self.hora_desde <= hora_actual <= self.hora_hasta:
            return False

        return True

    def dia_concuerda(self, fecha_a_chequear):
        """Este método evalua si el dia de la actuacion actual `self`
        concuerda con el dia de la semana de la fecha pasada por parametro.

        :param fecha_a_chequear: fecha a chequear
        :type fecha_a_chequear: `datetime.date`
        :returns: bool - True si la actuacion es para el mismo dia de
                  la semana que el dia de la semana de `fecha_a_chequear`
        """
        # NO quiero que funcione con `datatime` ni ninguna otra
        #  subclase, más que específicamente `datetime.date`,
        #  por eso no uso `isinstance()`.
        assert type(fecha_a_chequear) == datetime.date

        return self.dia_semanal == fecha_a_chequear.weekday()

    def es_anterior_a(self, time_a_chequear):
        """Este método evalua si el rango de tiempo de la actuacion
        actual `self` es anterior a la hora pasada por parametro.
        Verifica que sea 'estrictamente' anterior, o sea, ambas horas
        de la Actuacion deben ser anteriores a la hora a chequear
        para que devuelva True.

        :param time_a_chequear: hora a chequear
        :type time_a_chequear: `datetime.time`
        :returns: bool - True si ambas horas de la actuacion son anteriores
                  a la hora pasada por parametro `time_a_chequear`.
        """
        # NO quiero que funcione con ninguna subclase, más que
        #  específicamente `datetime.time`, por eso no uso `isinstance()`.
        assert type(time_a_chequear) == datetime.time

        # Es algo redundante chequear ambos, pero bueno...
        return self.hora_desde < time_a_chequear and \
            self.hora_hasta < time_a_chequear

    def clean(self):
        """
        Valida que al crear una actuación a una campaña
        no exista ya una actuación en el rango horario
        especificado y en el día semanal seleccionado.
        """
        if self.hora_desde and self.hora_hasta:
            if self.hora_desde >= self.hora_hasta:
                raise ValidationError({
                    'hora_desde': [_("La hora 'desde' debe ser menor o igual a la hora 'hasta'.")],
                    'hora_hasta': [_("La hora 'hasta' debe ser mayor a la hora 'desde'.")],
                })

            conflicto = self.get_campana().actuacionesdialer.filter(
                dia_semanal=self.dia_semanal,
                hora_desde__lte=self.hora_hasta,
                hora_hasta__gte=self.hora_desde,
            )
            if any(conflicto):
                raise ValidationError({
                    'hora_desde': [_("Ya esta cubierto el rango horario en ese día semanal.")],
                    'hora_hasta': [_("Ya esta cubierto el rango horario ese día semanal.")],
                })


class ActuacionVigente(models.Model):
    """
    Modelo  para las actuaciones de las campanas

    """

    """Dias de la semana, compatibles con datetime.date.weekday()"""

    campana = models.OneToOneField(Campana, on_delete=models.CASCADE)
    domingo = models.BooleanField()
    lunes = models.BooleanField()
    martes = models.BooleanField()
    miercoles = models.BooleanField()
    jueves = models.BooleanField()
    viernes = models.BooleanField()
    sabado = models.BooleanField()
    hora_desde = models.TimeField()
    hora_hasta = models.TimeField()

    def __str__(self):
        return "Campaña {0} - Actuación vigente: hora dese {1} a horas hasta {2}".format(
            self.campana, self.hora_desde, self.hora_hasta
        )

    def get_dias_vigente_wombat(self):
        dias = ""
        if self.domingo:
            dias += "1"
        if self.lunes:
            dias += "2"
        if self.martes:
            dias += "3"
        if self.miercoles:
            dias += "4"
        if self.jueves:
            dias += "5"
        if self.viernes:
            dias += "6"
        if self.sabado:
            dias += "7"
        return dias

    def get_hora_desde_wombat(self):
        return "{0}00".format(self.hora_desde.strftime("%H%M"))

    def get_hora_hasta_wombat(self):
        return "{0}00".format(self.hora_hasta.strftime("%H%M"))

    def get_dias_vigente_display(self):
        dias = ""
        if self.domingo:
            dias += "Domingo,"
        if self.lunes:
            dias += "Lunes,"
        if self.martes:
            dias += "Martes,"
        if self.miercoles:
            dias += "Miercoles,"
        if self.jueves:
            dias += "Jueves,"
        if self.viernes:
            dias += "Vienes,"
        if self.sabado:
            dias += "Sabado"
        return dias


class Backlist(models.Model):

    nombre = models.CharField(
        max_length=128, verbose_name=_('Nombre')
    )
    fecha_alta = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Fecha alta')
    )
    archivo_importacion = models.FileField(
        upload_to=upload_to,
        max_length=256,
        verbose_name=_('Archivo de importación')
    )
    nombre_archivo_importacion = models.CharField(
        max_length=256, verbose_name=_('Nombre Archivo de importación')
    )

    sin_definir = models.BooleanField(
        default=True,
    )
    cantidad_contactos = models.PositiveIntegerField(
        default=0)

    def __str__(self):
        return "{0}: ({1} contactos)".format(self.nombre,
                                             self.cantidad_contactos)


class ContactoBacklist(models.Model):
    """
    Lista de contacto que no quieren que los llamen
    """

    telefono = models.CharField(max_length=128)
    back_list = models.ForeignKey(
        Backlist, related_name='contactosbacklist', blank=True, null=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return "Telefono no llame {0}  ".format(self.telefono)


class SitioExterno(models.Model):
    """
    sitio externo para embeber en el agente
    """
    BOTON = 1
    AUTOMATICO = 2
    SERVER = 3

    DISPARADORES = (
        (BOTON, _('Agente')),
        (AUTOMATICO, _('Automático')),
        (SERVER, _('Servidor')),
    )

    GET = 1
    POST = 2

    METODOS = (
        (GET, _('GET')),
        (POST, _('POST')),
    )

    MULTIPART = 1
    WWW_FORM = 2
    TEXT_PLAIN = 3
    JSON = 4

    FORMATOS = (
        (MULTIPART, 'multipart/form-data'),
        (WWW_FORM, 'application/x-www-form-urlencoded'),
        (TEXT_PLAIN, 'text/plain'),
        (JSON, 'application/json'),
    )

    EMBEBIDO = 1
    NUEVA_PESTANA = 2

    OBJETIVOS = (
        (EMBEBIDO, _('Embebido')),
        (NUEVA_PESTANA, _('Nueva pestaña')),
    )

    nombre = models.CharField(max_length=128)
    url = models.CharField(max_length=256)
    oculto = models.BooleanField(default=False)
    disparador = models.PositiveIntegerField(choices=DISPARADORES, default=SERVER)
    metodo = models.PositiveIntegerField(choices=METODOS, default=GET)
    formato = models.PositiveIntegerField(choices=FORMATOS, default=MULTIPART,
                                          blank=True, null=True,
                                          verbose_name='Content-Type')
    objetivo = models.PositiveIntegerField(choices=OBJETIVOS, default=EMBEBIDO,
                                           blank=True, null=True)

    def __str__(self):
        return "Sitio: {0} - url: {1}".format(self.nombre, self.url)

    def ocultar(self):
        """setea la campana como oculta"""
        self.oculto = True
        self.save()

    def desocultar(self):
        """setea la campana como visible"""
        self.oculto = False
        self.save()

    def get_parametros(self, agente, campana, contacto, datos_de_llamada):
        parametros = {}
        for parametro in campana.parametros_crm.all():
            if not parametro.es_placeholder():
                valor = parametro.obtener_valor(agente, contacto, datos_de_llamada)
                parametros[parametro.nombre] = str(valor)
        return parametros

    def get_url_interaccion(self, agente, campana, contacto, datos_de_llamada, completa=False):
        # Beauty
        # Tomar parametros de tipo placeholder y reemplazarlos en la url
        url = self.url
        valores = {}
        for parametro in campana.parametros_crm.all():
            valor = str(parametro.obtener_valor(agente, contacto, datos_de_llamada))
            if parametro.es_placeholder():
                url = url.replace(parametro.nombre, valor)
            else:
                valores[parametro.nombre] = valor

        valores = '&'.join([key + '=' + val for (key, val) in valores.items()])
        if completa and valores:
            return url + '?' + valores
        else:
            return url

    def get_configuracion_de_interaccion(self, agente, campana, contacto, datos_de_llamada):
        return {
            'dispara_agente': self.disparador == self.BOTON,
            'formato': self.get_formato_display(),
            'formato_es_JSON': self.formato == self.JSON,
            'url': self.get_url_interaccion(agente, campana, contacto, datos_de_llamada),
            'abre_pestana': self.objetivo == self.NUEVA_PESTANA,
            'metodo': 'GET' if self.metodo == self.GET else 'POST',
            'parametros': self.get_parametros(agente, campana, contacto, datos_de_llamada),
        }


class SistemaExterno(models.Model):
    """Representa un sistema externo que se comunica con OML a través de sus CRMs
    y la API de OML
    """
    nombre = models.CharField(unique=True, max_length=128)
    agentes = models.ManyToManyField(
        AgenteProfile, through="AgenteEnSistemaExterno", verbose_name=_("Agentes"))

    def __str__(self):
        return "Sistema Externo: {0}".format(self.nombre)


class AgenteEnSistemaExterno(models.Model):
    """Representa la relación entre un agente de OML y un sistema externo"""
    agente = models.ForeignKey(AgenteProfile, on_delete=models.CASCADE)
    sistema_externo = models.ForeignKey(SistemaExterno, on_delete=models.CASCADE)
    id_externo_agente = models.CharField(max_length=128)

    def __str__(self):
        return "Agente: {0} en Sistema Externo: {1} con id_externo: {2}".format(
            self.agente, self.sistema_externo, self.id_externo_agente)

    class Meta:
        unique_together = (('sistema_externo', 'id_externo_agente'),
                           ('sistema_externo', 'agente'))


class ReglasIncidencia(models.Model):
    """
    Reglas de llamada de wombat para las campañas dialer
    """

    RS_BUSY = 1
    "Regla de llamado para ocupado"

    TERMINATED = 2
    "Regla para llamada terminado"

    RS_NOANSWER = 3
    "Regla para llamada no atendida"

    RS_REJECTED = 4
    "Regla para llamada rechazada"

    RS_TIMEOUT = 5
    "Regla para timeout"

    ESTADOS_CHOICES = (
        (RS_BUSY, _("Ocupado")),
        (TERMINATED, _("Contestador")),
        (RS_NOANSWER, _("No atendido")),
        (RS_REJECTED, _("Rechazado")),
        (RS_TIMEOUT, _("Timeout"))
    )

    ESTADO_PERSONALIZADO_CONTESTADOR = _('CONTESTADOR')

    FIXED = 1

    MULT = 2

    EN_MODO_CHOICES = (
        (FIXED, "FIXED"),
        (MULT, "MULT")
    )

    campana = models.ForeignKey(Campana, related_name='reglas_incidencia', on_delete=models.CASCADE)
    estado = models.PositiveIntegerField(choices=ESTADOS_CHOICES)
    estado_personalizado = models.CharField(max_length=128, blank=True, null=True)
    intento_max = models.IntegerField()
    reintentar_tarde = models.IntegerField()
    en_modo = models.PositiveIntegerField(choices=EN_MODO_CHOICES, default=MULT)

    def __str__(self):
        return "Regla de incidencia para la campana: {0} - estado: {1}".format(
            self.campana.nombre, self.estado)

    def get_estado_wombat(self):
        if self.estado is ReglasIncidencia.RS_BUSY:
            return "RS_BUSY"
        elif self.estado is ReglasIncidencia.TERMINATED:
            return "TERMINATED"
        elif self.estado is ReglasIncidencia.RS_NOANSWER:
            return "RS_NOANSWER"
        elif self.estado is ReglasIncidencia.RS_REJECTED:
            return "RS_REJECTED"
        elif self.estado is ReglasIncidencia.RS_TIMEOUT:
            return "RS_TIMEOUT"
        else:
            return ""

    def get_en_modo_wombat(self):
        if self.en_modo is ReglasIncidencia.FIXED:
            return "FIXED"
        elif self.en_modo is ReglasIncidencia.MULT:
            return "MULT"
        else:
            return ""


class AgenteEnContactoManager(models.Manager):

    def contacto_asignado(self, agente_id, campana_id):
        # Devuelve el contacto asignado a un agente en una campaña
        return self.filter(
            estado__in=[AgenteEnContacto.ESTADO_ENTREGADO, AgenteEnContacto.ESTADO_ASIGNADO],
            agente_id=agente_id,
            campana_id=campana_id)

    def esta_asignado_o_entregado_a_agente(self, contacto_id, campana_id, agente_id):
        # Devuelve si el agente tiene ese contacto asignado o entregado
        return self.contacto_asignado(agente_id, campana_id).filter(
            contacto_id=contacto_id).exists()

    def activos(self, campana_id):
        # Devuelve los que estan activos de acuerdo al campo de desactivacion definido en la
        # campaña
        campana = Campana.objects.get(pk=campana_id)
        campo_desactivacion = campana.campo_desactivacion
        desactivacion_booleana = {campo_desactivacion: "FALSE"}
        desactivacion_numerica = {campo_desactivacion: "0"}
        # deberiamos tener algo como "desactivado: FALSE" o  "desactivado: 0", sin llaves
        desactivacion_booleana_str = json.dumps(desactivacion_booleana)[1:-1]
        desactivacion_numerica_str = json.dumps(desactivacion_numerica)[1:-1]
        return self.filter(campana_id=campana_id).exclude(
            Q(datos_contacto__contains=desactivacion_booleana_str) |
            Q(datos_contacto__contains=desactivacion_numerica_str))


class AgenteEnContacto(models.Model):
    """
    Relaciona a agentes que están en comunicación con contactos de la BD de una campaña
    """
    objects = AgenteEnContactoManager()

    ESTADO_INICIAL = 0  # significa que el contacto aún no ha sido entregado a ningún agente

    ESTADO_ENTREGADO = 1  # significa que un agente solicitó este contacto y le fue entregado

    ESTADO_ASIGNADO = 3  # El agente esta en proceso de contactación, se lo reserva por X tiempo

    ESTADO_FINALIZADO = 2  # significa que el agente culminó de forma satisfactoria la llamada

    ESTADO_CHOICES = (
        (ESTADO_INICIAL, 'INICIAL'),
        (ESTADO_ENTREGADO, 'ENTREGADO'),
        (ESTADO_ASIGNADO, 'ASIGNADO'),
        (ESTADO_FINALIZADO, 'FINALIZADO'),
    )
    agente_id = models.IntegerField()
    contacto_id = models.IntegerField()
    datos_contacto = models.TextField()
    telefono_contacto = models.CharField(max_length=128)
    campana_id = models.IntegerField()
    estado = models.PositiveIntegerField(choices=ESTADO_CHOICES)
    modificado = models.DateTimeField(auto_now=True, null=True)
    es_originario = models.BooleanField(default=True)
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return "Agente de id={0} relacionado con contacto de id={1} con el estado {2}".format(
            self.agente_id, self.contacto_id, self.estado)

    @classmethod
    def asignar_contacto(cls, contacto_id, campana_id, agente):
        try:
            agente_en_contacto = cls.objects.get(agente_id=agente.id, campana_id=campana_id,
                                                 contacto_id=contacto_id,
                                                 estado__in=[AgenteEnContacto.ESTADO_ENTREGADO,
                                                             AgenteEnContacto.ESTADO_ASIGNADO])
        except AgenteEnContacto.DoesNotExist:
            return False  # No se pudo asignar

        agente_en_contacto.estado = AgenteEnContacto.ESTADO_ASIGNADO
        agente_en_contacto.save()
        return True

    @classmethod
    def entregar_contacto(cls, agente, campana_id):
        # Si ya tiene un contacto ASIGNADO solo puede llamar a ese.
        contacto_asignado = AgenteEnContacto.objects.filter(agente_id=agente.id,
                                                            estado=AgenteEnContacto.ESTADO_ASIGNADO,
                                                            campana_id=campana_id)
        if contacto_asignado.exists():
            agente_en_contacto = contacto_asignado[0]
            data = model_to_dict(agente_en_contacto)
            data['datos_contacto'] = literal_eval(data['datos_contacto'])
            data['result'] = 'OK'
            data['code'] = 'contacto-asignado'
            return data

        # Si no tiene un contacto asignado, asignarle otro

        # Si el agente tiene algún contacto entregado previamente se libera para
        # que pueda ser entregado a otros agentes de la campaña
        __, orden = cls.liberar_contacto(agente.id, campana_id)

        # obtiene el orden de la ultimo asignacion entregada al agente
        # (-1 si no tenía ninguno asignado y le asigna consecutivamente
        # a partir los numeros de orden superiores o iguales a este
        numero_agentes_contacto = AgenteEnContacto.objects.filter(campana_id=campana_id).count()
        orden = (orden + 1) % (numero_agentes_contacto + 1)

        try:
            qs_agentes_contactos_no_orden = cls.objects.activos(
                campana_id=campana_id).filter(
                    agente_id__in=[-1, agente.pk], estado=AgenteEnContacto.ESTADO_INICIAL,
                    campana_id=campana_id)
            qs_agentes_contactos = qs_agentes_contactos_no_orden.filter(orden__gte=orden)
            qs_agentes_contactos = qs_agentes_contactos.select_for_update()
        except DatabaseError:
            return {'result': 'Error',
                    'code': 'error-concurrencia',
                    'data': 'Contacto siendo accedido por más de un agente'}

        if qs_agentes_contactos.exists():
            # encuentra y devuelve el contacto a asignar al
            # de acuerdo al orden definido en el atributo 'orden'
            # desde la lista de los contactos disponibles para el agente
            agente_en_contacto = qs_agentes_contactos.first()
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_ENTREGADO
            agente_en_contacto.agente_id = agente.id
            agente_en_contacto.save()
            data = model_to_dict(agente_en_contacto)
            data['datos_contacto'] = literal_eval(data['datos_contacto'])
            data['result'] = 'OK'
            data['code'] = 'contacto-entregado'
            return data
        elif qs_agentes_contactos_no_orden.select_for_update().exists():
            # significa que no se encontro contacto porque se llego al final del
            # orden, asi que tomamos el primero recibido sin tener en cuenta el orden
            # en el filtro ()
            agente_en_contacto = qs_agentes_contactos_no_orden.first()
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_ENTREGADO
            agente_en_contacto.agente_id = agente.id
            agente_en_contacto.save()
            data = model_to_dict(agente_en_contacto)
            data['datos_contacto'] = literal_eval(data['datos_contacto'])
            data['result'] = 'OK'
            data['code'] = 'contacto-entregado'
            return data
        else:
            return {'result': 'Error',
                    'code': 'error-no-contactos',
                    'data': 'No hay contactos para asignar en esta campaña'}

    @classmethod
    def liberar_contacto(cls, agente_id, campana_id):
        qs_agente_en_contacto = cls.objects.contacto_asignado(agente_id, campana_id)
        if qs_agente_en_contacto.exists():
            agente_en_contacto = qs_agente_en_contacto.first()
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_INICIAL
            agente_en_contacto.agente_id = -1
            agente_en_contacto.save()
            return True, agente_en_contacto.orden
        return False, -1

    @classmethod
    def liberar_contactos_por_tiempo(cls):

        # obtenemos las campañas preview activas y almacenamos en un dict su
        # tiempo de reserva
        campanas_preview_dict = {}
        campanas_preview_activas = Campana.objects.obtener_campanas_preview().filter(
            estado=Campana.ESTADO_ACTIVA)

        tiempo_actual = now()
        for campana_preview in campanas_preview_activas:
            campanas_preview_dict[campana_preview.pk] = campana_preview.tiempo_desconexion

        agente_en_contacto_ids = []
        for agente_en_contacto in AgenteEnContacto.objects.filter(
                estado__in=[AgenteEnContacto.ESTADO_ENTREGADO, AgenteEnContacto.ESTADO_ASIGNADO]):
            campana_id = agente_en_contacto.campana_id
            tiempo_de_reserva = campanas_preview_dict[campana_id]
            delta_tiempo_desconexion = timedelta(minutes=tiempo_de_reserva)
            hora_limite_reserva = tiempo_actual - delta_tiempo_desconexion
            ultima_modificacion = agente_en_contacto.modificado
            delta_tiempo_asignacion = timedelta(
                minutes=settings.DURACION_ASIGNACION_CONTACTO_PREVIEW)
            hora_limite_asignacion = tiempo_actual - delta_tiempo_asignacion
            if ultima_modificacion <= hora_limite_reserva or \
               ultima_modificacion <= hora_limite_asignacion:
                agente_en_contacto_ids.append(agente_en_contacto.pk)
        liberados = AgenteEnContacto.objects.filter(pk__in=agente_en_contacto_ids).update(
            agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)
        return liberados.count()

    @classmethod
    def ultimo_id(cls):
        ultimo = AgenteEnContacto.objects.last()
        if ultimo:
            return ultimo.id
        return 0


class ParametrosCrm(models.Model):
    """
    Variables a enviar en la url del crm de sitio externo
    """
    DATO_CAMPANA = 1
    DATO_CONTACTO = 2
    DATO_LLAMADA = 3
    CUSTOM = 4

    TIPOS = (
        (DATO_CAMPANA, _('Dato de Campaña')),
        (DATO_CONTACTO, _('Dato de Contacto')),
        (DATO_LLAMADA, _('Dato de Llamada')),
        (CUSTOM, _('Fijo')),
    )

    OPCIONES_CAMPANA = (
        ('id', _('ID de Campaña')),
        ('nombre', _('Nombre')),
        ('tipo', _('Tipo de Campaña')),
    )
    OPCIONES_CAMPANA_KEYS = [key for key, value in OPCIONES_CAMPANA]

    OPCIONES_LLAMADA = (
        ('call_id', _('ID de Llamada')),
        ('agent_id', _('ID de Agente')),
        ('telefono', _('Teléfono')),
        ('id_contacto', _('ID de Cliente')),
        ('rec_filename', _('Archivo de Grabación')),
        ('call_wait_duration', _('Tiempo de espera')),
    )
    OPCIONES_LLAMADA_KEYS = [key for key, value in OPCIONES_LLAMADA]

    campana = models.ForeignKey(Campana, related_name='parametros_crm', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=128)
    valor = models.CharField(max_length=256)
    tipo = models.PositiveIntegerField(choices=TIPOS)

    def __str__(self):
        return "Variable {0} con valor: {1} para la campana {2}".format(
            self.nombre, self.valor, self.campana)

    def es_placeholder(self):
        return self.nombre[0] == '{' and self.nombre[-1] == '}' and self.nombre[1:-1].isdigit()

    def obtener_valor(self, agente, contacto, datos_de_llamada):
        if self.tipo == ParametrosCrm.DATO_CAMPANA:
            return self.obtener_valor_de_campana()
        if self.tipo == ParametrosCrm.DATO_CONTACTO:
            return self.obtener_valor_de_contacto(contacto)
        if self.tipo == ParametrosCrm.DATO_LLAMADA:
            return self.obtener_valor_de_llamada(agente, datos_de_llamada)
        if self.tipo == ParametrosCrm.CUSTOM:
            return self.valor

    def obtener_valor_de_campana(self):
        if self.valor == 'tipo':
            return self.campana.get_type_display()
        return getattr(self.campana, self.valor)

    def obtener_valor_de_contacto(self, contacto):
        if contacto is None:
            return ''
        datos_contacto = contacto.obtener_datos()
        return datos_contacto[self.valor]

    def obtener_valor_de_llamada(self, agente, datos_de_llamada):
        if self.valor == 'agent_id':
            return agente.id
        return datos_de_llamada[self.valor]
