# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import getpass
import json
import logging
import os
import re
import sys
import uuid

from ast import literal_eval

from crontab import CronTab

from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.db import models, connection
from django.db.models import Max, Q, Count
from django.conf import settings
from django.core.exceptions import ValidationError, SuspiciousOperation

from ominicontacto_app.utiles import ValidadorDeNombreDeCampoExtra, datetime_hora_minima_dia, \
    datetime_hora_maxima_dia

logger = logging.getLogger(__name__)

SUBSITUTE_REGEX = re.compile(r'[^a-z\._-]')


class User(AbstractUser):
    is_agente = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    last_session_key = models.CharField(blank=True, null=True, max_length=40)

    def get_agente_profile(self):
        agente_profile = None
        if hasattr(self, 'agenteprofile'):
            agente_profile = self.agenteprofile
        return agente_profile

    def get_supervisor_profile(self):
        supervisor_profile = None
        if hasattr(self, 'supervisorprofile'):
            supervisor_profile = self.supervisorprofile
        return supervisor_profile

    def get_is_administrador(self):
        supervisor = self.get_supervisor_profile()
        if supervisor and supervisor.is_administrador:
            return True
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

    def get_tiene_permiso_administracion(self):
        """Funcion devuelve true si tiene permiso de acceso a la pagina
        de adminstracion del sistema"""
        if self.get_is_administrador():
            return True
        elif self.get_is_supervisor_normal():
            return True
        elif self.get_is_supervisor_customer():
            return True
        return False

    def set_session_key(self, key):
        if self.last_session_key and not self.last_session_key == key:
            try:
                Session.objects.get(session_key=self.last_session_key).delete()
            except Session.DoesNotExist:
                logger.exception("Excepcion detectada al obtener session "
                                 "con el key {0} no existe ".format(self.last_session_key))

        self.last_session_key = key
        self.save()

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
    auto_attend_ics = models.BooleanField(default=False)
    auto_attend_inbound = models.BooleanField(default=False)
    auto_attend_dialer = models.BooleanField(default=False)
    auto_pause = models.BooleanField(default=False)
    auto_unpause = models.PositiveIntegerField()

    def __unicode__(self):
        return self.nombre


class AgenteProfileManager(models.Manager):

    def obtener_agente_por_sip(self, sip_agente):

        try:
            return self.get(sip_extension=sip_agente)
        except AgenteProfile.DoesNotExist:
            logger.exception("Excepcion detectada al obtener_agente_por_sip "
                             "con el sip {0} no existe ".format(sip_agente))
            return None


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
    modulos = models.ManyToManyField(Modulo)
    grupo = models.ForeignKey(Grupo, related_name='agentes')
    estado = models.PositiveIntegerField(choices=ESTADO_CHOICES, default=ESTADO_OFFLINE)
    reported_by = models.ForeignKey(User, related_name="reportedby")
    is_inactive = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.get_full_name()

    def get_modulos(self):
        return "\n".join([modulo.nombre for modulo in self.modulos.all()])

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

    def get_id_nombre_agente(self):
        return "{0}_{1}".format(self.id, self.user.get_full_name())

    def desactivar(self):
        self.is_inactive = True
        self.save()

    def activar(self):
        self.is_inactive = False
        self.save()


class SupervisorProfileManager(models.Manager):

    def obtener_ultimo_sip_extension(self):
        """
        Este metodo se encarga de devolver el siguinte sip_extension
        y si no existe supervisor e devuelve 3000
        """
        try:
            identificador = \
                self.latest('id').sip_extension + 1
        except SupervisorProfile.DoesNotExist:
            identificador = 3000

        return identificador


class SupervisorProfile(models.Model):
    objects = SupervisorProfileManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    sip_password = models.CharField(max_length=128, blank=True, null=True)
    is_administrador = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.get_full_name()
#
# class PhysiotherapistProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     active = models.BooleanField(default=True)
#     name = models.CharField(max_length=64)


class CalificacionManager(models.Manager):
    def usuarios(self):
        """
        Devuelve todas las calificaciones excepto la restringida de sistema
        para agenda
        """
        return self.exclude(nombre=settings.CALIFICACION_REAGENDA)


class Calificacion(models.Model):
    nombre = models.CharField(max_length=50)
    objects = CalificacionManager()

    def es_reservada(self):
        return self.nombre == settings.CALIFICACION_REAGENDA

    def __unicode__(self):
        return self.nombre


class CalificacionCampana(models.Model):
    """Clase Version
    Atributos: Calificacion, nombre. """
    nombre = models.CharField(max_length=50)
    calificacion = models.ManyToManyField(Calificacion)

    def __unicode__(self):
        return self.nombre


class Formulario(models.Model):
    nombre = models.CharField(max_length=64)
    descripcion = models.TextField()

    def __unicode__(self):
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
        (TIPO_TEXTO, 'Texto'),
        (TIPO_FECHA, 'Fecha'),
        (TIPO_LISTA, 'Lista'),
        (TIPO_TEXTO_AREA, 'Caja de Texto de Area'),
    )

    formulario = models.ForeignKey(Formulario, related_name="campos")
    nombre_campo = models.CharField(max_length=64)
    orden = models.PositiveIntegerField()
    tipo = models.PositiveIntegerField(choices=TIPO_CHOICES)
    values_select = models.TextField(blank=True, null=True)
    is_required = models.BooleanField()

    class Meta:
        ordering = ['orden']
        unique_together = ("orden", "formulario")

    def __unicode__(self):
        return "campo {0} del formulario {1}".format(self.nombre_campo,
                                                     self.formulario)

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
    return "audios_reproduccion/%Y/%m/{0}-{1}".format(
        str(uuid.uuid4()), filename)[:95]


