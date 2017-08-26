# -*- coding: utf-8 -*-

"""Metodos utilitarios para ser reutilizados en los distintos
módulos de tests.
"""

from __future__ import unicode_literals

import os
import random

from django.test import TestCase
from ominicontacto_app.models import (
    User, AgenteProfile, Modulo, Grupo, SupervisorProfile
)


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


class OMLBaseTest(TestCase, OMLTestUtilsMixin):
    """Clase base para tests"""


def default_db_is_postgresql():
    """Devuelve si la DB por default es PostgreSql"""
    return settings.DATABASES['default']['ENGINE'] == \
        'django.db.backends.postgresql_psycopg2'
