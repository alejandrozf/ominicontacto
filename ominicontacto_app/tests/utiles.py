# -*- coding: utf-8 -*-

"""Metodos utilitarios para ser reutilizados en los distintos
módulos de tests.
"""

from __future__ import unicode_literals

import os
import random

from django.test import TestCase
from ominicontacto_app.models import (
    User, AgenteProfile, Modulo, Grupo, SupervisorProfile, Contacto,
    BaseDatosContacto
)


def ru():
    """Devuelve random UUID"""
    return str(uuid.uuid4())


def rtel():
    """Devuelve nro telefonico aleatorio"""
    return unicode(random.randint(1140000000000000,
                                  1149999999999999))


class OMLTestUtilsMixin(object):

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

    def crear_user_agente(self):
        """Crea un user"""
        return User.objects.create_user(
            username='user_test_agente',
            email='user_agente@gmail.com',
            password='admin123',
            is_agente=True
        )

    def crear_user_supervisor(self):
        """Crea un user"""
        return User.objects.create_user(
            username='user_test_supervisor',
            email='user_supervisor@gmail.com',
            password='admin123',
            is_supervisor=True
        )

    def crear_agente_profile(self, user):
        grupo = Grupo.objects.create(nombre="grupo_test", auto_unpause=0)
        return AgenteProfile.objects.create(
            user=user,
            sip_extension=AgenteProfile.objects.obtener_ultimo_sip_extension(),
            sip_password="sdsfhdfhfdhfd",
            grupo=grupo,
            reported_by=user
        )

    def crear_supervisor_profile(self, user):
        return SupervisorProfile.objects.create(
            user=user,
            sip_extension=SupervisorProfile.objects.
            obtener_ultimo_sip_extension(),
            sip_password="sdsfhdfhfdhfd",
        )

    def crear_lista_datos_extras(self):
        """Devuelve lista con datos extras.

        Lo que devuelve emula los datos extras de un contacto,
        luego de haber sido parseados desde string json.
        """
        return [ u'nombre extraño', '15/01/1988', '19:41']

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
        numeros_telefonicos=None, columna_extra=None):
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

        if columna_extra is None:
            metadata.cantidad_de_columnas = 4
            metadata.nombres_de_columnas = ['TELEFONO', 'NOMBRE', 'FECHA',
                                            'HORA']
        else:
            metadata.cantidad_de_columnas = 5
            metadata.nombres_de_columnas = ['TELEFONO', 'NOMBRE', 'FECHA',
                                            'HORA', columna_extra]

        metadata.columna_con_telefono = 0
        metadata.columnas_con_hora = [3]
        metadata.columnas_con_fecha = [2]
        metadata.primer_fila_es_encabezado = False
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

    def crear_campana(self, fecha_inicio=None, fecha_fin=None,
        cant_contactos=None, bd_contactos=None, columna_extra=None,
                      calificacion_campana=None, **kwargs):
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

        if not fecha_inicio or not fecha_fin:
            fecha_inicio = datetime.date.today()
            fecha_fin = fecha_inicio + datetime.timedelta(days=10)

        c = Campana(
            nombre="campaña-" + ru(),

            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,

            bd_contacto=bd_contactos,
            # audio_original="test/audio/original.wav",
            # audio_asterisk="test/audio/for-asterisk.wav",
        )
        c.save()

        c.nombre = "Campaña de PRUEBA - {0}".format(c.id)
        c.save()

       # self.crea_audios_de_campana(c)

        return c


class OMLBaseTest(TestCase, OMLTestUtilsMixin):
    """Clase base para tests"""


def default_db_is_postgresql():
    """Devuelve si la DB por default es PostgreSql"""
    return settings.DATABASES['default']['ENGINE'] == \
        'django.db.backends.postgresql_psycopg2'