def upload_to_audio_asterisk(instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    return "audios_asterisk/%Y/%m/{0}-{1}".format(
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

    descripcion = models.CharField(
        max_length=100,
    )
    audio_original = models.FileField(
        upload_to=upload_to_audio_original,
        max_length=100,
        null=True, blank=True,
    )
    audio_asterisk = models.FileField(
        upload_to=upload_to_audio_asterisk,
        max_length=100,
        null=True, blank=True,
    )
    borrado = models.BooleanField(
        default=False,
        editable=False,
    )

    def __unicode__(self):
        if self.borrado:
            return '(ELiminado) {0}'.format(self.descripcion)
        return self.descripcion

    def borrar(self):
        """
        Setea la ArchivoDeAudio como BORRADO.
        """
        logger.info("Seteando ArchivoDeAudio %s como BORRADO", self.id)

        self.borrado = True
        self.save()


class CampanaManager(models.Manager):

    def obtener_en_definicion_para_editar(self, campana_id):
        """Devuelve la campaña pasada por ID, siempre que dicha
        campaña pueda ser editar (editada en el proceso de
        definirla, o sea, en el proceso de "creacion" de la
        campaña).

        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.filter(
                estado=self.model.ESTADO_EN_DEFINICION).get(
                pk=campana_id)
        except self.model.DoesNotExist:
            raise(SuspiciousOperation("No se encontro campana %s en "
                                      "estado ESTADO_EN_DEFINICION"))

    def obtener_template_en_definicion_para_editar(self, campana_id):
        """Devuelve la campaña template pasada por ID, siempre que dicha
        campaña pueda ser editar (editada en el proceso de
        definirla, o sea, en el proceso de "creacion" de la
        campaña).

        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.filter(
                estado=self.model.ESTADO_TEMPLATE_EN_DEFINICION).get(
                pk=campana_id)
        except self.model.DoesNotExist:
            raise(SuspiciousOperation("No se encontro campana %s en "
                                      "estado ESTADO_TEMPLATE_EN_DEFINICION"))

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
        Devuelve campañas en estado pausadas.
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

    def obtener_all_activas_finalizadas(self):
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

    def obtener_campanas_vista_by_user(self, campanas, user):
        """
        devuelve las campanas filtradas por user
        :param campanas: queryset de campanas a filtrar
        :param user: usuario a filtrar
        :return: campanas filtradas por usuaro
        """
        return campanas.filter(Q(supervisors=user) | Q(reported_by=user))

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

    def crea_campana_de_template(self, template):
        """
        Este método se encarga de crear una campana a partir del template
        proporcionado.
        """
        assert template.estado == Campana.ESTADO_TEMPLATE_ACTIVO
        assert template.es_template

        campana = Campana.objects.replicar_campana(template)
        return campana

    def replicar_campana(self, campana):
        """
        Este método se encarga de replicar una campana existente, creando una
        campana nueva de iguales características.
        """
        assert isinstance(campana, Campana)

        ultimo_id = Campana.objects.obtener_ultimo_id_campana()

        # Replica Campana.
        campana_replicada = self.create(
            nombre="CAMPANA_CLONADA_{0}".format(ultimo_id + 1),
            fecha_inicio=campana.fecha_inicio,
            fecha_fin=campana.fecha_fin,
            bd_contacto=campana.bd_contacto,
            calificacion_campana=campana.calificacion_campana,
            gestion=campana.gestion,
            type=campana.type,
            formulario=campana.formulario,
            sitio_externo=campana.sitio_externo,
            tipo_interaccion=campana.tipo_interaccion,
            reported_by=campana.reported_by,
        )

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
            queue_asterisk=Queue.objects.ultimo_queue_asterisk(),
            auto_grabacion=campana.queue_campana.auto_grabacion,
            detectar_contestadores=campana.queue_campana.detectar_contestadores,

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
            queue_asterisk=Queue.objects.ultimo_queue_asterisk(),
            auto_grabacion=campana.queue_campana.auto_grabacion,
            detectar_contestadores=campana.queue_campana.detectar_contestadores,
        )
        # Eliminamos queuue de la campana asignada
        queue_a_eliminar = Queue.objects.get(campana=campana)
        queue_a_eliminar.delete()
        # guardarmos la nueva queue
        queue_replicada.save()


class Campana(models.Model):
    """Una campaña del call center"""

    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = CampanaManager()

    ESTADO_EN_DEFINICION = 1
    """La campaña esta siendo definida en el wizard"""

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

    ESTADO_TEMPLATE_EN_DEFINICION = 7
    """La campaña se creo como template y esta en proceso de definición."""

    ESTADO_TEMPLATE_ACTIVO = 8
    """La campaña se creo como template y esta activa, en condición de usarse
    como tal."""

    ESTADO_TEMPLATE_BORRADO = 9
    """La campaña se creo como template y esta borrada, ya no puede usarse
    como tal."""

    ESTADOS = (
        (ESTADO_EN_DEFINICION, 'En definicion'),
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_FINALIZADA, 'Finalizada'),
        (ESTADO_BORRADA, 'Borrada'),
        (ESTADO_PAUSADA, 'Pausada'),
        (ESTADO_INACTIVA, 'Inactiva'),

        (ESTADO_TEMPLATE_EN_DEFINICION, '(Template en definicion)'),
        (ESTADO_TEMPLATE_ACTIVO, 'Template Activo'),
        (ESTADO_TEMPLATE_BORRADO, 'Template Borrado'),
    )

    TYPE_ENTRANTE = 1
    TYPE_ENTRANTE_DISPLAY = 'Entrante'
    TYPE_DIALER = 2
    TYPE_DIALER_DISPLAY = 'Dialer'
    TYPE_MANUAL = 3
    TYPE_MANUAL_DISPLAY = 'Manual'
    TYPE_PREVIEW = 4
    TYPE_PREVIEW_DISPLAY = 'Preview'

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

    TIPO_INTERACCION = (
        (FORMULARIO, "Formulario"),
        (SITIO_EXTERNO, "Url externa")
    )

    TIEMPO_ACTUALIZACION_CONTACTOS = 1

    estado = models.PositiveIntegerField(
        choices=ESTADOS,
        default=ESTADO_EN_DEFINICION,
    )
    nombre = models.CharField(max_length=128, unique=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    calificacion_campana = models.ForeignKey(CalificacionCampana,
                                             related_name="calificacioncampana"
                                             )
    bd_contacto = models.ForeignKey(
        'BaseDatosContacto',
        null=True, blank=True,
        related_name="%(class)ss"
    )
    formulario = models.ForeignKey(Formulario, null=True, blank=True)
    oculto = models.BooleanField(default=False)
    gestion = models.CharField(max_length=128, default="Venta")
    campaign_id_wombat = models.IntegerField(null=True, blank=True)
    type = models.PositiveIntegerField(choices=TYPES_CAMPANA)
    sitio_externo = models.ForeignKey("SitioExterno", null=True, blank=True)
    tipo_interaccion = models.PositiveIntegerField(
        choices=TIPO_INTERACCION,
        default=FORMULARIO,
    )
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    supervisors = models.ManyToManyField(User, related_name="campanasupervisors")
    es_template = models.BooleanField(default=False)
    nombre_template = models.CharField(max_length=128, null=True, blank=True)
    es_manual = models.BooleanField(default=False)
    objetivo = models.PositiveIntegerField(default=0)
    tiempo_desconexion = models.PositiveIntegerField(default=0)  # para uso en campañas preview

    def __unicode__(self):
        return self.nombre

    def crear_tarea_actualizacion(self):
        """
        Adiciona una tarea que llama al procedimiento de actualización de cada
        asignación de agente a contacto para la campaña preview actual
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python')
        ruta_manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
        # adicionar nuevo cron job
        job = crontab.new(
            command='{0} {1} actualizar_campanas_preview {2} {3}'.format(
                ruta_python_virtualenv, ruta_manage_py, self.pk, self.tiempo_desconexion),
            comment=str(self.pk))
        # adicionar tiempo de periodicidad al cron job
        job.minute.every(self.TIEMPO_ACTUALIZACION_CONTACTOS)
        crontab.write_to_user(user=getpass.getuser())

    def eliminar_tarea_actualizacion(self):
        """
        Elimina la tarea que llama al procedimiento de actualización de cada
        asignación de agente a contacto para la campaña preview actual
        """
        crontab = CronTab(user=getpass.getuser())
        crontab.remove_all(comment=str(self.pk))
        crontab.write_to_user(user=getpass.getuser())

    def guardar_campaign_id_wombat(self, campaign_id_wombat):
        self.campaign_id_wombat = campaign_id_wombat
        self.save()

    def play(self):
        """Setea la campaña como ESTADO_ACTIVA"""
        logger.info("Seteando campana %s como ESTADO_ACTIVA", self.id)
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_ACTIVA
        self.save()

    def pausar(self):
        """Setea la campaña como ESTADO_PAUSADA"""
        logger.info("Seteando campana %s como ESTADO_PAUSADA", self.id)
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_PAUSADA
        self.save()

    def activar(self):
        """Setea la campaña como ESTADO_ACTIVA"""
        logger.info("Seteando campana %s como ESTADO_ACTIVA", self.id)
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_ACTIVA
        self.save()

    def remover(self):
        """Setea la campaña como ESTADO_BORRADA"""
        logger.info("Seteando campana %s como ESTADO_BORRADA", self.id)
        if self.type == Campana.TYPE_PREVIEW:
            # eliminamos el proceso que actualiza las conexiones de agentes a contactos
            # en la campaña
            self.eliminar_tarea_actualizacion()
            # eliminamos todos las entradas de AgenteEnContacto relativas a la campaña
            AgenteEnContacto.objects.filter(campana_id=self.pk).delete()
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_BORRADA
        self.save()

    def finalizar(self):
        """Setea la campaña como ESTADO_FINALIZADA"""
        logger.info("Seteando campana %s como ESTADO_FINALIZADA", self.id)
        # assert self.estado == Campana.ESTADO_ACTIVA
        self.estado = Campana.ESTADO_FINALIZADA
        if self.type == Campana.TYPE_PREVIEW:
            # eliminamos la planificación de actualización de relaciones de agentes con contactos
            # de la campaña
            self.eliminar_tarea_actualizacion()
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
        logger.info("Seteando campana-->template %s como BORRADA", self.id)
        assert self.estado == Campana.ESTADO_TEMPLATE_ACTIVO

        self.estado = Campana.ESTADO_TEMPLATE_BORRADO
        self.save()

    def _obtener_campos_bd_contacto(self, contacto):
        base_datos = self.bd_contacto
        metadata = base_datos.get_metadata()
        campos_contacto = metadata.nombres_de_columnas
        try:
            campos_contacto.remove('telefono')
        except ValueError:
            logger.warning("La BD no tiene campo 'telefono'")
        return campos_contacto

    def establecer_valores_iniciales_agente_contacto(self):
        """
        Rellena con valores iniciales la tabla que informa el estado de los contactos
        en relación con los agentes
        """
        # obtenemos todos los contactos de la campaña
        campana_contactos = self.bd_contacto.contactos.all()

        # obtenemos los campos de la BD del contacto
        campos_contacto = self._obtener_campos_bd_contacto(self.bd_contacto)

        # creamos los objetos del modelo AgenteEnContacto a crear
        agente_en_contacto_list = []
        for contacto in campana_contactos:
            datos_contacto = literal_eval(contacto.datos)
            datos_contacto = dict(zip(campos_contacto, datos_contacto))
            datos_contacto_json = json.dumps(datos_contacto)
            agente_en_contacto = AgenteEnContacto(
                agente_id=-1, contacto_id=contacto.pk, datos_contacto=datos_contacto_json,
                telefono_contacto=contacto.telefono, campana_id=self.pk,
                estado=AgenteEnContacto.ESTADO_INICIAL)
            agente_en_contacto_list.append(agente_en_contacto)

        # insertamos las instancias en la BD
        AgenteEnContacto.objects.bulk_create(agente_en_contacto_list)

    def finalizar_relacion_agente_contacto(self, contacto_pk):
        """
        Marca como finalizada la relación entre un agente y un contacto de una campaña
        preview
        """
        try:
            agente_en_contacto = AgenteEnContacto.objects.get(
                contacto_id=contacto_pk, campana_id=self.pk)
        except AgenteEnContacto.DoesNotExist:
            # para el caso cuando se llama al procedimiento luego de añadir un
            # nuevo contacto desde la consola de agentes
            pass
        else:
            agente_en_contacto.estado = AgenteEnContacto.ESTADO_FINALIZADO
            agente_en_contacto.save()

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

    def get_string_queue_asterisk(self):
        if self.queue_campana:
            return self.queue_campana.get_string_queue_asterisk()


class QueueManager(models.Manager):

    def ultimo_queue_asterisk(self):
        number = Queue.objects.all().aggregate(Max('queue_asterisk'))
        if number['queue_asterisk__max'] is None:
            return 1
        else:
            return number['queue_asterisk__max'] + 1

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

    campana = models.OneToOneField(
        Campana,
        related_name='queue_campana', blank=True, null=True
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
    queue_asterisk = models.PositiveIntegerField(unique=True)
    auto_grabacion = models.BooleanField(default=False,
                                         verbose_name='Grabar llamados')
    detectar_contestadores = models.BooleanField(default=False)
    ep_id_wombat = models.IntegerField(null=True, blank=True)

    # announcements
    announce = models.CharField(max_length=128, blank=True, null=True)
    announce_frequency = models.BigIntegerField(blank=True, null=True)

    audio_para_contestadores = models.ForeignKey(ArchivoDeAudio, blank=True, null=True,
                                                 on_delete=models.SET_NULL,
                                                 related_name='queues_contestadores')
    audio_de_ingreso = models.ForeignKey(ArchivoDeAudio, blank=True, null=True,
                                         on_delete=models.SET_NULL,
                                         related_name='queues_ingreso')

    # Predictiva
    initial_predictive_model = models.BooleanField(default=False)
    initial_boost_factor = models.DecimalField(
        default=1.0, max_digits=3, decimal_places=1, blank=True, null=True)

    # campos que no usamos
    musiconhold = models.CharField(max_length=128, blank=True, null=True)
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
    announce_holdtime = models.CharField(max_length=128, blank=True, null=True)
    joinempty = models.CharField(max_length=128, blank=True, null=True)
    leavewhenempty = models.CharField(max_length=128, blank=True, null=True)
    reportholdtime = models.NullBooleanField(blank=True, null=True)
    memberdelay = models.BigIntegerField(blank=True, null=True)
    timeoutrestart = models.NullBooleanField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def guardar_ep_id_wombat(self, ep_id_wombat):
        self.ep_id_wombat = ep_id_wombat
        self.save()

    def get_string_queue_asterisk(self):
        return '0078' + str(self.queue_asterisk)

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

    def existe_member_queue(self, member, queue):
        return self.obtener_member_por_queue(queue).filter(
            member=member).exists()

    def get_campanas_activas(self):
        return self.filter(queue_name__campana__estado=Campana.ESTADO_ACTIVA)


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

    def __unicode__(self):
        return "agente: {0} para la campana {1} ".format(
            self.member.user.get_full_name(), self.queue_name)

    class Meta:
        db_table = 'queue_member_table'
        unique_together = ('queue_name', 'member',)


class PausaManager(models.Manager):
    def activas(self):
        return self.filter(eliminada=False)

    def eliminadas(self):
        return self.filter(eliminada=True)


class Pausa(models.Model):
    objects = PausaManager()

    TIPO_PRODUCTIVA = 'P'
    CHOICE_PRODUCTIVA = 'Productiva'
    TIPO_RECREATIVA = 'R'
    CHOICE_RECREATIVA = 'Recreativa'
    TIPO_CHOICES = ((TIPO_PRODUCTIVA, CHOICE_PRODUCTIVA), (TIPO_RECREATIVA, CHOICE_RECREATIVA))
    nombre = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=TIPO_PRODUCTIVA)
    eliminada = models.BooleanField(default=False)

    def __unicode__(self):
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
            raise(SuspiciousOperation("No se encontro base datos en "
                                      "estado ESTADO_EN_DEFINICION"))

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
            raise(SuspiciousOperation("No se encontro base datos en "
                                      "estado ESTADO_EN_DEFINICION o ACTULIZADA"
                                      ))

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
            raise(SuspiciousOperation("No se encontro base datos en "
                                      "estado ESTADO_EN_DEFINICION"))


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
            raise(ValueError("La cantidad de columnas no ha sido seteada"))

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
            raise(ValueError("No se ha seteado 'columna_con_telefono'"))

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
    def primer_fila_es_encabezado(self):
        try:
            return self._metadata['prim_fila_enc']
        except KeyError:
            raise(ValueError("No se ha seteado si primer "
                             "fila es encabezado"))

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
            logger.exception("Error: {0} detectada al desserializar "
                             "datos extras. Datos extras: '{1}'"
                             "".format(e.message, datos_json))
            raise

        assert len(datos) == self.cantidad_de_columnas

        telefono = datos[col_telefono]
        return telefono

    def obtener_telefono_y_datos_extras(self, datos_json):
        """Devuelve tupla con (1) el numero telefonico del contacto,
        y (2) un dict con los datos extras del contacto

        :param datos: atribuito 'datos' del contacto, o sea, valores de
                      las columnas codificadas con json
        """
        # Decodificamos JSON
        try:
            datos = json.loads(datos_json)
        except Exception as e:
            logger.exception("Error: {0} detectada al desserializar "
                             "datos extras. Datos extras: '{1}'"
                             "".format(e.message, datos_json))
            raise

        assert len(datos) == self.cantidad_de_columnas

        # Obtenemos telefono
        telefono = datos[self.columna_con_telefono]

        # Obtenemos datos extra
        datos_extra = dict(zip(self.nombres_de_columnas,
                               datos))

        return telefono, datos_extra

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
        Devuelve True si el dato extra correspondiente a la columna
        con numero telefonico.

        Este metodo no realiza ningun tipo de sanitizacion del nombre
        de columna recibido por parametro! Se supone que el nombre
        de columna es valido y existe.

        :raises ValueError: si la columna no existe
        """
        index = self.nombres_de_columnas.index(nombre_de_columna)
        return index == self.columna_con_telefono

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
        return not (
            index in self.columnas_con_hora or
            index in self.columnas_con_fecha or
            index == self.columna_con_telefono)


class MetadataBaseDatosContacto(MetadataBaseDatosContactoDTO):
    """Encapsula acceso a metadatos de BaseDatosContacto"""

    def __init__(self, bd):
        super(MetadataBaseDatosContacto, self).__init__()
        self.bd = bd
        if bd.metadata is not None and bd.metadata != '':
            try:
                self._metadata = json.loads(bd.metadata)
            except Exception as e:
                logger.exception("Error: {0} detectada al desserializar "
                                 "metadata de la bd {1}".format(e.message, bd.id))
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
        except Exception as e:
            logger.exception("Error: {0} detectada al serializar "
                             "metadata de la bd {1}".format(e.message, self.bd.id))
            raise


class BaseDatosContacto(models.Model):
    objects = BaseDatosContactoManager()

    DATO_EXTRA_GENERICO = 'GENERICO'
    DATO_EXTRA_FECHA = 'FECHA'
    DATO_EXTRA_HORA = 'HORA'

    DATOS_EXTRAS = (
        (DATO_EXTRA_GENERICO, 'Dato Genérico'),
        (DATO_EXTRA_FECHA, 'Fecha'),
        (DATO_EXTRA_HORA, 'Hora'),
    )

    ESTADO_EN_DEFINICION = 0
    ESTADO_DEFINIDA = 1
    ESTADO_EN_DEPURACION = 2
    ESTADO_DEPURADA = 3
    ESTADO_DEFINIDA_ACTUALIZADA = 4
    ESTADOS = (
        (ESTADO_EN_DEFINICION, 'En Definición'),
        (ESTADO_DEFINIDA, 'Definida'),
        (ESTADO_EN_DEPURACION, 'En Depuracion'),
        (ESTADO_DEPURADA, 'Depurada'),
        (ESTADO_DEFINIDA_ACTUALIZADA, 'Definida en actualizacion')
    )

    nombre = models.CharField(
        max_length=128,
    )
    fecha_alta = models.DateTimeField(
        auto_now_add=True,
    )
    archivo_importacion = models.FileField(
        upload_to=upload_to,
        max_length=256,
    )
    nombre_archivo_importacion = models.CharField(
        max_length=256,
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

    def __unicode__(self):
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
        logger.info("Seteando base datos contacto %s como definida", self.id)
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
        copia = BaseDatosContacto.objects.create(
            nombre='{0} (reciclada)'.format(self.nombre),
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


class ContactoManager(models.Manager):

    def contactos_by_telefono(self, telefono):
        try:
            return self.filter(telefono__contains=telefono)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "número télefonico"))

    def contactos_by_filtro(self, filtro):
        try:
            return self.filter(Q(telefono__contains=filtro) |
                               Q(pk__contains=filtro))
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "filtro"))

    def contactos_by_filtro_bd_contacto(self, bd_contacto, filtro):
        try:
            contactos = self.filter(Q(telefono__contains=filtro))
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
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "base de datos de contactos"))

    def contactos_by_bds_contacto(self, bds_contacto):
        try:
            return self.filter(bd_contacto__in=bds_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontraron contactos con esas "
                                       "bases de datos de contactos"))

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
        related_name='contactos', blank=True, null=True
    )

    def obtener_telefono_y_datos_extras(self, metadata):
        """Devuelve lista con (telefono, datos_extras) utilizando
        la informacion de metadata pasada por parametro.

        Recibimos `metadata` por parametro por una cuestion de
        performance.
        """
        telefono, extras = metadata.obtener_telefono_y_datos_extras(self.datos)
        return (telefono, extras)

    def __unicode__(self):
        return '{0} >> {1}'.format(
            self.bd_contacto, self.datos)


