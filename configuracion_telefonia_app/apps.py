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
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class ConfiguracionTelefoniaAppConfig(AppConfig):
    name = 'configuracion_telefonia_app'

    def supervision_menu_items(self, request, permissions):
        items = []
        if 'lista_troncal_sip' in permissions:
            items.append({
                'label': _('Troncales SIP'),
                'url': reverse('lista_troncal_sip', args=(1,)),
            })
        if 'lista_rutas_entrantes' in permissions:
            items.append({
                'label': _('Rutas entrantes'),
                'url': reverse('lista_rutas_entrantes'),
            })
        if 'lista_rutas_salientes' in permissions:
            items.append({
                'label': _('Rutas salientes'),
                'url': reverse('lista_rutas_salientes')
            })
        if 'lista_ivrs' in permissions:
            items.append({
                'label': _('IVR'),
                'url': reverse('lista_ivrs')
            })
        if 'lista_grupos_horarios' in permissions:
            items.append({
                'label': _('Grupos horarios'),
                'url': reverse('lista_grupos_horarios')
            })
        if 'lista_validaciones_fecha_hora' in permissions:
            items.append({
                'label': _('Validaciones Horarias'),
                'url': reverse('lista_validaciones_fecha_hora', args=(1,))
            })
        if 'lista_identificador_cliente' in permissions:
            items.append({
                'label': _('Identificación de Clientes'),
                'url': reverse('lista_identificador_cliente', args=(1,))
            })
        if 'lista_destinos_personalizados' in permissions:
            items.append({
                'label': _('Destinos personalizados'),
                'url': reverse('lista_destinos_personalizados', args=(1,))
            })

        opciones_avanzadas = []
        if ('ajustar_configuracion_amd' in permissions):
            opciones_avanzadas.append({
                'label': _('AMD'),
                'url': reverse('ajustar_configuracion_amd', args=(1,))
            })

        if ('ajustar_formato_grabaciones' in permissions):
            opciones_avanzadas.append({
                'label': _('Esquema grabaciones'),
                'url': reverse('ajustar_formato_grabaciones', args=(1,))
            })
        if opciones_avanzadas:
            items.append({
                'label': _('Configuración avanzada'),
                'icon': 'icon-audio-file',
                'id': 'menuConfiguracionAvanzada',
                'children': opciones_avanzadas
            })

        audios = []
        if 'adicionar_audios_asterisk' in permissions:
            audios.append({
                'label': _('Paquetes de Audio de Asterisk'),
                'url': reverse('adicionar_audios_asterisk')
            })
        if 'lista_archivo_audio' in permissions:
            audios.append({
                'label': _('Audios Personalizados'),
                'url': reverse('lista_archivo_audio')
            })
        if 'lista_playlist' in permissions:
            audios.append({
                'label': _('Listas de Musica de Espera'),
                'url': reverse('lista_playlist', args=(1, ))
            })
        if audios:
            items.append({
                'label': _('Audios'),
                'icon': 'icon-audio-file',
                'id': 'menuAllAudios',
                'children': audios
            })

        if items:
            return [
                {
                    'order': 700,
                    'label': _('Telefonía'),
                    'icon': 'icon-phone',
                    'id': 'menuTelefonia',
                    'children': items,
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
            {'nombre': 'lista_rutas_entrantes',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'obtener_destinos_tipo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_ivrs',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'lista_grupos_horarios',
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
            {'nombre': 'ajustar_configuracion_amd',
             'roles': ['Administrador', ]},
            {'nombre': 'ajustar_formato_grabaciones',
             'roles': ['Administrador', ]},
        ]

    informacion_de_permisos = {
        'lista_troncal_sip':
            {'descripcion': _('Ver la lista de Troncales SIP'), 'version': '1.7.0'},
        'crear_troncal_sip':
            {'descripcion': _('Crear un Troncal SIP'), 'version': '1.7.0'},
        'editar_troncal_sip':
            {'descripcion': _('Editar un Troncal SIP'), 'version': '1.7.0'},
        'eliminar_troncal_sip':
            {'descripcion': _('Eliminar un Troncal SIP'), 'version': '1.7.0'},
        'lista_rutas_salientes':
            {'descripcion': _('Ver la lista de Rutas Salientes'), 'version': '1.7.0'},
        'lista_rutas_entrantes':
            {'descripcion': _('Ver la lista de Rutas Entrantes'), 'version': '1.7.0'},
        'obtener_destinos_tipo':
            {'descripcion':
             _('Lista con posibles destinos. Usado en varios formularios de configuración.'),
             'version': '1.7.0'},
        'lista_ivrs':
            {'descripcion': _('Ver la lista de IVRs'), 'version': '1.7.0'},
        'lista_grupos_horarios':
            {'descripcion': _('Ver lista de Grupos Horarios'), 'version': '1.7.0'},
        'lista_validaciones_fecha_hora':
            {'descripcion': _('Ver lista de Validaciones horarias'), 'version': '1.7.0'},
        'crear_validacion_fecha_hora':
            {'descripcion': _('Crear Validacion horaria'), 'version': '1.7.0'},
        'editar_validacion_fecha_hora':
            {'descripcion': _('Editar Validacion horaria'), 'version': '1.7.0'},
        'eliminar_validacion_fecha_hora':
            {'descripcion': _('Eliminar Validacion horaria'), 'version': '1.7.0'},
        'lista_identificador_cliente':
            {'descripcion': _('Ver lista de Identificadores de clientes'), 'version': '1.7.0'},
        'crear_identificador_cliente':
            {'descripcion': _('Crear un Identificador de clientes'), 'version': '1.7.0'},
        'editar_identificador_cliente':
            {'descripcion': _('Editar un Identificador de clientes'), 'version': '1.7.0'},
        'eliminar_identificador_cliente':
            {'descripcion': _('Eliminar un Identificador de clientes'), 'version': '1.7.0'},
        'lista_destinos_personalizados':
            {'descripcion': _('Ver lista de destinos personalizados'), 'version': '1.7.0'},
        'crear_destino_personalizado':
            {'descripcion': _('Crear un Destino personalizado'), 'version': '1.7.0'},
        'editar_destino_personalizado':
            {'descripcion': _('Editar un Destino personalizado'), 'version': '1.7.0'},
        'eliminar_destino_personalizado':
            {'descripcion': _('Eliminar un Destino personalizado'), 'version': '1.7.0'},
        'adicionar_audios_asterisk':
            {'descripcion': _('Menu para instalar paquetes de audio de Asterisk'),
             'version': '1.7.0'},
        'lista_playlist':
            {'descripcion': _('Ver listas de Musicas de espera'), 'version': '1.7.0'},
        'crear_playlist':
            {'descripcion': _('Crear lista de Musicas de espera'), 'version': '1.7.0'},
        'eliminar_playlist':
            {'descripcion': _('Eliminar lista de Musicas de espera'), 'version': '1.7.0'},
        'editar_playlist':
            {'descripcion': _('Editar lista de Musicas de espera'), 'version': '1.7.0'},
        'eliminar_musica_de_espera':
            {'descripcion': _('Eliminar Musica de espera'), 'version': '1.7.0'},
        'ajustar_configuracion_amd':
            {'descripcion': _('Ajustar configuración AMD'), 'version': '1.12.0'},
        'ajustar_formato_grabaciones':
            {'descripcion': _('Ajustar configuración AMD'), 'version': '1.12.0'},
    }
