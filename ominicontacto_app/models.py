# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import logging
import uuid
import re
import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db.models import Max, Q, Count
from django.core.exceptions import ValidationError, SuspiciousOperation
from ominicontacto_app.utiles import log_timing,\
    ValidadorDeNombreDeCampoExtra

logger = logging.getLogger(__name__)

SUBSITUTE_REGEX = re.compile(r'[^a-z\._-]')


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
    auto_attend_ics = models.BooleanField(default=False)
    auto_attend_inbound = models.BooleanField(default=False)
    auto_attend_dialer = models.BooleanField(default=False)
    auto_pause = models.BooleanField(default=False)

    def __unicode__(self):
        return self.nombre


class AgenteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sip_extension = models.IntegerField(unique=True)
    sip_password = models.CharField(max_length=128, blank=True, null=True)
    modulos = models.ManyToManyField(Modulo)
    grupo = models.ForeignKey(Grupo)

    def __unicode__(self):
        return self.user.get_full_name()

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

    ESTADOS = (
        (ESTADO_EN_DEFINICION, '(en definicion)'),
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_FINALIZADA, 'Finalizada'),
        (ESTADO_BORRADA, 'Borrada'),
    )

    estado = models.PositiveIntegerField(
        choices=ESTADOS,
        default=ESTADO_EN_DEFINICION,
    )
    nombre = models.CharField(max_length=128)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    bd_contacto = models.ForeignKey(
        'BaseDatosContacto',
        null=True, blank=True,
        related_name="%(class)ss"
    )

    def __unicode__(self):
            return self.nombre


class QueueManager(models.Manager):

    def ultimo_queue_asterisk(self):
        number = Queue.objects.all().aggregate(Max('queue_asterisk'))
        if number['queue_asterisk__max'] is None:
            return 1
        else:
            return number['queue_asterisk__max'] + 1