class MensajeRecibidoManager(models.Manager):

    def mensaje_recibido_por_remitente(self):
        return self.values('remitente').annotate(Max('timestamp'))

    def mensaje_remitente_fecha(self, remitente, timestamp):
        try:
            return self.get(remitente=remitente, timestamp=timestamp)
        except MensajeRecibido.DoesNotExist:
            raise (SuspiciousOperation("No se encontro mensaje recibido con esa"
                                       " fecha y remitente"))


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

    def __unicode__(self):
        return "mensaje recibido del numero {0}".format(self.remitente)

    class Meta:
        db_table = 'mensaje_recibido'


class MensajeEnviado(models.Model):
    remitente = models.CharField(max_length=20)
    destinatario = models.CharField(max_length=20)
    timestamp = models.CharField(max_length=255)
    agente = models.ForeignKey(AgenteProfile)
    content = models.TextField()
    result = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "mensaje enviado al número {0}".format(self.destinatario)

    class Meta:
        db_table = 'mensaje_enviado'


class GrabacionManager(models.Manager):

    def grabacion_by_fecha(self, fecha):
        try:
            return self.filter(fecha=fecha)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con esa "
                                       "fecha"))

    def grabacion_by_fecha_intervalo(self, fecha_inicio, fecha_fin):
        fecha_inicio = datetime.datetime.combine(fecha_inicio,
                                                 datetime.time.min)
        fecha_fin = datetime.datetime.combine(fecha_fin, datetime.time.max)
        try:
            return self.filter(fecha__range=(fecha_inicio, fecha_fin))
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con ese rango "
                                       "de fechas"))

    def grabacion_by_fecha_intervalo_campanas(self, fecha_inicio, fecha_fin, campanas):
        fecha_inicio = datetime.datetime.combine(fecha_inicio,
                                                 datetime.time.min)
        fecha_fin = datetime.datetime.combine(fecha_fin, datetime.time.max)
        try:
            return self.filter(fecha__range=(fecha_inicio, fecha_fin),
                               campana__in=campanas).order_by('-fecha')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con ese rango "
                                       "de fechas"))

    def grabacion_by_tipo_llamada(self, tipo_llamada):
        try:
            return self.filter(tipo_llamada=tipo_llamada)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con esa "
                                       "tipo llamada"))

    def grabacion_by_id_cliente(self, id_cliente):
        try:
            return self.filter(id_cliente__contains=id_cliente)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con esa "
                                       "id cliente"))

    def grabacion_by_tel_cliente(self, tel_cliente):
        try:
            return self.filter(tel_cliente__contains=tel_cliente)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con esa "
                                       "tel de cliente"))

    def grabacion_by_sip_agente(self, sip_agente):
        try:
            return self.filter(sip_agente__contains=sip_agente)
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con esa "
                                       "sip agente"))

    def grabacion_by_filtro(self, fecha_desde, fecha_hasta, tipo_llamada,
                            tel_cliente, sip_agente, campana, campanas, marcadas):
        grabaciones = self.filter(campana__in=campanas)

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
            grabaciones = grabaciones.filter(fecha__range=(fecha_desde,
                                                           fecha_hasta))
        if tipo_llamada:
            grabaciones = grabaciones.filter(tipo_llamada=tipo_llamada)
        if tel_cliente:
            grabaciones = grabaciones.filter(tel_cliente__contains=tel_cliente)
        if sip_agente:
            grabaciones = grabaciones.filter(sip_agente=sip_agente)
        if campana:
            grabaciones = grabaciones.filter(campana=campana)
        if marcadas:
            total_grabaciones_marcadas = Grabacion.objects.marcadas()
            grabaciones = grabaciones & total_grabaciones_marcadas

        return grabaciones.order_by('-fecha')

    def obtener_count_campana(self):
        try:
            return self.values('campana', 'campana__nombre').annotate(
                cantidad=Count('campana')).order_by('campana')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro grabaciones "))

    def obtener_count_agente(self):
        try:
            return self.values('sip_agente').annotate(
                cantidad=Count('sip_agente')).order_by('sip_agente')
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro grabaciones "))

    def marcadas(self):
        marcaciones = GrabacionMarca.objects.values_list('uid', flat=True)
        return self.filter(uid__in=marcaciones)


