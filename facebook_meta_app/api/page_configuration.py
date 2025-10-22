import json
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from configuracion_telefonia_app.models import DestinoEntrante, GrupoHorario, PlantillaMensaje

from facebook_meta_app.models import PaginaMetaFacebook
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


class DestinoDeLineaCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=((DestinoEntrante.CAMPANA, _('Campana')),
                 (DestinoEntrante.MENU_INTERACTIVO_WHATSAPP, _('Menu Interactivo'))))
    data = JSONSerializerField()
    id_tmp = serializers.IntegerField(required=False)

    def validate(self, data):
        destination_type = data.get('type')
        destination_data = data.get('data')
        if destination_type == DestinoEntrante.CAMPANA:
            campana_id = destination_data
            self._validate_campana_as_destination(campana_id)
        elif destination_type == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
            # Aquí agregar la validación para el menú interactivo si es necesario
            pass
        else:
            raise serializers.ValidationError({
                'data': _('Tipo de destino no soportado.')})
        return data


    def _validate_campana_as_destination(self, campana_id):
        """ Valido que exista el destino de la campaña y lo guardo en self.destino """
        if not isinstance(campana_id, int):
            raise serializers.ValidationError({
                'data': _('Valor incorrecto. Debe ser un id')})
        try:
            destination = DestinoEntrante.objects.get(tipo=DestinoEntrante.CAMPANA,
                                                  object_id=campana_id)
            destination_pages = destination.pages.all()
            if 'page' in self.context:
                destination_pages = destination_pages.exclude(id=self.context['page'].id)
            if destination_pages.exists():  # verificar que la campnana no la este usando otra page.
                raise serializers.ValidationError({
                    'data': _('Valor incorrecto. Esta campaña esta siendo usada por otra línea')})
            return campana_id
        except DestinoEntrante.DoesNotExist:
            raise serializers.ValidationError({
                'data': _('No existe destino con ese id de Campaña')})


class MessengerMetaAppPageConfigurationCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default="")
    access_token = serializers.CharField(max_length=500)
    verify_token = serializers.CharField(max_length=255)
    app_id = serializers.CharField(max_length=255)
    page_id = serializers.CharField(max_length=255)
    destination = DestinoDeLineaCreateSerializer()
    schedule = serializers.PrimaryKeyRelatedField(
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
        fields = '__all__'

    def create(self, validated_data):
        destination_data = validated_data.pop('destination')
        print('destination_data:', destination_data)
         # Validar y obtener el destino de la campaña
        destination = DestinoEntrante.objects.get(tipo=destination_data['type'],
                                                  object_id=destination_data['data'])
        print('destination found:', destination)
        config = PaginaMetaFacebook.objects.create(destination=destination, **validated_data)
        print('config created:', config)
        return config

    def update(self, instance, validated_data):
        destination_data = validated_data.pop('destination', None)
        if destination_data:
            # Validar y obtener el destino de la campaña
            destination = DestinoEntrante.objects.get(tipo=destination_data['type'],
                                                      object_id=destination_data['data'])
            instance.destination = destination
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MessengerMetaAppPageConfigurationSerializer(serializers.ModelSerializer):
    destination = serializers.SerializerMethodField()
    class Meta:
        model = PaginaMetaFacebook
        fields = '__all__'

    def get_destination(self, obj):
        return {
            'type': obj.destination.tipo,
            'data': obj.destination.object_id
        }

class MessengerMetaAppPageConfigurationViewSet(viewsets.ViewSet):

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
        except PaginaMetaFacebook.DoesNotExist:
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR,
                    message=_('No se pudo actualizar la página'),
                    data={'id': [_('No existe una página con este id')]}),
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MessengerMetaAppPageConfigurationCreateSerializer(instance, data=request.data, context={'page': instance})
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se actualizó la página de forma exitosa'),
                    data={}),
                status=status.HTTP_200_OK)
        return Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR,
                    message=_('No se pudo actualizar la página'),
                    data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST)

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