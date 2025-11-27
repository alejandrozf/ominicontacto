import json
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from configuracion_telefonia_app.models import (DestinoEntrante, OpcionDestino,
                                                GrupoHorario, PlantillaMensaje)
from ominicontacto_app.models import Campana

from facebook_meta_app.models import (PaginaMetaFacebook, MenuInteractivoMessengerMetaApp,
                                      OpcionMenuInteractivoMessengerMetaApp,
                                      ConfiguracionMetaFacebookCampana)
from facebook_meta_app.api.utils import HttpResponseStatus, get_response_data


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
        elif instance["type_option"] == DestinoEntrante.CLOSING_MESSAGE:
            representation['destination_name'] = instance.nombre
        elif instance["type_option"] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            destination = DestinoDePaginaCreateSerializer(data=instance["destination"])
            destination.is_valid(raise_exception=True)
            representation['destination'] = destination.data
            representation['destination_name'] = destination.name
        return representation


class MenuInteractivoSerializer(serializers.Serializer):
    id_tmp = serializers.IntegerField(required=False)
    is_main = serializers.BooleanField(required=False, default=True)
    menu_header = serializers.CharField(max_length=60)
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


class DestinoDePaginaCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=((DestinoEntrante.CAMPANA, _('Campana')),
                 (DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP, _('Menu Interactivo'))))
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
        print('campana_id >>>', campana_id)
        if not isinstance(campana_id, int):
            raise serializers.ValidationError({
                'data': _('Valor incorrecto. Debe ser un id')})
        try:
            destino = DestinoEntrante.objects.get(tipo=DestinoEntrante.CAMPANA,
                                                  object_id=campana_id)
            print('destino found >>>', destino)
            destino_pages = destino.pages.all()
            if 'page' in self.context:
                destino_pages = destino_pages.exclude(id=self.context['page'].id)
            if destino_pages.exists():  # verificar que la campnana no la este usando otra page.
                raise serializers.ValidationError({
                    'data': _('Valor incorrecto. Esta campaña esta siendo usada por otra página')})
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
        if validated_data['type'] == DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP:
            self.create_menu_interactivo(validated_data)
        return validated_data

    def create_menu_interactivo(self, validated_data):
        # Si es un menú interactivo debo crearlo:
        print(validated_data)
        page = None
        if 'page' in self.context:
            page = self.context['page']
        list_menu_data = validated_data['data']
        destino_whith_options = []
        for menu_data in list_menu_data:
            menu = MenuInteractivoMessengerMetaApp(
                menu_header=menu_data['menu_header'],
                texto_opcion_incorrecta=menu_data['wrong_answer'],
                texto_derivacion=menu_data['success'],
                timeout=0,
                page=page
            )
            menu.save()
            destino = DestinoEntrante.crear_nodo_ruta_entrante(menu)
            print("menu data >>>", menu_data)
            opcions = {
                "id_temp": menu_data['id_tmp'] if 'id_tmp' in menu_data else None,
                'destino_anterior': destino,
                "opcions": menu_data['options'] if 'options' in menu_data else []

            }
            print("menu_data >>>", menu_data)
            print("validated_data >>>", validated_data)
            if 'id_tmp' in menu_data and 'id_tmp' in validated_data and\
                    menu_data['id_tmp'] == validated_data['id_tmp']:
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
                elif option_data['type_option'] == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                    destino_siguiente = self.find_destination(
                        destino_whith_options, option_data['destination'])
                    # if destino_siguiente\
                    #         and object_dict['destino_anterior'].id in destino_siguiente.\
                    #         destinos_siguientes.values_list('destino_siguiente', flat=True).\
                    #         distinct():
                    #     raise serializers.ValidationError({
                    #         'data': _('No puede existir dependencias recursiva entre menus')})
                elif option_data['type_option'] == DestinoEntrante.CLOSING_MESSAGE:
                    plantilla = PlantillaMensaje.objects.get(id=option_data['destination'])
                    try:
                        destino_siguiente = DestinoEntrante.get_nodo_ruta_entrante(plantilla)
                    except Exception:
                        destino_siguiente = DestinoEntrante.crear_nodo_ruta_entrante(plantilla)
                if destino_siguiente:
                    option_data['destination'] = destino_siguiente.content_object.id
                    opcion = OpcionDestino.crear_opcion_destino(
                        destino_anterior=object_dict['destino_anterior'],
                        destino_siguiente=destino_siguiente,
                        valor=option_data['value'])
                    OpcionMenuInteractivoMessengerMetaApp.objects.create(
                        opcion=opcion,
                        descripcion=option_data['description'] if 'description'
                                                                  in option_data else "")

    def find_destination(self, destino_whith_options, value):
        for object_dict in destino_whith_options:
            if object_dict['id_temp'] == value:
                return object_dict['destino_anterior']


class MessengerMetaAppPageConfigurationCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default="")
    access_token = serializers.CharField(max_length=500)
    verify_token = serializers.CharField(max_length=255)
    app_id = serializers.CharField(max_length=255)
    page_id = serializers.CharField(max_length=255)
    horario = serializers.PrimaryKeyRelatedField(
        queryset=GrupoHorario.objects.all(), allow_null=True, required=False)
    welcome_message = serializers.PrimaryKeyRelatedField(
        queryset=PlantillaMensaje.objects.all(), allow_null=True, required=False)
    goodbye_message = serializers.PrimaryKeyRelatedField(
        queryset=PlantillaMensaje.objects.all(), allow_null=True, required=False)
    out_of_hours_message = serializers.PrimaryKeyRelatedField(
        queryset=PlantillaMensaje.objects.all(), allow_null=True, required=False)
    allow_reply_comments = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = PaginaMetaFacebook
        fields = ['name', 'description', 'access_token', 'verify_token', 'app_id', 'page_id',
                  'horario', 'welcome_message', 'goodbye_message', 'out_of_hours_message',
                  'allow_reply_comments', 'is_active']


class DestinoEntranteRelatedField(serializers.RelatedField):

    def _option_representation(self, option):
        return {
            'id': option.id,
            'type_option': option.destino_siguiente.tipo,
            'destination': option.destino_siguiente.content_object.id,
            'value': option.valor,
            'description': option.opcion_menu_messenger_meta_app.descripcion,
            'destination_name': option.destino_siguiente.content_object.nombre
        }

    def _menu_representation(self, value, data_list):
        menu = value.content_object
        menu_representation = {
            'id': menu.id,
            'id_tmp': menu.id,
            'is_main': menu.is_main,
            'menu_header': menu.menu_header if menu.menu_header else '',
            'wrong_answer': menu.texto_opcion_incorrecta,
            'success': menu.texto_derivacion,
            'timeout': 0,
            'options': []
        }
        data_list.append(menu_representation)
        for opcion in value.destinos_siguientes.all():
            menu_representation['options'].append(self._option_representation(opcion))
            if opcion.destino_siguiente.tipo == DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP:
                if not any(item['id'] ==
                           opcion.destino_siguiente.content_object.id for item in data_list):
                    self._menu_representation(opcion.destino_siguiente, data_list)
        return data_list

    def to_representation(self, page):
        if page.destination:
            value = page.destination
            representation = {
                'type': value.tipo,
                'id': value.content_object.id,
            }
            if value.tipo == DestinoEntrante.CAMPANA:
                representation['data'] = value.content_object.id
            elif value.tipo == DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP:
                data_list = []
                self._menu_representation(value, data_list)
                try:
                    menu_used_list = [menu.get('id') for menu in data_list if 'id' in menu]
                    orphan_menus =\
                        MenuInteractivoMessengerMetaApp.objects.filter(page=page).exclude(
                            id__in=menu_used_list)
                    for menu in orphan_menus:
                        menu_used_list = [menu.get('id') for menu in data_list if 'id' in menu]
                        if menu.id not in menu_used_list:
                            destino = DestinoEntrante.objects.filter(
                                object_id=menu.id,
                                tipo=DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP).last()
                            self._menu_representation(destino, data_list)
                    representation['data'] = sorted(data_list, key=lambda x: x["id"])
                except Exception as e:
                    print("*************", e)
                    pass
            else:
                raise Exception('Tipo de destino incorrecto')
            return representation
        return {}


class MessengerMetaAppPageConfigurationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    access_token = serializers.CharField()
    verify_token = serializers.CharField()
    app_id = serializers.CharField()
    page_id = serializers.CharField()
    allow_reply_comments = serializers.BooleanField()
    is_active = serializers.BooleanField()
    destination = DestinoEntranteRelatedField(source='*', read_only=True)
    horario = serializers.IntegerField(source='horario.id', required=False)
    welcome_message = serializers.IntegerField(source='welcome_message.id', required=False)
    goodbye_message = serializers.IntegerField(source='goodbye_message.id', required=False)
    out_of_hours_message = serializers.IntegerField(
        source='out_of_hours_message.id', required=False)


class ViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = PaginaMetaFacebook.objects.all()
        serializer = MessengerMetaAppPageConfigurationSerializer(many=True, instance=queryset)
        return Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                message=_('Se obtuvieron las páginas de forma exitosa'),
                data=serializer.data),
            status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            instance = PaginaMetaFacebook.objects.get(pk=pk)
        except PaginaMetaFacebook.DoesNotExist:
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR,
                    message=_('No se pudo obtener la página'),
                    data={'id': [_('No existe una página con este id')]}),
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MessengerMetaAppPageConfigurationSerializer(instance)
        return Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                message=_('Se obtuvieron las páginas de forma exitosa'),
                data=serializer.data),
            status=status.HTTP_200_OK)

    def create(self, request):
        serializer = MessengerMetaAppPageConfigurationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print('serializer valid')
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se creó la página de forma exitosa'),
                    data={}),
                status=status.HTTP_200_OK)
        return Response(
            data=get_response_data(
                status=HttpResponseStatus.ERROR,
                message=_('No se pudo crear la página'),
                data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = PaginaMetaFacebook.objects.get(pk=pk)

            request_data = request.data.copy()
            if 'destination' not in request_data:
                return Response(data=get_response_data(
                    message=_('Error en los datos'), errors={
                        'destination': [_('Este campo es requerido.')]}),
                    status=status.HTTP_400_BAD_REQUEST)
            destino_data = request_data.pop('destination')
            print('destino_data >>>', destino_data)
            serializer = MessengerMetaAppPageConfigurationCreateSerializer(
                instance, data=request_data, context={'page': instance})
            print('serializer >>>', serializer.is_valid())
            if serializer.is_valid():
                serializer_destino =\
                    DestinoDePaginaCreateSerializer(data=destino_data, context={'page': instance})
                if serializer_destino.is_valid():
                    # Primero desconectar destino anterior de la página para poderlo borrar
                    # pues es un campo PROTECT
                    instance.destination = None
                    instance.save()
                    for menu_old in instance.menuinteractivo.all():
                        try:
                            destino_old = DestinoEntrante.objects.get(
                                object_id=menu_old.pk,
                                tipo=DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP)
                            opciones_destino =\
                                OpcionDestino.objects.filter(destino_anterior=destino_old)
                            for option in opciones_destino:
                                if option.destino_siguiente.tipo ==\
                                        DestinoEntrante.MENU_INTERACTIVO_MESSENGER_META_APP:
                                    option.destino_siguiente.delete()
                                option.delete()
                            destino_old.delete()
                            menu_old.delete()
                        except Exception:
                            # DestinoEntrante.DoesNotExist no existe pq se elimino anteriormente
                            # como opción de otro menú interactivo')
                            menu_old.delete()
                    serializer_destino.save()
                    destino = serializer_destino.destino
                    page = serializer.save(
                        destination=destino
                    )
                    if page.destination.tipo == DestinoEntrante.CAMPANA:
                        if not destino.content_object.whatsapp_habilitado:
                            destino.content_object.whatsapp_habilitado = True
                            destino.content_object.save()
                            confwhatsappcampana = ConfiguracionMetaFacebookCampana(
                                campana=destino.content_object,
                                page=page,
                                nivel_servicio=90,
                            )
                            confwhatsappcampana.save()
                    if page.destination.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                        destino.content_object.is_main = True
                        destino.content_object.save()

                    serialized_data = serializer.data
                    serialized_data['destination'] = serializer_destino.data
                    # StreamDeLineas().notificar_nueva_linea(line)
                    return Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            message=_('Se creo la línea de forma exitosa'),
                            data=serialized_data),
                        status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        data=get_response_data(
                            message=_('Error en los datos') + ' destination: {}'.format(
                                serializer_destino.errors),
                            errors={'destination': serializer_destino.errors}),
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    data=get_response_data(message=_('Error en los datos'),
                                           errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                data=get_response_data(message=_('Error al crear la página >>>') + str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            instance = PaginaMetaFacebook.objects.get(pk=pk)
        except PaginaMetaFacebook.DoesNotExist:
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR,
                    message=_('No se pudo eliminar la página'),
                    data={'id': [_('No existe una página con este id')]}),
                status=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                message=_('Se elimino la página de forma exitosa')),
            status=status.HTTP_200_OK)
