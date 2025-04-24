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

from django.utils.translation import ugettext as _
from rest_framework import serializers
from configuracion_telefonia_app.models import DestinoEntrante, GrupoHorario, OpcionDestino
from ominicontacto_app.models import Campana
from whatsapp_app.models import ConfiguracionProveedor, Linea
from whatsapp_app.models import (
    PlantillaMensaje, MenuInteractivoWhatsapp, OpcionMenuInteractivoWhatsapp)
import json


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.IntegerField(source='proveedor.id')
    status = serializers.CharField()
    configuration = serializers.JSONField(source='configuracion')
    schedule = serializers.IntegerField(source='horario.id', required=False)
    welcome_message = serializers.IntegerField(source='mensaje_bienvenida.id', required=False)
    farewell_message = serializers.IntegerField(source='mensaje_despedida.id', required=False)
    afterhours_message = serializers.IntegerField(source='mensaje_fueradehora.id', required=False)


class LineaCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.PrimaryKeyRelatedField(
        queryset=ConfiguracionProveedor.objects.all(), source='proveedor')
    configuration = serializers.JSONField(source='configuracion')
    schedule = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=GrupoHorario.objects.all(), required=False, source='horario')
    welcome_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_bienvenida')
    farewell_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_despedida')
    afterhours_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_fueradehora')

    class Meta:
        model = Linea
        fields = [
            'id',
            'name',
            'number',
            'provider',
            'configuration',
            'schedule',
            'welcome_message',
            'farewell_message',
            'afterhours_message'
        ]

    def validate(self, data):
        proveedor = data.get('proveedor')
        configuracion = data.get('configuracion')
        self.validar_configuracion(proveedor, configuracion)
        return data

    def validar_configuracion(self, proveedor, configuracion):
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'app_name' not in configuracion\
                    or 'app_id' not in configuracion:
                raise serializers.ValidationError({
                    'configuration': _('Configuración incorrecta para el tipo de proveedor')})
            if Linea.objects.filter(configuracion__app_id=configuracion['app_id']).exists():
                raise serializers.ValidationError({
                    'app_id': _('Ya existe una Linea con ese App ID')})
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'app_id' not in configuracion\
                    or 'token_de_verificacion' not in configuracion:
                raise serializers.ValidationError({
                    'configuration': _('Configuración incorrecta para el tipo de proveedor')})


class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        try:
            if isinstance(data, int):
                json_data = data
            else:
                json_data = {}
                json_data = json.loads(json.dumps(data))
        except Exception:
            pass
        finally:
            return json_data

    def to_representation(self, value):
        return value


class DestinoDeLineaCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=((DestinoEntrante.CAMPANA, _('Campana')),
                 (DestinoEntrante.MENU_INTERACTIVO_WHATSAPP, _('Menu Interactivo'))))
    data = JSONSerializerField()
    id_tmp = serializers.IntegerField(required=False)

    def validate_data(self, destination):
        destination_type = self.initial_data.get('type')
        # Si el destino es de una campaña, valido que exista
        if destination_type == DestinoEntrante.CAMPANA:
            return self._validate_campana_as_destination(destination)
        # Si el tipo es Menu Interactivo debo crear el Menu y sus opciones
        return self._validate_menu_interactivo_as_destination(destination)

    def _validate_campana_as_destination(self, campana_id):
        """ Valido que exista el destino de la campaña y lo guardo en self.destino """
        if not isinstance(campana_id, int):
            raise serializers.ValidationError({
                'data': _('Valor incorrecto. Debe ser un id')})
        try:
            destino = DestinoEntrante.objects.get(tipo=DestinoEntrante.CAMPANA,
                                                  object_id=campana_id)
            destino_lineas = destino.lineas.all()
            if 'line' in self.context:
                destino_lineas = destino_lineas.exclude(id=self.context['line'].id)
            if destino_lineas.exists():  # verificar que la campnana no la este usando otra linea.
                raise serializers.ValidationError({
                    'data': _('Valor incorrecto. Esta campaña esta siendo usada por otra línea')})
            self.destino = destino
            return campana_id
        except DestinoEntrante.DoesNotExist:
            raise serializers.ValidationError({
                'data': _('No existe destino con ese id de Campaña')})

    def _validate_menu_interactivo_as_destination(self, menu_data):
        """ Valido que esten bien los datos para crear un menu interactivo """
        self.menu_serializer = MenuInteractivoSerializer(data=menu_data, many=True)
        if not self.menu_serializer.is_valid(raise_exception=True):
            raise serializers.ValidationError({
                'destination': _('Valor incorrecto.')})
        return menu_data

    def create(self, validated_data):
        """ En caso de que sea un Menu interactivo debo crearlo """
        if validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            self.create_menu_interactivo(validated_data)
        return validated_data

    def create_menu_interactivo(self, validated_data):
        # Si es un menú interactivo debo crearlo:
        line = None
        if 'line' in self.context:
            line = self.context['line']
        list_menu_data = validated_data['data']
        destino_whith_options = []
        for menu_data in list_menu_data:
            menu = MenuInteractivoWhatsapp(menu_header=menu_data['menu_header'],
                                           menu_body=menu_data['menu_body'],
                                           menu_footer=menu_data['menu_footer']
                                           if 'menu_footer' in menu_data else '',
                                           menu_button=menu_data['menu_button'],
                                           texto_opcion_incorrecta=menu_data['wrong_answer'],
                                           texto_derivacion=menu_data['success'],
                                           timeout=0,
                                           line=line
                                           )
            menu.save()
            destino = DestinoEntrante.crear_nodo_ruta_entrante(menu)
            opcions = {
                "id_temp": menu_data['id_tmp'],
                'destino_anterior': destino,
                "opcions": menu_data['options']

            }
            if menu_data['id_tmp'] == validated_data['id_tmp']:
                self.destino = destino
            destino_whith_options.append(opcions)
            menu_data['id'] = menu.id
        self.crear_opcions(destino_whith_options)

    def crear_opcions(self, destino_whith_options):
        for object_dict in destino_whith_options:
            for option_data in object_dict['opcions']:
                if option_data['type_option'] == DestinoEntrante.CAMPANA:
                    campana = Campana.objects.get(id=option_data['destination'])
                    destino_siguiente = DestinoEntrante.get_nodo_ruta_entrante(campana)
                else:
                    destino_siguiente = self.find_destination(
                        destino_whith_options, option_data['destination'])
                    if destino_siguiente\
                            and object_dict['destino_anterior'].id in destino_siguiente.\
                            destinos_siguientes.values_list('destino_siguiente', flat=True).\
                            distinct():
                        raise serializers.ValidationError({
                            'data': _('No puede existir dependencias recursiva entre menus')})
                if destino_siguiente:
                    option_data['destination'] = destino_siguiente.content_object.id
                    opcion = OpcionDestino.crear_opcion_destino(
                        destino_anterior=object_dict['destino_anterior'],
                        destino_siguiente=destino_siguiente,
                        valor=option_data['value'])
                    OpcionMenuInteractivoWhatsapp.objects.create(
                        opcion=opcion,
                        descripcion=option_data['description'] if 'description'
                                                                  in option_data else "")

    def update_opcions(self, destino_whith_options):
        # TODO NO SE USA ACTUALMENTE IMPLEMENTACION INCOMPLETA
        for object_dict in destino_whith_options:
            for option_data in object_dict['opcions']:
                if not option_data['type_option'] == DestinoEntrante.CAMPANA:
                    campana = Campana.objects.get(id=option_data['destination'])
                    destino_siguiente = DestinoEntrante.get_nodo_ruta_entrante(campana)
                else:
                    destino_siguiente = self.find_destination(
                        destino_whith_options, option_data['destination'])
            return destino_siguiente

    def find_destination(self, destino_whith_options, value):
        for object_dict in destino_whith_options:
            if object_dict['id_temp'] == value:
                return object_dict['destino_anterior']

    def update_menu_interactivo(self, instance, validated_data):
        list_menu_data = validated_data['data']
        destino_whith_options = []
        for menu_data in list_menu_data:
            menu = MenuInteractivoWhatsapp.objects.get(pk=menu_data['id'])
            menu.menu_header = menu_data['menu_header']
            menu.menu_body = menu_data['temenu_bodyxt']
            menu.menu_body = menu_data['menu_body']
            menu.menu_button = menu_data['menu_button']
            menu.texto_opcion_incorrecta = menu_data['wrong_answer']
            menu.texto_derivacion = menu_data['success']
            menu.timeout = menu_data['timeout']
            menu.save()
            opcions = {
                "id": menu_data['id'],
                'destino_anterior': instance,
                "opcions": menu_data['options']
            }
            destino_whith_options.append(opcions)
        self.update_opcions(destino_whith_options)

    def borrar_destino_sobrante(self, destino_previo, destino):
        # Si pasa de un menu a una campaña, borro el menu, su destino y sus componentes asociados.
        if destino_previo and destino_previo.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP \
                and destino.tipo == DestinoEntrante.CAMPANA:
            destino_previo.delete()
            destino_previo.content_object.delete()

    def update(self, instance, validated_data):
        # Cambio destino de una campaña por otro
        if instance.tipo == validated_data['type'] == DestinoEntrante.CAMPANA:
            pass
        # Cambio destino Menu Interactivo por Campaña:
        if instance.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP \
                and validated_data['type'] == DestinoEntrante.CAMPANA:
            pass
            # Se debe borrar después de guardar la Linea por la referencia al destino anterior.
            # self.borrar_destino_sobrante(instance, self.destino)
        # Cambio destino campaña por Menu Interactivo:
        if instance.tipo == DestinoEntrante.CAMPANA \
                and validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            self.create_menu_interactivo(validated_data)
        # Cambio destino campaña por Menu Interactivo:
        if instance.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP \
                and validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            self.update_menu_interactivo(instance, validated_data)

        return validated_data