class Queue(models.Model):
    """
    Clase cola para el servidor de kamailio
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

    TYPE_ICS = 1
    """Tipo de cola ICS"""

    TYPE_DIALER = 2
    """Tipo de cola DIALER"""

    TYPE_INBOUND = 3
    """Tipo de cola inbound"""

    TYPE_CHOICES = (
        (TYPE_ICS, 'ICS'),
        (TYPE_DIALER, 'DIALER'),
        (TYPE_INBOUND, 'INBOUND'),
    )

    campana = models.OneToOneField(
        Campana,
        related_name='queue_campana', blank=True, null=True
    )

    name = models.CharField(max_length=128, primary_key=True)
    timeout = models.BigIntegerField()
    retry = models.BigIntegerField()
    maxlen = models.BigIntegerField()
    wrapuptime = models.BigIntegerField()
    servicelevel = models.BigIntegerField()
    strategy = models.CharField(max_length=128, choices=STRATEGY_CHOICES)
    eventmemberstatus = models.BooleanField()
    eventwhencalled = models.BooleanField()
    weight = models.BigIntegerField()
    ringinuse = models.BooleanField()
    setinterfacevar = models.BooleanField()
    members = models.ManyToManyField(AgenteProfile, through='QueueMember')
    type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    wait = models.PositiveIntegerField()
    queue_asterisk = models.PositiveIntegerField(unique=True)
    auto_grabacion = models.BooleanField(default=False)

    # campos que no usamos
    musiconhold = models.CharField(max_length=128, blank=True, null=True)
    announce = models.CharField(max_length=128, blank=True, null=True)
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
    announce_frequency = models.BigIntegerField(blank=True, null=True)
    announce_round_seconds = models.BigIntegerField(blank=True, null=True)
    announce_holdtime = models.CharField(max_length=128, blank=True, null=True)
    joinempty = models.CharField(max_length=128, blank=True, null=True)
    leavewhenempty = models.CharField(max_length=128, blank=True, null=True)
    reportholdtime = models.NullBooleanField(blank=True, null=True)
    memberdelay = models.BigIntegerField(blank=True, null=True)
    timeoutrestart = models.NullBooleanField(blank=True, null=True)

    def __unicode__(self):
        return self.name

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
    penalty = models.IntegerField(choices=DIGITO_CHOICES,)
    paused = models.IntegerField()

    def __unicode__(self):
        return "agente: {0} para la campana {1} ".format(
            self.member.user.get_full_name(), self.queue_name)

    class Meta:
        db_table = 'queue_member_table'
        unique_together = ('queue_name', 'member',)


class Pausa(models.Model):
    nombre = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nombre


#==============================================================================
# Base Datos Contactos
#==============================================================================
class BaseDatosContactoManager(models.Manager):
    """Manager para BaseDatosContacto"""

    def obtener_definidas(self):
        """
        Este método filtra lo objetos BaseDatosContacto que
        esté definidos.
        """
        definidas = [BaseDatosContacto.ESTADO_DEFINIDA,
                     BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA]
        return self.filter(estado__in=definidas)

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
            "'columna_con_telefono' = {0} porque  la BD solo "
            "posee {1} columnas"
            "".format(columna, self.cantidad_de_columnas))
        self._metadata['col_telefono'] = columna

    # -----

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
            "recibe listas o tuplas. Se recibio: {0}".format(type(columnas)))
        for col in columnas:
            assert isinstance(col, int), ("Los elementos de "
            "'columnas_con_fecha' deben ser int. Se encontro: {0}".format(
                type(col)))
            assert col < self.cantidad_de_columnas, ("No se puede setear "
                "'columnas_con_fecha' = {0} porque  la BD solo "
                "posee {1} columnas"
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
            "recibe listas o tuplas. Se recibio: {0}".format(type(columnas)))
        for col in columnas:
            assert isinstance(col, int), ("Los elementos de "
            "'columnas_con_hora' deben ser int. Se encontro: {0}".format(
                type(col)))
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
            "recibe listas o tuplas. Se recibio: {0}".format(type(columnas)))
        assert len(columnas) == self.cantidad_de_columnas, ("Se intentaron "
            "setear {0} nombres de columnas, pero la BD posee {1} columnas"
            "".format(len(columnas), self.cantidad_de_columnas))

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
        except:
            logger.exception("Excepcion detectada al desserializar "
                             "datos extras. Datos extras: '{0}'"
                             "".format(datos_json))
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
        except:
            logger.exception("Excepcion detectada al desserializar "
                             "datos extras. Datos extras: '{0}'"
                             "".format(datos_json))
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
            assert index_columna < self.cantidad_de_columnas, (""
                "columnas_con_fecha: "
                "index_columna >= cantidad_de_columnas")

        for index_columna in self.columnas_con_hora:
            assert index_columna >= 0, "columnas_con_hora: index_columna < 0"
            assert index_columna < self.cantidad_de_columnas, (""
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
                    index in self.columnas_con_hora
                    or
                    index in self.columnas_con_fecha
                    or
                    index == self.columna_con_telefono
                    )


class MetadataBaseDatosContacto(MetadataBaseDatosContactoDTO):
    """Encapsula acceso a metadatos de BaseDatosContacto"""

    def __init__(self, bd):
        super(MetadataBaseDatosContacto, self).__init__()
        self.bd = bd
        if bd.metadata is not None and bd.metadata != '':
            try:
                self._metadata = json.loads(bd.metadata)
            except:
                logger.exception("Excepcion detectada al desserializar "
                                 "metadata de la bd {0}".format(bd.id))
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
        except:
            logger.exception("Excepcion detectada al serializar "
                             "metadata de la bd {0}".format(self.bd.id))
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
        assert self.estado == BaseDatosContacto.ESTADO_EN_DEFINICION
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


class ContactoManager(models.Manager):

    def contactos_by_telefono(self, telefono):
        try:
            return self.filter(telefono__contains=telefono)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "número télefonico"))

    def contactos_by_id_cliente(self, id_cliente):
        try:
            return self.filter(id_cliente=id_cliente)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "id_cliente"))

    def contactos_by_filtro(self, bd_contacto, filtro):
        try:
            contactos = self.filter(Q(nombre__contains=filtro) |
                                    Q(id_cliente__contains=filtro) |
                                    Q(apellido__contains=filtro) |
                                    Q(dni__contains=filtro) |
                                    Q(fecha_nacimiento__contains=filtro) |
                                    Q(cuil__contains=filtro))
            return contactos.filter(bd_contacto=bd_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "filtro"))

    def obtener_contacto_editar(self, id_cliente):
        """Devuelve el contacto pasado por ID, siempre que dicha
        pedido pueda ser editar
        FIXME: chequear que sea unico el id_cliente no está definido asi en el
        modelo
        En caso de no encontarse, lanza SuspiciousOperation
        """
        try:
            return self.get(id_cliente=id_cliente)
        except Contacto.DoesNotExist:
            return None

    def contactos_by_bd_contacto(self, bd_contacto):
        try:
            return self.filter(bd_contacto=bd_contacto)
        except Contacto.DoesNotExist:
            raise (SuspiciousOperation("No se encontro contactos con este "
                                       "base de datos de contactos"))


class Contacto(models.Model):
    objects_default = models.Manager()
    # Por defecto django utiliza el primer manager instanciado. Se aplica al
    # admin de django, y no aplica las customizaciones del resto de los
    # managers que se creen.

    objects = ContactoManager()

    telefono = models.CharField(max_length=128)
    id_cliente = models.IntegerField()
    nombre = models.CharField(max_length=128)
    apellido = models.CharField(max_length=128)
    dni = models.CharField(max_length=128)
    fecha_nacimiento = models.CharField(max_length=128)
    cuil = models.CharField(max_length=128)
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
        try:
            return self.filter(fecha__range=(fecha_inicio, fecha_fin))
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

    def grabacion_by_filtro(self, fecha, tipo_llamada, id_cliente,
                              tel_cliente, sip_agente, campana):
        grabaciones = self.filter()
        if fecha:
            grabaciones = grabaciones.filter(fecha=fecha)

        if tipo_llamada:
            grabaciones = grabaciones.filter(tipo_llamada=tipo_llamada)

        if id_cliente:
            grabaciones = grabaciones.filter(id_cliente=id_cliente)

        if tel_cliente:
            grabaciones = grabaciones.filter(tel_cliente=tel_cliente)

        if sip_agente:
            grabaciones = grabaciones.filter(sip_agente=sip_agente)
        if campana:
            grabaciones = grabaciones.filter(campana=campana)

        return grabaciones

    def obtener_count_campana(self):
        try:
            return self.values('campana__nombre').annotate(cantidad=Count('campana'))
        except Grabacion.DoesNotExist:
            raise (SuspiciousOperation("No se encontro grabaciones "))


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

    TYPE_LLAMADA_CHOICES = (
        (TYPE_ICS, 'ICS'),
        (TYPE_DIALER, 'DIALER'),
        (TYPE_INBOUND, 'INBOUND'),
        (TYPE_MANUAL, 'MANUAL'),
    )
    fecha = models.DateTimeField()
    tipo_llamada = models.PositiveIntegerField(choices=TYPE_LLAMADA_CHOICES)
    id_cliente = models.CharField(max_length=255)
    tel_cliente = models.CharField(max_length=255)
    grabacion = models.CharField(max_length=255)
    sip_agente = models.IntegerField()
    campana = models.ForeignKey(Campana, related_name='grabaciones')

    def __unicode__(self):
        return "grabacion del agente con el sip {0} con el cliente {1}".format(
            self.sip_agente, self.id_cliente)


class AgendaManager(models.Manager):

    def eventos_fecha_hoy(self):
        try:
            return self.filter(fecha=datetime.datetime.today())
        except Agenda.DoesNotExist:
            raise (SuspiciousOperation("No se encontro evenos en el dia de la "
                                       "fecha"))


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


class FormularioDemo(models.Model):

    campana = models.ForeignKey(Campana, related_name="formularios")
    contacto = models.ForeignKey(Contacto, related_name="formulario_contacto")
    extra_1 = models.TextField(blank=True, null=True)
    extra_2 = models.CharField(max_length=128, blank=True, null=True)
    extra_3 = models.CharField(max_length=128, blank=True, null=True)
    extra_4 = models.TextField(blank=True, null=True)
    extra_5 = models.CharField(max_length=128, blank=True, null=True)
    extra_6 = models.CharField(max_length=128, blank=True, null=True)
    extra_7 = models.CharField(max_length=128, blank=True, null=True)
    extra_8 = models.CharField(max_length=128, blank=True, null=True)
    extra_9 = models.CharField(max_length=128, blank=True, null=True)
    extra_10 = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return "Formulario demo para campana{0} para el contacto {1} ".format(
            self.campana, self.contacto)