class Grabacion(models.Model):
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = GrabacionManager()
    TYPE_ICS = 1
    """Tipo de llamada ICS"""

    TYPE_DIALER = 2
    """Tipo de llamada DIALER"""

    TYPE_INBOUND = 3
    """Tipo de llamada inbound"""

    TYPE_MANUAL = 4
    """Tipo de llamada manual"""

    TYPE_PREVIEW = 5
    # tipo de llamada preview

    TYPE_LLAMADA_CHOICES = (
        (TYPE_ICS, 'ICS'),
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
    sip_agente = models.IntegerField()
    campana = models.ForeignKey(Campana, related_name='grabaciones')
    uid = models.CharField(max_length=45, blank=True, null=True)

    def __unicode__(self):
        return "grabacion del agente con el sip {0} con el cliente {1}".format(
            self.sip_agente, self.id_cliente)

    def obtener_nombre_agente(self):
        agente = AgenteProfile.objects.obtener_agente_por_sip(self.sip_agente)
        if agente:
            return agente.user.get_full_name()
        return self.sip_agente


class GrabacionMarca(models.Model):
    """
    Contiene los atributos de una grabación marcada
    """
    uid = models.CharField(max_length=45)
    descripcion = models.TextField()

    def __unicode__(self):
        return "Grabacion con uid={0} marcada con descripcion={1}".format(
            self.uid, self.descripcion)

    class Meta:
        db_table = 'ominicontacto_app_grabacion_marca'


class AgendaManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=datetime.datetime.today())
        except Agenda.DoesNotExist:
            raise (SuspiciousOperation("No se encontro evenos en el dia de la "
                                       "fecha"))

    def eventos_filtro_fecha(self, fecha_desde, fecha_hasta):
        eventos = self.filter()
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
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
                               related_name='eventos')
    es_personal = models.BooleanField()
    fecha = models.DateField()
    hora = models.TimeField()
    es_smart = models.BooleanField()
    medio_comunicacion = models.PositiveIntegerField(
        choices=MEDIO_COMUNICACION_CHOICES)
    telefono = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    descripcion = models.TextField()

    def __unicode__(self):
        return "Evento programado para la fecha {0} a las {1} hs".format(
            self.fecha, self.hora)