class OpcionMenuSerializer(serializers.BaseSerializer):

    def to_internal_value(self, data):
        value = data.get('value')
        destination = data.get('destination')
        description = data.get('description')
        type_option = data.get('type_option')

        if not destination:
            raise serializers.ValidationError({
                'destination': 'This field is required.'
            })
        if not value:
            raise serializers.ValidationError({
                'value': 'This field is required.'
            })
        return {
            'destination': destination,
            'value': value,
            'description': description,
            'type_option': type_option
        }

    def to_representation(self, instance):
        representation = {
            'value': instance["value"],
            'description': instance["description"],
            'type_option': instance["type_option"],
            'destination': instance["destination"]
        }
        if instance["type_option"] == DestinoEntrante.CAMPANA:
            representation['destination_name'] = instance.nombre
        elif instance["type_option"] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            destination = DestinoDeLineaCreateSerializer(data=instance["destination"])
            destination.is_valid(raise_exception=True)
            representation['destination'] = destination.data
            representation['destination_name'] = destination.name
        print('representation', representation)
        return representation


class MenuInteractivoSerializer(serializers.Serializer):
    id_tmp = serializers.IntegerField(required=False)
    is_main = serializers.BooleanField(required=False, default=True)
    menu_header = serializers.CharField(max_length=60)
    menu_body = serializers.CharField(max_length=1024)
    menu_footer = serializers.CharField(required=False, allow_blank=True, max_length=60)
    menu_button = serializers.CharField(max_length=20)
    wrong_answer = serializers.CharField()
    success = serializers.CharField()
    timeout = serializers.IntegerField(min_value=0, required=False)
    options = OpcionMenuSerializer(many=True)

    def validate_options(self, options):
        # Verifico que no se repitan opciones:
        if len(options) > len(set([option['value'] for option in options])):
            raise serializers.ValidationError({
                'options': _('El valor de las opciones no puede repetirse')})
        if len(options) > 10:
            raise serializers.ValidationError({
                'options': _('No pueden definirse más de 10 opciones')})
        return options


