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

from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):

    def handle(self, *args, **options):
        self._verificar_permisos_en_urls()

    def _verificar_permisos_en_urls(self):

        excepciones = {
            'ominicontacto_app': [
                'index', 'login', 'acerca', 'view_blanco',
                # Deprecated urls?
                'chat_create', 'nueva_mensaje_chat', 'agenda_agente_list', 'agenda_nuevo'],
            'api_app': [
                'api_login', 'api'],
        }

        print('Este script sólo verificará urls definidas con un name.')
        for app in apps.get_app_configs():
            if hasattr(app, 'configuraciones_de_permisos'):
                modulo = app.module.__name__
                print('Verificando: ' + modulo)

                ignorar = set()
                if modulo in excepciones:
                    ignorar = set(excepciones[modulo])
                urlpatterns = app.module.urls.urlpatterns
                configuraciones_sin_url = set()

                url_names = set()
                for url in urlpatterns:
                    if hasattr(url, 'name') and url.name is not None:
                        url_names.add(url.name)
                    elif hasattr(url, 'url_patterns') and modulo == 'api_app':
                        resolver_urls = self._obtener_api_app_resolver_url_names(url.url_patterns)
                        url_names = url_names.union(resolver_urls)
                url_names -= ignorar

                for configuracion in app.configuraciones_de_permisos():
                    nombre = configuracion['nombre']
                    if nombre not in ignorar:
                        if nombre in url_names:
                            url_names.remove(nombre)
                        else:
                            configuraciones_sin_url.add(nombre)

                if configuraciones_sin_url:
                    print('  Configuraciones sin URL:')
                    print('    ' + str(configuraciones_sin_url))
                if url_names:
                    print('  Urls sin permisos')
                    print('    ' + str(url_names))
                if not (configuraciones_sin_url or url_names):
                    print('  App sin permisos sin url o urls sin permisos.')
                print('----------------------------------------------------------')

    def _obtener_api_app_resolver_url_names(self, urlpatterns):
        url_names = set()
        for url in urlpatterns:
            if hasattr(url, 'name') and url.name is not None:
                # Elimino el sufijo automático de rest_framework
                name = url.name
                if url.name.find('-') > -1:
                    name = name[:name.find('-')]
                url_names.add(name)
        return url_names