class CalificacionClienteManager(models.Manager):

    def obtener_cantidad_calificacion_campana(self, campana):
        try:
            return self.values('calificacion').annotate(
                cantidad=Count('calificacion')).filter(campana=campana)
        except CalificacionCliente.DoesNotExist:
            raise (SuspiciousOperation("No se encontro califacaciones "))


class CalificacionCliente(models.Model):

    objects = CalificacionClienteManager()

    campana = models.ForeignKey(Campana, related_name="calificaconcliente")
    contacto = models.ForeignKey(Contacto)
    es_venta = models.BooleanField(default=False)
    calificacion = models.ForeignKey(Calificacion, blank=False, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    agente = models.ForeignKey(AgenteProfile, related_name="calificaciones")
    observaciones = models.TextField(blank=True, null=True)
    wombat_id = models.IntegerField()
    agendado = models.BooleanField(default=False)

    def __unicode__(self):
        return "Calificacion para la campana {0} para el contacto " \
               "{1} ".format(self.campana, self.contacto)

    def get_venta(self):
        try:
            return MetadataCliente.objects.get(campana=self.campana,
                                               agente=self.agente,
                                               contacto=self.contacto)
        except MetadataCliente.DoesNotExist:
            return None
        except MetadataCliente.MultipleObjectsReturned:
            return None


class DuracionDeLlamada(models.Model):
    """Representa la duración de las llamdas de las campanas, con el fin
        de contar con los datos para búsquedas y estadísticas"""

    TYPE_ICS = 1
    """Tipo de llamada ICS"""

    TYPE_DIALER = 2
    """Tipo de llamada DIALER"""

    TYPE_INBOUND = 3
    """Tipo de llamada inbound"""

    TYPE_MANUAL = 4
    """Tipo de llamada manual"""

    TYPE_LLAMADA_CHOICES = (
        (TYPE_ICS, 'ICS'),
        (TYPE_DIALER, 'DIALER'),
        (TYPE_INBOUND, 'INBOUND'),
        (TYPE_MANUAL, 'MANUAL'),
    )

    agente = models.ForeignKey(AgenteProfile, related_name="llamadas")
    numero_telefono = models.CharField(max_length=20)
    fecha_hora_llamada = models.DateTimeField(auto_now=True)
    tipo_llamada = models.PositiveIntegerField(choices=TYPE_LLAMADA_CHOICES)
    duracion = models.TimeField()


class MetadataCliente(models.Model):
    agente = models.ForeignKey(AgenteProfile, related_name="metadataagente")
    campana = models.ForeignKey(Campana, related_name="metadatacliente")
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE)
    metadata = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Metadata para el contacto {0} de la campana{1} " \
               "{1} ".format(self.contacto, self.campana)