class DestinoEntranteRelatedField(serializers.RelatedField):

    def _menu_representation(self, value, data_list):
        menu = value.content_object
        menu_representation = {
            'id': menu.id,
            'id_tmp': menu.id,
            'is_main': menu.is_main,
            'menu_header': menu.menu_header if menu.menu_header else '',
            'menu_body': menu.menu_body,
            'menu_footer': menu.menu_footer if menu.menu_footer else '',
            'menu_button': menu.menu_button,
            'wrong_answer': menu.texto_opcion_incorrecta,
            'success': menu.texto_derivacion,
            'timeout': 0,
            'options': []
        }
        for opcion in value.destinos_siguientes.all():
            menu_representation['options'].append({
                'id': opcion.id,
                'type_option': opcion.destino_siguiente.tipo,
                'destination': opcion.destino_siguiente.content_object.id,
                'value': opcion.valor,
                'description': opcion.opcion_menu_whatsapp.descripcion,
                'destination_name': opcion.destino_siguiente.content_object.nombre
            })
            if opcion.destino_siguiente.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                if not [item for item in data_list
                        if item['id'] == opcion.destino_siguiente.content_object.id]:
                    data_list.insert(
                        0, self._menu_representation(opcion.destino_siguiente, data_list))
        return menu_representation

    def to_representation(self, line):
        value = line.destino
        representation = {
            'type': value.tipo,
            'id': value.content_object.id,
        }
        if value.tipo == DestinoEntrante.CAMPANA:
            representation['data'] = value.content_object.id
        elif value.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            data_list = []
            menu_representation = self._menu_representation(value, data_list)
            data_list.insert(0, menu_representation)
            try:
                menu_used_list = [menu.get('id') for menu in data_list if 'id' in menu]
                orphan_menus =\
                    MenuInteractivoWhatsapp.objects.filter(line=line).exclude(
                        id__in=menu_used_list)
                for menu in orphan_menus:
                    menu_used_list = [menu.get('id') for menu in data_list if 'id' in menu]
                    if menu.id not in menu_used_list:
                        destino = DestinoEntrante.objects.filter(
                            object_id=menu.id,
                            tipo=DestinoEntrante.MENU_INTERACTIVO_WHATSAPP).last()
                        menu_representation = self._menu_representation(destino, data_list)
                        data_list.append(menu_representation)
                representation['data'] = data_list
            except Exception as e:
                print(e)
                pass
        else:
            raise Exception('Tipo de destino incorrecto')
        return representation


class LineaRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.IntegerField(source='proveedor.id')
    configuration = serializers.JSONField(source='configuracion')
    schedule = serializers.IntegerField(source='horario.id', required=False)
    destination = DestinoEntranteRelatedField(source='*', read_only=True)
    welcome_message = serializers.IntegerField(source='mensaje_bienvenida.id', required=False)
    farewell_message = serializers.IntegerField(source='mensaje_despedida.id', required=False)
    afterhours_message = serializers.IntegerField(source='mensaje_fueradehora.id', required=False)


class UpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.PrimaryKeyRelatedField(
        queryset=ConfiguracionProveedor.objects.all(), source='proveedor')
    configuration = serializers.JSONField(source='configuracion')
    schedule = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=GrupoHorario.objects.all(),
        required=False, source='horario')
    welcome_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_bienvenida')
    farewell_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_despedida')
    afterhours_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_fueradehora')

    class Meta:
        model = Linea
        fields = [
            'id',
            'name',
            'number',
            'provider',
            'configuration',
            'schedule',
            'welcome_message',
            'farewell_message',
            'afterhours_message'
        ]

    def validate(self, data):
        proveedor = data.get('proveedor')
        configuracion = data.get('configuracion')
        if proveedor:
            if not configuracion:
                if self.instance.proveedor.tipo_proveedor != proveedor.tipo_proveedor:
                    raise serializers.ValidationError({
                        'configuration': _('Debe indicar una configuración de proveedor.')
                    })
            else:
                self.validar_configuracion(proveedor, configuracion)
        elif configuracion:
            raise serializers.ValidationError({
                'provider': _('Debe indicar un proveedor.')
            })
        return data

    def validar_configuracion(self, proveedor, configuracion):
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'app_name' not in configuracion\
                    or 'app_id' not in configuracion:
                raise serializers.ValidationError({
                    'configuration': _('Configuración incorrecta para el tipo de proveedor')})
            otras_lineas = Linea.objects.exclude(id=self.instance.id)
            if otras_lineas.filter(configuracion__app_id=configuracion['app_id']).exists():
                raise serializers.ValidationError({
                    'app_id': _('Ya existe una Linea con ese App ID')})
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'app_id' not in configuracion\
                    or 'token_de_verificacion' not in configuracion:
                raise serializers.ValidationError({
                    'configuration': _('Configuración incorrecta para el tipo de proveedor')})
