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

from collections import ChainMap
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db import models


class PermisoOMLManager(models.Manager):
    def get_queryset(self):
        return super(PermisoOMLManager, self).\
            get_queryset().filter(content_type__model='permiso_oml')


class PermisoOML(Permission):
    """No esta asociado a ningun Model"""

    objects = PermisoOMLManager()

    class Meta:
        proxy = True
        verbose_name = "permiso_oml"

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        self.content_type = ct
        super(PermisoOML, self).save(*args)

    @property
    def descripcion(self):
        return DESCRIPCIONES.get(self.codename, self.codename)

    @property
    def version(self):
        return VERSIONES.get(self.codename, '1.0.0')


def cargar_descripciones():
    # Iterar por todas las apps instaladas.
    descripciones_de_apps = []
    for app in apps.get_app_configs():
        if hasattr(app, 'descripciones'):
            descripciones_de_apps.append(app.descripciones)
    return dict(ChainMap(*descripciones_de_apps))


def cargar_descripciones_y_versiones():
    # Iterar por todas las apps instaladas.
    descripciones = {}
    versiones = {}
    for app in apps.get_app_configs():
        if hasattr(app, 'informacion_de_permisos'):
            for nombre, informacion in app.informacion_de_permisos.items():
                descripciones[nombre] = informacion.get('descripcion', nombre)
                versiones[nombre] = informacion.get('version', '1.0.0')
    return descripciones, versiones


DESCRIPCIONES, VERSIONES = cargar_descripciones_y_versiones()