class Chat(models.Model):
    agente = models.ForeignKey(AgenteProfile, related_name="chatsagente")
    user = models.ForeignKey(User, related_name="chatsusuario")
    fecha_hora_chat = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Chat entre el agente {0} y el usuario {1} " \
               "{1} ".format(self.agente, self.user)


class MensajeChat(models.Model):
    sender = models.ForeignKey(User, related_name="chatssender")
    to = models.ForeignKey(User, related_name="chatsto")
    mensaje = models.TextField()
    fecha_hora = models.DateTimeField(auto_now=True)
    chat = models.ForeignKey(Chat, related_name="mensajeschat")


class WombatLogManager(models.Manager):

    def obtener_wombat_log_contacto(self, contacto):
        try:
            return self.filter(contacto=contacto)
        except WombatLog.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contacto con el id"
                                       ": {0}".format(contacto.pk)))


class WombatLog(models.Model):
    objects = WombatLogManager()

    campana = models.ForeignKey(Campana, related_name="logswombat")
    contacto = models.ForeignKey(Contacto)
    agente = models.ForeignKey(AgenteProfile, related_name="logsaagente",
                               blank=True, null=True)
    telefono = models.CharField(max_length=128)
    estado = models.CharField(max_length=128)
    calificacion = models.CharField(max_length=128)
    timeout = models.IntegerField()
    metadata = models.TextField()
    fecha_hora = models.DateTimeField(auto_now=True)


