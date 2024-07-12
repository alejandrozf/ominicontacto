# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""Metodos utilitarios para ser reutilizados en los distintos
módulos de tests.
"""

from __future__ import unicode_literals

import os
import random
import datetime
import uuid
import shutil
import json
import tempfile

from django.test import TestCase, TransactionTestCase
from django.conf import settings
from django.test.utils import override_settings
from django.core.management import call_command
from django.contrib.auth.models import Group
from django.db import connections

from ominicontacto_app.models import (
    User, AgenteProfile, SupervisorProfile, Contacto,
    BaseDatosContacto, NombreCalificacion, Campana, Queue, OpcionCalificacion,
    ActuacionVigente, ReglasIncidencia, CalificacionCliente,
    ArchivoDeAudio
)
from ominicontacto_app.tests.factories import (NombreCalificacionFactory, GrupoFactory,
                                               QueueMemberFactory)
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from mock import Mock


PASSWORD = 'admin123'


def ru():
    """Devuelve random UUID"""
    return str(uuid.uuid4())


def rtel():
    """Devuelve nro telefonico aleatorio"""
    return str(random.randint(1140000000000000,
                              1149999999999999))


def _tmpdir():
    """Crea directorio temporal"""
    return tempfile.mkdtemp(prefix=".oml-tests-", dir="/dev/shm")


class OMLTestUtilsMixin(object):

    DEFAULT_PASSWORD = PASSWORD

    def get_test_resource(self, resource):
        """Devuelve el path completo a archivo del directorio test
        """
        tmp = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        resource1 = os.path.join(tmp, "test", resource)
        if os.path.exists(resource1):
            return resource1

        self.fail("Resource {0} no existe en ningulo "
                  "de los directorios buscados".format(resource))

    def read_test_resource(self, resource):
        """Devuelve el contenido de un archivo del directorio test/"""
        tmp = self.get_test_resource(resource)
        with open(tmp, 'r') as f:
            return f.read()

    def copy_test_resource_to_mediaroot(self, resource):
        """Copia test-resource a directorio MEDIA_ROOT.

        :returns: path absoluto al archivo en MEDIA_ROOT
        """
        tmp = self.get_test_resource(resource)
        filename = os.path.split(tmp)[1]
        new_path = os.path.join(settings.MEDIA_ROOT, filename)
        if not os.path.exists(new_path):
            shutil.copy(tmp, settings.MEDIA_ROOT)
        return new_path

    def crear_user_agente(self, first_name=None, last_name=None, username=None):
        """Crea un user"""

        if first_name is None:
            first_name = 'User_%i' % User.objects.count()
        if last_name is None:
            last_name = 'Test'
        if username is None:
            username = 'user_test_agente_%i' % User.objects.count()

        user = User.objects.create_user(
            username=username,
            email='user_agente@gmail.com',
            password=PASSWORD,
            is_agente=True,
            first_name=first_name,
            last_name=last_name,
        )
        return user

    def crear_user_supervisor(self, username=None):
        """Crea un user"""
        if username is None:
            username = 'user_test_supervisor_%i' % User.objects.count()
        user = User.objects.create_user(
            username=username,
            email='user_supervisor@gmail.com',
            password=PASSWORD,
            is_supervisor=True
        )
        return user

    def crear_agente_profile(self, user=None):
        if user is None:
            user = self.crear_user_agente()
        grupo = GrupoFactory(auto_unpause=0)
        profile = AgenteProfile.objects.create(
            user=user,
            sip_extension=1000 + user.id,
            sip_password="sdsfhdfhfdhfd",
            grupo=grupo,
            reported_by=user
        )
        profile.user.groups.set([Group.objects.get(name=User.AGENTE)])
        return profile

    def crear_supervisor_profile(self, rol=User.GERENTE, user=None):

        if user is None:
            user = self.crear_user_supervisor()

        roles_permitidos = [User.ADMINISTRADOR, User.GERENTE, User.SUPERVISOR, User.REFERENTE]
        assert rol in roles_permitidos, "Rol incorrecto: {0}".format(rol)

        is_administrador = False
        is_customer = False
        if rol == User.ADMINISTRADOR:
            is_administrador = True
            user.groups.set([Group.objects.get(name=User.ADMINISTRADOR)])
        elif rol == User.GERENTE:
            user.groups.set([Group.objects.get(name=User.GERENTE)])
        elif rol == User.REFERENTE:
            is_customer = True
            user.groups.set([Group.objects.get(name=User.REFERENTE)])
        elif rol == User.SUPERVISOR:
            user.groups.set([Group.objects.get(name=User.SUPERVISOR)])

        return SupervisorProfile.objects.create(
            user=user,
            sip_extension=1000 + user.id,
            sip_password="sdsfhdfhfdhfd",
            is_administrador=is_administrador,
            is_customer=is_customer,
        )

    def crear_administrador(self, username='admin_', first_name='', last_name=''):
        """Crea un user administrador con su perfil de supervisor"""
        user = User.objects.create_user(
            username=username,
            email='user_admin@gmail.com',
            password=PASSWORD,
            is_agente=False,
            is_supervisor=True,
            first_name=first_name,
            last_name=last_name,
            borrado=False,
        )
        if username == 'admin_':
            user.username = "admin_" + str(user.id)
        user.save()

        profile = self.crear_supervisor_profile(user=user, rol=User.ADMINISTRADOR)
        profile.save()

        return user

    def crear_lista_datos_extras(self):
        """Devuelve lista con datos extras.

        Lo que devuelve emula los datos extras de un contacto,
        luego de haber sido parseados desde string json.
        """
        return [u'nombre extraño', '15/01/1988', '19:41']

    def crear_contacto(self, bd_contacto, nro_telefonico=None):
        """Crea un contacto asociado a la base de datos de
        contactos especificada.
        - bd_contacto: base de datos de contactos a la que
            pertenece el contacto
        - nro_telefonico: nro telefonico del contacto. Si no se epscifica
            o es None, se genera un numero aleatorio
        """
        nro_telefonico = nro_telefonico or rtel()
        return Contacto.objects.create(
            telefono=nro_telefonico,
            datos=json.dumps(self.crear_lista_datos_extras()),
            bd_contacto=bd_contacto
        )

    def crear_base_datos_contacto(self, cant_contactos=None,
                                  numeros_telefonicos=None, columna_extra=None,
                                  columna_id_externo=None):
        """Crea base datos contacto
        - cant_contactos: cantidad de contactos a crear.
            Si no se especifica, se genera una cantidad
            aleatoria de contactos
        - numeros_telefonicos: lista con numeros de contactos a crear.
            Si se especifica, se ignora el valor `cant_contactos`
        """
        bd_contacto = BaseDatosContacto.objects.create(
            nombre="base-datos-contactos-" + ru())

        metadata = bd_contacto.get_metadata()

        cantidad_de_columnas = 4
        nombres_de_columnas = ['TELEFONO', 'NOMBRE', 'FECHA', 'HORA']
        if columna_extra is not None:
            cantidad_de_columnas += 1
            nombres_de_columnas.append(columna_extra)
        if columna_id_externo is not None:
            cantidad_de_columnas += 1
            nombres_de_columnas.append(columna_id_externo)

        metadata.cantidad_de_columnas = cantidad_de_columnas
        metadata.nombres_de_columnas = nombres_de_columnas
        metadata.columna_con_telefono = 0
        metadata.columnas_con_telefono = [0]
        metadata.columnas_con_hora = [3]
        metadata.columnas_con_fecha = [2]
        metadata.primer_fila_es_encabezado = False
        if columna_id_externo is not None:
            metadata.columna_id_externo = cantidad_de_columnas - 1
        metadata.save()
        bd_contacto.save()

        if numeros_telefonicos is None:
            if cant_contactos is None:
                cant_contactos = random.randint(3, 7)
            for _ in range(0, cant_contactos):
                self.crear_contacto(bd_contacto)
            bd_contacto.cantidad_contactos = cant_contactos

        else:
            for nro_telefonico in numeros_telefonicos:
                self.crear_contacto(
                    bd_contacto, nro_telefonico=nro_telefonico)
            bd_contacto.cantidad_contactos = len(numeros_telefonicos)
            bd_contacto.save()
            return bd_contacto

        bd_contacto.sin_definir = False
        bd_contacto.estado = BaseDatosContacto.ESTADO_DEFINIDA
        bd_contacto.save()

        return bd_contacto

    def crea_calificaciones(self):
        """Crea calificaciones"""
        grupo_calificacion = []
        c = NombreCalificacion.objects.create(nombre="No interesado")
        grupo_calificacion.append(c)
        c = NombreCalificacion.objects.create(nombre="llamar mas tarde")
        grupo_calificacion.append(c)
        c = NombreCalificacion.objects.create(nombre="contestador")
        grupo_calificacion.append(c)
        c = NombreCalificacion.objects.create(nombre="equivocado")
        grupo_calificacion.append(c)
        c = NombreCalificacion.objects.create(nombre="Venta")
        grupo_calificacion.append(c)
        return grupo_calificacion

    def crear_calificacion_campana(self, campana):
        calificaciones = self.crea_calificaciones()
        opciones_calificacion = []
        for calificacion in calificaciones:
            opciones_calificacion.append(
                OpcionCalificacion(campana=campana, nombre=calificacion.nombre))
        OpcionCalificacion.objects.bulk_create(opciones_calificacion)

    def crear_campana(
            self, type, cant_contactos=None, bd_contactos=None,
            columna_extra=None, user=None, **kwargs):
        """Crea una campana en su estado inicial
        - cant_contactos: cant. de contactos a crear para la campaña
            Si es None, se generara un nro. aleatorio de contactos
        - bd_contactos: base de datos de contactos a usar. Si es
            None, se generara una nueva. Si se especifica, entonces
            el valor de `cant_contactos` es ignorado
        - fecha_inicio: fecha de inicio de la campaña. Si es None
            utiliza una por default.
        - fecha_fin: fecha de fin de la campaña. Si es None
            utiliza una por default.
        """

        if not bd_contactos:
            if cant_contactos is not None:
                bd_contactos = self.crear_base_datos_contacto(
                    cant_contactos=cant_contactos, columna_extra=columna_extra)

        # creo usuario supervisor
        if not user:
            user = self.crear_user_supervisor()
            self.crear_supervisor_profile(user=user)

        c = Campana(
            nombre="campaña-" + ru(),
            bd_contacto=bd_contactos,
            type=type,
            reported_by=user,

        )

        c.save()

        self.crear_calificacion_campana(c)

        c.supervisors.add(user)

        c.nombre = "Campaña de PRUEBA - {0}".format(c.id)
        c.save()

        # self.crea_audios_de_campana(c)

        return c

    def crear_campana_dialer(
            self, fecha_inicio=None, fecha_fin=None, cant_contactos=None,
            bd_contactos=None, columna_extra=None,
            user=None, **kwargs):
        """Crea una campana dialer en su estado inicial
        - fecha_inicio: fecha de inicio de la campaña. Si es None
            utiliza una por default.
        - fecha_fin: fecha de fin de la campaña. Si es None
            utiliza una por default.
        """
        if not fecha_inicio or not fecha_fin:
            fecha_inicio = datetime.date.today()
            fecha_fin = fecha_inicio + datetime.timedelta(days=10)

        campana = self.crear_campana(
            Campana.TYPE_DIALER, cant_contactos, bd_contactos, columna_extra, user)
        campana.fecha_inicio = fecha_inicio
        campana.fecha_fin = fecha_fin
        campana.save()

        # Crear cola de campana
        self.crear_queue_dialer(campana)

        return campana

    def crear_campana_manual(
            self, cant_contactos=None, bd_contactos=None, columna_extra=None,
            user=None, **kwargs):
        """Crea una campana manual en su estado inicial
        """

        campana = self.crear_campana(
            Campana.TYPE_MANUAL, cant_contactos, bd_contactos, columna_extra, user)
        self.crear_queue_manual(campana)
        return campana

    def crear_campana_entrante(
            self, cant_contactos=None, bd_contactos=None, columna_extra=None,
            user=None, **kwargs):
        """Crea una campana entrante en su estado inicial
        """

        campana = self.crear_campana(
            Campana.TYPE_ENTRANTE, cant_contactos, bd_contactos, columna_extra,
            user)
        self.crear_queue_entrante(campana)
        return campana

    def crear_queue_dialer(self, campana):
        """
        Crear una cola para una campana dialer
        :param campana: campana para crear una cola
        :return:
        """
        queue = Queue(
            campana=campana,
            name=campana.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=5,
            strategy=Queue.RRMEMORY,
            weight=5,
            wait=5,
            auto_grabacion=True,
            detectar_contestadores=True,
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            audio_para_contestadores=self.crear_arhivo_de_audio()
        )
        queue.save()

    def crear_queue_entrante(self, campana):
        """
        Crear una cola para una campana entrante
        :param campana: campana para crear una cola
        :return:
        """
        queue = Queue(
            campana=campana,
            name=campana.nombre,
            timeout=5,
            retry=5,
            maxlen=5,
            wrapuptime=5,
            servicelevel=5,
            strategy=Queue.RRMEMORY,
            weight=5,
            wait=5,
            auto_grabacion=True,
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            audio_de_ingreso=self.crear_arhivo_de_audio()
        )
        queue.save()

    def crear_queue_manual(self, campana):
        """
        Crear una cola para una campana manual
        :param campana: campana para crear una cola
        :return:
        """
        queue = Queue(
            campana=campana,
            name=campana.nombre,
            maxlen=5,
            wrapuptime=5,
            servicelevel=30,
            strategy='rrmemory',
            eventmemberstatus=True,
            eventwhencalled=True,
            ringinuse=True,
            setinterfacevar=True,
            weight=0,
            wait=120,
            auto_grabacion=True,
            detectar_contestadores=True
        )
        queue.save()

    def crear_actuacion_vigente(self, campana, hora_desde, hora_hasta,
                                domingo=False, lunes=False, martes=False,
                                miercoles=False, jueves=False, viernes=False,
                                sabado=False,):
        """
        Crear una actuacion vigente para una campana dialer
        :param campana: campana para crear una actuacion
        :param dias_semana:
        :return:
        """
        actuacion = ActuacionVigente(
            campana=campana,
            domingo=domingo,
            lunes=lunes,
            martes=martes,
            miercoles=miercoles,
            jueves=jueves,
            viernes=viernes,
            sabado=sabado,
            hora_desde=hora_desde,
            hora_hasta=hora_hasta
        )
        actuacion.save()

    def crear_regla_incidencia(self, campana, estado):
        regla = ReglasIncidencia(
            campana=campana,
            estado=estado,
            intento_max=3,
            reintentar_tarde=150
        )
        regla.save()

    def crear_calificacion_cliente(self, agente, contacto,
                                   opcion_calificacion):
        calificacioncliente = CalificacionCliente(
            agente=agente,
            contacto=contacto,
            opcion_calificacion=opcion_calificacion
        )
        calificacioncliente.save()

    @override_settings(MEDIA_ROOT=_tmpdir())
    def crear_arhivo_de_audio(self):
        original = self.copy_test_resource_to_mediaroot("wavs/8k16bitpcm.wav")

        archivo_de_audio = ArchivoDeAudio(id=1,
                                          descripcion="Audio",
                                          audio_original=original)
        conversor_audio = ConversorDeAudioService()
        conversor_audio.convertir_audio_de_archivo_de_audio_globales(
            archivo_de_audio)
        archivo_de_audio.save = Mock()
        return archivo_de_audio

    def _hacer_miembro(self, agente, campana):
        QueueMemberFactory.create(
            member=agente, queue_name=campana.queue_campana,
            id_campana=campana.get_queue_id_name())


class OMLBaseTest(TestCase, OMLTestUtilsMixin):
    """Clase base para tests"""

    databases = {'default', 'replica'}
    # Deshabilitado por defecto
    ejecutar_actualizar_permisos = False

    def setUp(self, *args, **kwargs):
        super(OMLBaseTest, self).setUp(*args, **kwargs)
        if hasattr(settings, 'DESHABILITAR_MIGRACIONES_EN_TESTS') and \
                settings.DESHABILITAR_MIGRACIONES_EN_TESTS:
            NombreCalificacionFactory(nombre=settings.CALIFICACION_REAGENDA)
            Group.objects.create(name=User.ADMINISTRADOR)
            Group.objects.create(name=User.GERENTE)
            Group.objects.create(name=User.SUPERVISOR)
            Group.objects.create(name=User.REFERENTE)
            Group.objects.create(name=User.AGENTE)
        if self.ejecutar_actualizar_permisos:
            self.actualizar_permisos()

        connections['replica']._orig_cursor = connections['replica'].cursor
        connections['replica'].cursor = connections['default'].cursor

    def tearDown(self):
        connections['replica'].cursor = connections['replica']._orig_cursor
        super(OMLBaseTest, self).tearDown()

    def actualizar_permisos(self):
        """ Ejecuta la actulización de permisos para cada rol. Desactivado por defecto para
            economizar tiempo de testing. Solo es útil si se desea testear permisos"""
        call_command('actualizar_permisos')


class OMLTransaccionBaseTest(TransactionTestCase, OMLTestUtilsMixin):
    """Clase base para tests que involucran transacciones en distintos hilos"""
    databases = {'default', 'replica'}


def default_db_is_postgresql():
    """Devuelve si la DB por default es PostgreSql"""
    return settings.DATABASES['default']['ENGINE'] == \
        'django.db.backends.postgresql_psycopg2'
