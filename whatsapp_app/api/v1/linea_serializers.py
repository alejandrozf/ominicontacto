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


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.IntegerField(source='proveedor.id')
    configuration = serializers.JSONField(source='configuracion')
    # destination = serializers.IntegerField(source='destino.id', required=False)
    # destination_type = serializers.IntegerField(source='destino.tipo', required=False)
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


class DestinoDeLineaCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=((DestinoEntrante.CAMPANA, _('Campana')),
                 (DestinoEntrante.MENU_INTERACTIVO_WHATSAPP, _('Menu Interactivo'))))
    data = serializers.JSONField()

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
            if not destino.content_object.whatsapp_habilitado:
                raise serializers.ValidationError({
                    'data': _('Valor incorrecto. La campaña no tiene whatsapp habilitado')})
            self.destino = destino
            return campana_id
        except DestinoEntrante.DoesNotExist:
            raise serializers.ValidationError({
                'data': _('No existe destino con ese id de Campaña')})

    def _validate_menu_interactivo_as_destination(self, menu_data):
        """ Valido que esten bien los datos para crear un menu interactivo """
        self.menu_serializer = MenuInteractivoSerializer(data=menu_data)

        if not self.menu_serializer.is_valid(raise_exception=True):
            raise serializers.ValidationError({
                'destination': _('Valor incorrecto.')})
        return menu_data

    def create(self, validated_data):
        """ En caso de que sea un Menu interactivo debo crearlo """
        if validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            self.create_menu_interactivo()

        return validated_data

    def create_menu_interactivo(self):
        # Si es un menú interactivo debo crearlo:
        menu_data = self.menu_serializer.data
        self.menu = MenuInteractivoWhatsapp(texto_opciones=menu_data['text'],
                                            texto_opcion_incorrecta=menu_data['wrong_answer'],
                                            texto_derivacion=menu_data['success'],
                                            timeout=menu_data['timeout'])
        self.menu.save()
        self.destino = DestinoEntrante.crear_nodo_ruta_entrante(self.menu)
        for option_data in menu_data['options']:
            self.crear_opcion(option_data)

    def crear_opcion(self, option_data):
        campana = Campana.objects.get(id=option_data['destination'])
        destino_campana = DestinoEntrante.get_nodo_ruta_entrante(campana)
        opcion = OpcionDestino.crear_opcion_destino(destino_anterior=self.destino,
                                                    destino_siguiente=destino_campana,
                                                    valor=option_data['value'])
        OpcionMenuInteractivoWhatsapp.objects.create(opcion=opcion,
                                                     descripcion=option_data['description'])

    def update_menu_interactivo(self, instance):
        menu_data = self.menu_serializer.data
        self.destino = instance
        self.menu = instance.content_object
        self.menu.texto_opciones = menu_data['text']
        self.menu.texto_opcion_incorrecta = menu_data['wrong_answer']
        self.menu.texto_derivacion = menu_data['success']
        self.menu.timeout = menu_data['timeout']
        self.menu.save()

        valores = set(instance.destinos_siguientes.values_list('valor', flat=True))
        for option_data in menu_data['options']:
            # Actualizar opciones con valores preexistentes
            if option_data['value'] in valores:
                opcion = instance.destinos_siguientes.get(valor=option_data['value'])
                campana = Campana.objects.get(id=option_data['destination'])
                destino_campana = DestinoEntrante.get_nodo_ruta_entrante(campana)
                opcion.destino_siguiente = destino_campana
                opcion.save()
                opcion.opcion_menu_whatsapp.descripcion = option_data['description']
                opcion.opcion_menu_whatsapp.save()
                valores.remove(option_data['value'])
            else:
                self.crear_opcion(option_data)
        # Elimino las opciones que no tienen valor
        instance.destinos_siguientes.filter(valor__in=valores).delete()

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
            self.create_menu_interactivo()
        # Cambio destino campaña por Menu Interactivo:
        if instance.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP \
                and validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            self.update_menu_interactivo(instance)

        return validated_data

    def serialize_data(self):
        serialize_data = {
            'type': self.data['type']
        }
        if self.data['type'] == DestinoEntrante.CAMPANA:
            serialize_data['id'] = self.data['data']
        elif self.data['type'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            serialize_data.update(self.menu_serializer.data)
            serialize_data['id'] = self.menu.id
        else:
            raise Exception('Se obtuvo un type inválido')
        return serialize_data


class OpcionMenuSerializer(serializers.Serializer):
    value = serializers.CharField()
    description = serializers.CharField(source='descripcion')
    destination = serializers.PrimaryKeyRelatedField(
        queryset=Campana.objects.filter(whatsapp_habilitado=True))


class MenuInteractivoSerializer(serializers.Serializer):
    text = serializers.CharField()
    wrong_answer = serializers.CharField()
    success = serializers.CharField()
    timeout = serializers.IntegerField(min_value=0)
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

    def to_representation(self, value):
        representation = {
            'type': value.tipo,
            'id': value.content_object.id,
        }
        if value.tipo == DestinoEntrante.CAMPANA:
            representation['data'] = value.content_object.id
        elif value.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            menu = value.content_object
            menu_representation = {
                'text': menu.texto_opciones,
                'wrong_answer': menu.texto_opcion_incorrecta,
                'success': menu.texto_derivacion,
                'timeout': menu.timeout,
                'options': []
            }
            for opcion in value.destinos_siguientes.all():
                menu_representation['options'].append({
                    'id': opcion.id,
                    'destination': opcion.destino_siguiente.content_object.id,
                    'value': opcion.valor,
                    'description': opcion.opcion_menu_whatsapp.descripcion,
                })
            representation['data'] = menu_representation
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
    destination_type = serializers.IntegerField(source='destino.tipo', required=False)
    destination = DestinoEntranteRelatedField(source='destino', read_only=True)
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