class QueuelogManager(models.Manager):

    def llamadas_iniciadas(self):
        return Queuelog.objects.filter(event='ENTERQUEUE')

    def obtener_log_agente_event_periodo_all(
            self, eventos, fecha_desde, fecha_hasta, agente):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(queuename='ALL', event__in=eventos, agent=agente,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_agente_pk_event_periodo_all(
            self, eventos, fecha_desde, fecha_hasta, agente_pk):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(queuename='ALL', event__in=eventos, agent_id=agente_pk,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_agente_event_periodo(
            self, eventos, fecha_desde, fecha_hasta, agente):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(event__in=eventos, agent=agente,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_agente_pk_event_periodo(
            self, eventos, fecha_desde, fecha_hasta, agente_pk):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(event__in=eventos, agent_id=agente_pk,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_agente_campana_event_periodo(
            self, eventos, fecha_desde, fecha_hasta, agente_pk, campana_pk):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(event__in=eventos, agent_id=agente_pk,
                               campana_id=campana_pk,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_campana_id_event_periodo(
            self, eventos, fecha_desde, fecha_hasta, campana_pk):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(event__in=eventos, campana_id=campana_pk,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_log_event_periodo(self, eventos, fecha_desde, fecha_hasta):
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
        try:
            return self.filter(event__in=eventos,
                               time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        except Queuelog.DoesNotExist:
            raise(SuspiciousOperation("No se encontro agente con esos filtros "))

    def obtener_agentes_campanas_total(self, eventos, fecha_desde, fecha_hasta, agentes,
                                       campanas):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)

        cursor = connection.cursor()
        sql = """select agent, queuename, SUM(data2::integer), Count(*)
                 from ominicontacto_app_queuelog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 and queuename = ANY(%(campanas)s) GROUP BY agent, queuename order by
                 agent, queuename
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
            'campanas': ["{0}_{1}".format(campana.id, campana.nombre)
                         for campana in campanas],
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_tiempo_llamadas_agente(self, eventos, fecha_desde, fecha_hasta, agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)

        cursor = connection.cursor()
        sql = """select agent_id, SUM(data2::integer)
                 from ominicontacto_app_queuelog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 GROUP BY agent_id order by agent_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_count_evento_agente(self, eventos, fecha_desde, fecha_hasta, agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)

        cursor = connection.cursor()
        sql = """select agent_id, count(*)
                 from ominicontacto_app_queuelog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 GROUP BY agent_id order by agent_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_tiempo_llamadas_saliente_agente(self, eventos, fecha_desde, fecha_hasta,
                                                agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)

        cursor = connection.cursor()
        sql = """select agent_id, SUM(data2::integer)
                 from ominicontacto_app_queuelog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 and data4='saliente'
                 GROUP BY agent_id order by agent_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_count_saliente_evento_agente(self, eventos, fecha_desde, fecha_hasta,
                                             agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)

        cursor = connection.cursor()
        sql = """select agent_id, count(*)
                 from ominicontacto_app_queuelog where time between %(fecha_desde)s and
                 %(fecha_hasta)s and event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 and data4='saliente'
                 GROUP BY agent_id order by agent_id
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,
        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def obtener_tiempos_event_agentes(self, eventos, fecha_desde, fecha_hasta,
                                      agentes):

        if fecha_desde and fecha_hasta:
            fecha_desde = datetime_hora_minima_dia(fecha_desde)
            fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        cursor = connection.cursor()
        sql = """select agent_id, time, event, data1
                 from ominicontacto_app_queuelog where
                 time between %(fecha_desde)s and %(fecha_hasta)s and
                 event = ANY(%(eventos)s) and agent_id = ANY(%(agentes)s)
                 and queuename = 'ALL'  order by agent_id, time desc
        """
        params = {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'eventos': eventos,
            'agentes': agentes,

        }

        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values


class Queuelog(models.Model):

    objects = QueuelogManager()

    time = models.DateTimeField()
    callid = models.CharField(max_length=32, blank=True, null=True)
    queuename = models.CharField(max_length=32, blank=True, null=True)
    campana_id = models.IntegerField(blank=True, null=True)
    agent = models.CharField(max_length=32, blank=True, null=True)
    agent_id = models.IntegerField(blank=True, null=True)
    event = models.CharField(max_length=32, blank=True, null=True)
    data1 = models.CharField(max_length=128, blank=True, null=True)
    data2 = models.CharField(max_length=128, blank=True, null=True)
    data3 = models.CharField(max_length=128, blank=True, null=True)
    data4 = models.CharField(max_length=128, blank=True, null=True)
    data5 = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return "Log queue en la fecha {0} de la queue {1} del agente {2} " \
               "con el evento {3} ".format(self.time, self.queuename,
                                           self.agent, self.event)


class AgendaContactoManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=datetime.datetime.today())
        except AgendaContacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro evenos en el dia de la "
                                       "fecha"))

    def eventos_filtro_fecha(self, fecha_desde, fecha_hasta):
        eventos = self.filter(tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
            eventos = eventos.filter(fecha__range=(fecha_desde, fecha_hasta))
        else:
            hoy_ahora = datetime.datetime.today()
            hoy = hoy_ahora.date()
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

    agente = models.ForeignKey(AgenteProfile, related_name="agendacontacto")
    contacto = models.ForeignKey(Contacto)
    fecha = models.DateField()
    hora = models.TimeField()
    tipo_agenda = models.PositiveIntegerField(choices=TYPE_AGENDA_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    campana = models.ForeignKey(Campana, related_name='agendas', null=True)

    def __unicode__(self):
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
                    'hora_desde': ["La hora desde debe ser\
                        menor o igual a la hora hasta."],
                    'hora_hasta': ["La hora hasta debe ser\
                        mayor a la hora desde."],
                })

            conflicto = self.get_campana().actuacionesdialer.filter(
                dia_semanal=self.dia_semanal,
                hora_desde__lte=self.hora_hasta,
                hora_hasta__gte=self.hora_desde,
            )
            if any(conflicto):
                raise ValidationError({
                    'hora_desde': ["Ya esta cubierto el rango horario\
                        en ese día semanal."],
                    'hora_hasta': ["Ya esta cubierto el rango horario\
                        en ese día semanal."],
                })


# class Actuacion(AbstractActuacion):
#     """
#     Representa los días de la semana y los
#     horarios en que una campaña se ejecuta.
#     """
#
#     campana = models.ForeignKey(
#         'CampanaDialer',
#         related_name='actuacionesdialer'
#     )
#
#     def __unicode__(self):
#         return "Campaña {0} - Actuación: {1}".format(
#             self.campana,
#             self.get_dia_semanal_display(),
#         )
#
#     def get_campana(self):
#         return self.campana


class ActuacionVigente(models.Model):
    """
    Modelo  para las actuaciones de las campanas

    """

    """Dias de la semana, compatibles con datetime.date.weekday()"""

    campana = models.OneToOneField(Campana)
    domingo = models.BooleanField()
    lunes = models.BooleanField()
    martes = models.BooleanField()
    miercoles = models.BooleanField()
    jueves = models.BooleanField()
    viernes = models.BooleanField()
    sabado = models.BooleanField()
    hora_desde = models.TimeField()
    hora_hasta = models.TimeField()

    def __unicode__(self):
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
        max_length=128,
    )
    fecha_alta = models.DateTimeField(
        auto_now_add=True,
    )
    archivo_importacion = models.FileField(
        upload_to=upload_to,
        max_length=256,
    )
    nombre_archivo_importacion = models.CharField(
        max_length=256,
    )

    sin_definir = models.BooleanField(
        default=True,
    )
    cantidad_contactos = models.PositiveIntegerField(
        default=0)

    def __unicode__(self):
        return "{0}: ({1} contactos)".format(self.nombre,
                                             self.cantidad_contactos)


class ContactoBacklist(models.Model):
    """
    Lista de contacto que no quieren que los llamen
    """

    telefono = models.CharField(max_length=128)
    back_list = models.ForeignKey(
        Backlist, related_name='contactosbacklist', blank=True, null=True)

    def __unicode__(self):
        return "Telefono no llame {0}  ".format(self.telefono)


class SitioExterno(models.Model):
    """
    sitio externo para embeber en el agente
    """

    nombre = models.CharField(max_length=128)
    url = models.CharField(max_length=256)
    oculto = models.BooleanField(default=False)

    def __unicode__(self):
        return "Sitio: {0} - url: {1}".format(self.nombre, self.url)

    def ocultar(self):
        """setea la campana como oculta"""
        self.oculto = True
        self.save()

    def desocultar(self):
        """setea la campana como visible"""
        self.oculto = False
        self.save()


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
        (RS_BUSY, "Ocupado"),
        (TERMINATED, "Contestador"),
        (RS_NOANSWER, "No atendido"),
        (RS_REJECTED, "Rechazado"),
        (RS_TIMEOUT, "Timeout")
    )

    FIXED = 1

    MULT = 2

    EN_MODO_CHOICES = (
        (FIXED, "FIXED"),
        (MULT, "MULT")
    )

    campana = models.ForeignKey(Campana, related_name='reglas_incidencia')
    estado = models.PositiveIntegerField(choices=ESTADOS_CHOICES)
    estado_personalizado = models.CharField(max_length=128, blank=True, null=True)
    intento_max = models.IntegerField()
    reintentar_tarde = models.IntegerField()
    en_modo = models.PositiveIntegerField(choices=EN_MODO_CHOICES, default=MULT)

    def __unicode__(self):
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


class UserApiCrm(models.Model):
    usuario = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=128)

    def __unicode__(self):
        return self.usuario


class CalificacionManual(models.Model):

    # objects = CalificacionClienteManager()

    campana = models.ForeignKey(Campana, related_name="calificacionmanual")
    telefono = models.CharField(max_length=128)
    es_gestion = models.BooleanField(default=False)
    calificacion = models.ForeignKey(Calificacion, blank=False, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    agente = models.ForeignKey(AgenteProfile, related_name="calificacionesmanuales")
    observaciones = models.TextField(blank=True, null=True)
    agendado = models.BooleanField(default=False)
    metadata = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "Calificacion manual para la campana {0} para el telefono " \
               "{1} ".format(self.campana, self.telefono)


class AgendaManualManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=datetime.datetime.today())
        except AgendaContacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro evenos en el dia de la "
                                       "fecha"))

    def eventos_filtro_fecha(self, fecha_desde, fecha_hasta):
        eventos = self.filter(tipo_agenda=AgendaManual.TYPE_PERSONAL)
        if fecha_desde and fecha_hasta:
            fecha_desde = datetime.datetime.combine(fecha_desde,
                                                    datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_hasta,
                                                    datetime.time.max)
            eventos = eventos.filter(fecha__range=(fecha_desde, fecha_hasta))
        else:
            hoy_ahora = datetime.datetime.today()
            hoy = hoy_ahora.date()
            eventos = eventos.filter(fecha__gte=hoy)
        return eventos.order_by('-fecha')


class AgendaManual(models.Model):
    objects = AgendaManualManager()

    TYPE_PERSONAL = 1
    """Tipo de agenda Personal"""

    TYPE_GLOBAL = 2
    """Tipo de agenda Global"""

    TYPE_AGENDA_CHOICES = (
        (TYPE_PERSONAL, 'PERSONAL'),
        (TYPE_GLOBAL, 'GLOBAL'),
    )

    agente = models.ForeignKey(AgenteProfile, related_name="agendamanual")
    telefono = models.CharField(max_length=128)
    fecha = models.DateField()
    hora = models.TimeField()
    tipo_agenda = models.PositiveIntegerField(choices=TYPE_AGENDA_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    campana = models.ForeignKey(Campana, related_name="agendas_manuales", null=True)

    def __unicode__(self):
        return "Agenda para el telefono {0} agendado por el agente {1}" \
               " para la fecha {2} a la hora {3}hs ".format(
                   self.telefono, self.agente, self.fecha, self.hora)


class AgenteEnContacto(models.Model):
    """
    Relaciona a agentes que están en comunicación con contactos de la BD de una campaña
    """

    ESTADO_INICIAL = 0  # significa que el contacto aún no ha sido entregado a ningún agente

    ESTADO_ENTREGADO = 1  # significa que un agente solicitó este contacto y le fue entregado

    ESTADO_FINALIZADO = 2  # significa que el agente culminó de forma satisfactoria la llamada

    ESTADO_CHOICES = (
        (ESTADO_INICIAL, 'INICIAL'),
        (ESTADO_ENTREGADO, 'ENTREGADO'),
        (ESTADO_FINALIZADO, 'FINALIZADO'),
    )
    agente_id = models.IntegerField()
    contacto_id = models.IntegerField()
    datos_contacto = models.TextField()
    telefono_contacto = models.CharField(max_length=128)
    campana_id = models.IntegerField()
    estado = models.PositiveIntegerField(choices=ESTADO_CHOICES)
    modificado = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return "Agente de id={0} relacionado con contacto de id={1} con el estado {2}".format(
            self.agente_id, self.contacto_id, self.estado)
