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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class ConfiguracionTelefoniaAppConfig(AppConfig):
    name = 'configuracion_telefonia_app'

    def supervision_menu_items(self, request):
        if request.user.get_es_administrador_o_supervisor_normal():
            children = []
            if request.user.get_is_administrador():
                children += [
                    {
                        'label': _('Troncales SIP'),
                        'url': reverse('lista_troncal_sip', args=(1,)),
                    },
                    {
                        'label': _('Rutas entrantes'),
                        'url': reverse('lista_rutas_entrantes', args=(1,)),
                    },
                    {
                        'label': _('Rutas salientes'),
                        'url': reverse('lista_rutas_salientes', args=(1,)),
                    },
                    {
                        'label': _('IVR'),
                        'url': reverse('lista_ivrs', args=(1,)),
                    },
                ]
            children += [
                {
                    'label': _('Grupos horarios'),
                    'url': reverse('lista_grupos_horarios', args=(1,)),
                },
                {
                    'label': _('Validaciones Horarias'),
                    'url': reverse('lista_validaciones_fecha_hora', args=(1,)),
                },
                {
                    'label': _('Identificación de Clientes'),
                    'url': reverse('lista_identificador_cliente', args=(1,)),
                },
                {
                    'label': _('Destinos personalizados'),
                    'url': reverse('lista_destinos_personalizados', args=(1,)),
                },
                {
                    'label': _('Audios'),
                    'icon': 'icon-audio-file',
                    'id': 'menuAllAudios',
                    'children': [
                        {
                            'label': _('Paquetes de Audio de Asterisk'),
                            'url': reverse('adicionar_audios_asterisk'),
                        },
                        {
                            'label': _('Audios Personalizados'),
                            'url': reverse('lista_archivo_audio'),
                        },
                        {
                            'label': _('Listas de Musica de Espera'),
                            'url': reverse('lista_playlist'),
                        },
                    ],
                },
            ]

            return [
                {
                    'label': _('Telefonía'),
                    'icon': 'icon-phone',
                    'id': 'menuTelefonia',
                    'children': children,
                },
            ]
        return None

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'lista_troncal_sip',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'crear_troncal_sip',
             'roles': ['Administrador', ]},
            {'nombre': 'editar_troncal_sip',
             'roles': ['Administrador', ]},
            {'nombre': 'eliminar_troncal_sip',
             'roles': ['Administrador', ]},
            {'nombre': 'lista_rutas_salientes',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'ordenar_rutas_salientes',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'crear_ruta_saliente',
             'roles': ['Administrador', ]},
            {'nombre': 'editar_ruta_saliente',
             'roles': ['Administrador', ]},
            {'nombre': 'eliminar_ruta_saliente',
             'roles': ['Administrador', ]},
            {'nombre': 'lista_rutas_entrantes',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'crear_ruta_entrante',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'editar_ruta_entrante',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'eliminar_ruta_entrante',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'obtener_destinos_tipo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_ivrs',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'crear_ivr',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'editar_ivr',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'eliminar_ivr',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'lista_grupos_horarios',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'crear_grupo_horario',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'editar_grupo_horario',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_grupo_horario',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_validaciones_fecha_hora',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'crear_validacion_fecha_hora',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'editar_validacion_fecha_hora',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_validacion_fecha_hora',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_identificador_cliente',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'crear_identificador_cliente',
             'roles': ['Administrador', ]},
            {'nombre': 'editar_identificador_cliente',
             'roles': ['Administrador', ]},
            {'nombre': 'eliminar_identificador_cliente',
             'roles': ['Administrador', ]},
            {'nombre': 'lista_destinos_personalizados',
             'roles': ['Administrador', ]},
            {'nombre': 'crear_destino_personalizado',
             'roles': ['Administrador', ]},
            {'nombre': 'editar_destino_personalizado',
             'roles': ['Administrador', ]},
            {'nombre': 'eliminar_destino_personalizado',
             'roles': ['Administrador', ]},
            {'nombre': 'adicionar_audios_asterisk',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_playlist',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'crear_playlist',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_playlist',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'editar_playlist',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_musica_de_espera',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
        ]

    informacion_de_permisos = {
        'lista_troncal_sip':
            {'descripcion': _('Ver la lista de Troncales SIP'), 'version': '1.6.2'},
        'crear_troncal_sip':
            {'descripcion': _('Crear un Troncal SIP'), 'version': '1.6.2'},
        'editar_troncal_sip':
            {'descripcion': _('Editar un Troncal SIP'), 'version': '1.6.2'},
        'eliminar_troncal_sip':
            {'descripcion': _('Eliminar un Troncal SIP'), 'version': '1.6.2'},
        'lista_rutas_salientes':
            {'descripcion': _('Ver la lista de Rutas Salientes'), 'version': '1.6.2'},
        'ordenar_rutas_salientes':
            {'descripcion': _('Modificar el orden de las Rutas Salientes'), 'version': '1.6.2'},
        'crear_ruta_saliente':
            {'descripcion': _('Crear una Ruta Saliente'), 'version': '1.6.2'},
        'editar_ruta_saliente':
            {'descripcion': _('Editar una Ruta Saliente'), 'version': '1.6.2'},
        'eliminar_ruta_saliente':
            {'descripcion': _('Eliminar una Ruta Saliente'), 'version': '1.6.2'},
        'lista_rutas_entrantes':
            {'descripcion': _('Ver la lista de Rutas Entrantes'), 'version': '1.6.2'},
        'crear_ruta_entrante':
            {'descripcion': _('Crear una Ruta Entrante'), 'version': '1.6.2'},
        'editar_ruta_entrante':
            {'descripcion': _('Editar una Ruta Entrante'), 'version': '1.6.2'},
        'eliminar_ruta_entrante':
            {'descripcion': _('Eliminar una Ruta Entrante'), 'version': '1.6.2'},
        'obtener_destinos_tipo':
            {'descripcion':
             _('Lista con posibles destinos. Usado en varios formularios de configuración.'),
             'version': '1.6.2'},
        'lista_ivrs':
            {'descripcion': _('Ver la lista de IVRs'), 'version': '1.6.2'},
        'crear_ivr':
            {'descripcion': _('Crear un IVR'), 'version': '1.6.2'},
        'editar_ivr':
            {'descripcion': _('Editar IVR'), 'version': '1.6.2'},
        'eliminar_ivr':
            {'descripcion': _('Eliminar IVR'), 'version': '1.6.2'},
        'lista_grupos_horarios':
            {'descripcion': _('Ver lista de Grupos Horarios'), 'version': '1.6.2'},
        'crear_grupo_horario':
            {'descripcion': _('Crear un Grupo Horario'), 'version': '1.6.2'},
        'editar_grupo_horario':
            {'descripcion': _('Editar un Grupo Horario'), 'version': '1.6.2'},
        'eliminar_grupo_horario':
            {'descripcion': _('Eliminar un Grupo Horario'), 'version': '1.6.2'},
        'lista_validaciones_fecha_hora':
            {'descripcion': _('Ver lista de Validaciones horarias'), 'version': '1.6.2'},
        'crear_validacion_fecha_hora':
            {'descripcion': _('Crear Validacion horaria'), 'version': '1.6.2'},
        'editar_validacion_fecha_hora':
            {'descripcion': _('Editar Validacion horaria'), 'version': '1.6.2'},
        'eliminar_validacion_fecha_hora':
            {'descripcion': _('Eliminar Validacion horaria'), 'version': '1.6.2'},
        'lista_identificador_cliente':
            {'descripcion': _('Ver lista de Identificadores de clientes'), 'version': '1.6.2'},
        'crear_identificador_cliente':
            {'descripcion': _('Crear un Identificador de clientes'), 'version': '1.6.2'},
        'editar_identificador_cliente':
            {'descripcion': _('Editar un Identificador de clientes'), 'version': '1.6.2'},
        'eliminar_identificador_cliente':
            {'descripcion': _('Eliminar un Identificador de clientes'), 'version': '1.6.2'},
        'lista_destinos_personalizados':
            {'descripcion': _('Ver lista de destinos personalizados'), 'version': '1.6.2'},
        'crear_destino_personalizado':
            {'descripcion': _('Crear un Destino personalizado'), 'version': '1.6.2'},
        'editar_destino_personalizado':
            {'descripcion': _('Editar un Destino personalizado'), 'version': '1.6.2'},
        'eliminar_destino_personalizado':
            {'descripcion': _('Eliminar un Destino personalizado'), 'version': '1.6.2'},
        'adicionar_audios_asterisk':
            {'descripcion': _('Menu para instalar paquetes de audio de Asterisk'),
             'version': '1.6.2'},
        'lista_playlist':
            {'descripcion': _('Ver listas de Musicas de espera'), 'version': '1.6.2'},
        'crear_playlist':
            {'descripcion': _('Crear lista de Musicas de espera'), 'version': '1.6.2'},
        'eliminar_playlist':
            {'descripcion': _('Eliminar lista de Musicas de espera'), 'version': '1.6.2'},
        'editar_playlist':
            {'descripcion': _('Editar lista de Musicas de espera'), 'version': '1.6.2'},
        'eliminar_musica_de_espera':
            {'descripcion': _('Eliminar Musica de espera'), 'version': '1.6.2'},
    }
