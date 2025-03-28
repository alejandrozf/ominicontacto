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
import re
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from ominicontacto_app.models import ArchivoDeAudio
from configuracion_telefonia_app.models import (IVR, DestinoEntrante, OpcionDestino)
from ominicontacto_app.views_archivo_de_audio import convertir_archivo_audio

EMPTY_CHOICE = ('', '---------')
VALORES_FIJOS_IVR = (IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
VALOR_OPCION_FIELD = {
    IVR.VALOR_TIME_OUT: 'time_out_destination',
    IVR.VALOR_DESTINO_INVALIDO: 'invalid_destination'
}


class DestinationOptionCreateSerializer(serializers.Serializer):
    DMFT_REGEX = r'^[0-9|\-|#|\*]{1,5}$'

    id = serializers.IntegerField(required=False, allow_null=True)
    dtmf = serializers.CharField()
    destination_type = serializers.IntegerField()
    destination = serializers.IntegerField()

    def _validar_dtmf(self, data):
        dtmf = data['dtmf']
        compiled_regex = re.compile(self.DMFT_REGEX)
        if compiled_regex.match(dtmf) is None:
            raise serializers.ValidationError({
                'dtmf({0})'.format(dtmf): 'El valor del DTMF debe tener como máximo 5 dígitos(0-9)'
                                          'o un caracter (#, -, *)'
            })

    def validate(self, data):
        self._validar_dtmf(data)
        return data


class DestinationOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    dtmf = serializers.CharField(source='valor')
    destination_type = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = OpcionDestino
        fields = ('id', 'dtmf', 'destination_type', 'destination', 'destino_siguiente')
        read_only_fields = ['destino_siguiente']

    def get_destination_type(self, opcion_destino):
        return opcion_destino.destino_siguiente.tipo

    def get_destination(self, opcion_destino):
        return opcion_destino.destino_siguiente.pk


class AudioOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArchivoDeAudio
        fields = ('id', 'descripcion')


class DestinationTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = DestinoEntrante
        fields = ('id', 'nombre')


class IVRSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source='nombre', read_only=True)
    description = serializers.CharField(source='descripcion', read_only=True)
    time_out_destination = serializers.SerializerMethodField(read_only=True)
    time_out_destination_type = serializers.SerializerMethodField(read_only=True)
    invalid_destination = serializers.SerializerMethodField(read_only=True)
    invalid_destination_type = serializers.SerializerMethodField(read_only=True)
    destination_options = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IVR
        fields = ('id', 'name', 'description', 'audio_principal', 'time_out_destination',
                  'time_out_destination_type', 'time_out', 'time_out_retries', 'time_out_audio',
                  'invalid_destination', 'invalid_retries', 'invalid_audio',
                  'invalid_destination_type', 'destination_options')

    def _get_nodo_ivr(self, ivr):
        return DestinoEntrante.objects.get(
            object_id=ivr.pk, content_type=ContentType.objects.get_for_model(ivr))

    def _get_destino_by_value(self, ivr, value):
        nodo_ivr = self._get_nodo_ivr(ivr)
        opcion_destino = nodo_ivr.destinos_siguientes.get(valor=value)
        return opcion_destino.destino_siguiente

    def get_destination_options(self, ivr):
        valores_fijos_ivr = (IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
        nodo_ivr = self._get_nodo_ivr(ivr)
        destination_options = nodo_ivr.destinos_siguientes.exclude(valor__in=valores_fijos_ivr)
        return [DestinationOptionSerializer(option).data for option in destination_options]

    def get_time_out_destination(self, ivr):
        destino = self._get_destino_by_value(ivr, IVR.VALOR_TIME_OUT)
        return destino.pk

    def get_time_out_destination_type(self, ivr):
        destino = self._get_destino_by_value(ivr, IVR.VALOR_TIME_OUT)
        return destino.tipo

    def get_invalid_destination(self, ivr):
        destino = self._get_destino_by_value(ivr, IVR.VALOR_DESTINO_INVALIDO)
        return destino.pk

    def get_invalid_destination_type(self, ivr):
        destino = self._get_destino_by_value(ivr, IVR.VALOR_DESTINO_INVALIDO)
        return destino.tipo


class IVRCreateSerializer(serializers.ModelSerializer):
    AUDIO_OML = 1
    AUDIO_EXTERNO = 2
    MAIN_AUDIO = 1
    TIME_OUT_AUDIO = 2
    INVALID_AUDIO = 3
    CREATE = 1
    UPDATE = 2

    id = serializers.IntegerField(required=False, allow_null=True)
    # Audios
    main_audio = serializers.IntegerField(allow_null=True)
    time_out_audio = serializers.IntegerField(allow_null=True)
    invalid_audio = serializers.IntegerField(allow_null=True)
    type_main_audio = serializers.IntegerField()
    type_time_out_audio = serializers.IntegerField()
    type_invalid_audio = serializers.IntegerField()
    main_audio_ext = serializers.FileField(allow_null=True)
    time_out_audio_ext = serializers.FileField(allow_null=True)
    invalid_audio_ext = serializers.FileField(allow_null=True)
    # Fixed destinations
    time_out_destination = serializers.IntegerField()
    time_out_destination_type = serializers.IntegerField()
    invalid_destination = serializers.IntegerField()
    invalid_destination_type = serializers.IntegerField()
    # Destination options
    destination_options = DestinationOptionCreateSerializer(many=True, read_only=True)
    destination_options_json = serializers.JSONField(write_only=True)

    def _validar_audio(self, opcion, data):
        if opcion == self.MAIN_AUDIO:
            # Audio principal
            field = 'main_audio'
            fieldExt = 'main_audio_ext'
            fieldType = 'type_main_audio'
        if opcion == self.TIME_OUT_AUDIO:
            # Audio de time out
            field = 'time_out_audio'
            fieldExt = 'time_out_audio_ext'
            fieldType = 'type_time_out_audio'
        elif opcion == self.INVALID_AUDIO:
            # Audio para opcion invalida
            field = 'invalid_audio'
            fieldExt = 'invalid_audio_ext'
            fieldType = 'type_invalid_audio'
        tipoAudio = data[fieldType]
        audio = data[field]
        audioExt = data[fieldExt]
        if tipoAudio == self.AUDIO_OML:
            if audio is None:
                raise serializers.ValidationError({
                    field: 'Debe escoger un audio interno del sistema'
                })
            elif audioExt is not None:
                raise serializers.ValidationError({
                    field: 'No puedes tener un audio externo con la opcion de audio interno'
                })
        elif tipoAudio == self.AUDIO_EXTERNO:
            if audioExt is None:
                raise serializers.ValidationError({
                    field: 'Debe escoger un audio como archivo externo'
                })
            elif audioExt is not None and not audioExt.name.endswith('.wav'):
                # valida extension .wav
                raise serializers.ValidationError({
                    field: 'El archivo no tiene extension .wav'
                })

    def _validar_dtmf_repetidos(self, destination_options):
        dtmfs = []
        for opcion in destination_options:
            dtmf = opcion['dtmf'] if 'dtmf' in opcion.keys() else None
            if dtmf in dtmfs:
                raise serializers.ValidationError(
                    "Hay DTMF's repetidos en las opciones de destino del IVR"
                )
            dtmfs.append(dtmf)

    def validate_destination_options_json(self, data):
        self._validar_dtmf_repetidos(data)
        for d in data:
            serializer = DestinationOptionCreateSerializer(data=d)
            serializer.is_valid(raise_exception=True)
        return data

    def validate(self, data):
        self._validar_audio(self.MAIN_AUDIO, data)
        self._validar_audio(self.TIME_OUT_AUDIO, data)
        self._validar_audio(self.INVALID_AUDIO, data)
        return data

    # GETTERS
    def _get_destination_options(self, validated_data):
        return validated_data.pop('destination_options_json')

    def _get_local_destination_options(self, nodo_ivr):
        valores_fijos_ivr = (IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
        return nodo_ivr.destinos_siguientes.exclude(valor__in=valores_fijos_ivr)

    def _get_fixed_destinations(self, validated_data):
        return {
            'time_out_destination': validated_data.pop('time_out_destination'),
            'time_out_destination_type': validated_data.pop('time_out_destination_type'),
            'invalid_destination': validated_data.pop('invalid_destination'),
            'invalid_destination_type': validated_data.pop('invalid_destination_type')
        }

    def _set_audios(self, validated_data, instance=None):
        type_main_audio = validated_data.pop('type_main_audio')
        type_time_out_audio = validated_data.pop('type_time_out_audio')
        type_invalid_audio = validated_data.pop('type_invalid_audio')
        main_audio_ext = validated_data.pop('main_audio_ext')
        time_out_audio_ext = validated_data.pop('time_out_audio_ext')
        invalid_audio_ext = validated_data.pop('invalid_audio_ext')
        audio_principal_pk = validated_data.pop('main_audio')
        time_out_audio_pk = validated_data.pop('time_out_audio')
        invalid_audio_pk = validated_data.pop('invalid_audio')
        # Audios locales
        audio_principal = ArchivoDeAudio.objects.get(
            pk=audio_principal_pk) if audio_principal_pk is not None else None
        time_out_audio = ArchivoDeAudio.objects.get(
            pk=time_out_audio_pk) if time_out_audio_pk is not None else None
        invalid_audio = ArchivoDeAudio.objects.get(
            pk=invalid_audio_pk) if invalid_audio_pk is not None else None

        if main_audio_ext is not None and type_main_audio == self.AUDIO_EXTERNO:
            self._asignar_audio_externo(
                main_audio_ext, self.MAIN_AUDIO, validated_data, instance=instance)
        elif main_audio_ext is None and type_main_audio == self.AUDIO_OML:
            if instance is not None:
                instance.audio_principal = audio_principal
            else:
                validated_data['audio_principal'] = audio_principal

        if time_out_audio_ext is not None and type_time_out_audio == self.AUDIO_EXTERNO:
            self._asignar_audio_externo(
                time_out_audio_ext, self.TIME_OUT_AUDIO, validated_data, instance=instance)
        elif time_out_audio_ext is None and type_time_out_audio == self.AUDIO_OML:
            if instance is not None:
                instance.time_out_audio = time_out_audio
            else:
                validated_data['time_out_audio'] = time_out_audio

        if invalid_audio_ext is not None and type_invalid_audio == self.AUDIO_EXTERNO:
            self._asignar_audio_externo(
                invalid_audio_ext, self.INVALID_AUDIO, validated_data, instance=instance)
        elif invalid_audio_ext is None and type_invalid_audio == self.AUDIO_OML:
            if instance is not None:
                instance.invalid_audio = invalid_audio
            else:
                validated_data['invalid_audio'] = invalid_audio

    # SETTERS
    def _set_fixed_destinations(self, nodo_ivr, data=None, option=1):
        if data is not None:
            time_out_destination_new = DestinoEntrante.objects.get(pk=data['time_out_destination'])
            invalid_destination_new = DestinoEntrante.objects.get(pk=data['invalid_destination'])
            if option is self.CREATE:
                OpcionDestino.crear_opcion_destino(
                    nodo_ivr, time_out_destination_new, IVR.VALOR_TIME_OUT)
                OpcionDestino.crear_opcion_destino(
                    nodo_ivr, invalid_destination_new, IVR.VALOR_DESTINO_INVALIDO)
            elif option is self.UPDATE:
                time_out = nodo_ivr.destinos_siguientes.get(valor=IVR.VALOR_TIME_OUT)
                invalid_destination = nodo_ivr.destinos_siguientes.get(
                    valor=IVR.VALOR_DESTINO_INVALIDO)
                time_out.destino_siguiente = time_out_destination_new
                invalid_destination.destino_siguiente = invalid_destination_new
                time_out.save()
                invalid_destination.save()

    def _set_destination_options(self, nodo_ivr, destination_options):
        local_destination_options = self._get_local_destination_options(nodo_ivr)
        actuales_ids = list(local_destination_options.values_list('id', flat=True))
        nuevos_ids = []
        for destination in destination_options:
            dtmf = destination['dtmf']
            opcion_destino_id = destination['id']
            destino_id = destination['destination']
            destino_siguiente = DestinoEntrante.objects.get(pk=destino_id)
            # Update
            if opcion_destino_id is not None:
                nuevos_ids.append(opcion_destino_id)
                opcion_destino = OpcionDestino.objects.get(pk=opcion_destino_id)
                opcion_destino.valor = dtmf
                opcion_destino.destino_siguiente = destino_siguiente
                opcion_destino.destino_anterior = nodo_ivr
                opcion_destino.save()
            # Create
            else:
                OpcionDestino.objects.create(
                    valor=dtmf,
                    destino_siguiente=destino_siguiente,
                    destino_anterior=nodo_ivr
                )
        diference_ids = list(set(actuales_ids) - set(nuevos_ids))
        OpcionDestino.objects.filter(pk__in=diference_ids).delete()

    def _asignar_audio_externo(self, audio, typeAudio, validated_data, instance=None):
        descripcion = ''.join(audio.name.rsplit('.wav', 1))
        descripcion = ArchivoDeAudio.calcular_descripcion(descripcion)
        kwargs = {
            'descripcion': descripcion,
            'audio_original': audio
        }
        archivo_de_audio = ArchivoDeAudio.crear_archivo(**kwargs)
        convertir_archivo_audio(archivo_de_audio)
        if instance is not None:
            if typeAudio == self.MAIN_AUDIO:
                instance.audio_principal = archivo_de_audio
            elif typeAudio == self.TIME_OUT_AUDIO:
                instance.time_out_audio = archivo_de_audio
            elif typeAudio == self.INVALID_AUDIO:
                instance.invalid_audio = archivo_de_audio
        else:
            if typeAudio == self.MAIN_AUDIO:
                validated_data['audio_principal'] = archivo_de_audio
            elif typeAudio == self.TIME_OUT_AUDIO:
                validated_data['time_out_audio'] = archivo_de_audio
            elif typeAudio == self.INVALID_AUDIO:
                validated_data['invalid_audio'] = archivo_de_audio

    def update(self, instance, validated_data):
        ivr = instance
        destination_options = self._get_destination_options(validated_data)
        fixed_destinations = self._get_fixed_destinations(validated_data)
        nodo_ivr = DestinoEntrante.objects.get(
            object_id=ivr.pk, content_type=ContentType.objects.get_for_model(ivr))
        self._set_audios(validated_data, instance=ivr)
        ivr.nombre = validated_data.get('nombre', ivr.nombre)
        ivr.descripcion = validated_data.get('descripcion', ivr.descripcion)
        ivr.time_out = validated_data.get('time_out', ivr.time_out)
        ivr.invalid_retries = validated_data.get('invalid_retries', ivr.invalid_retries)
        ivr.time_out_retries = validated_data.get(
            'time_out_retries', ivr.time_out_retries)
        ivr.audio_principal = validated_data.get('audio_principal', ivr.audio_principal)
        ivr.time_out_audio = validated_data.get('time_out_audio', ivr.time_out_audio)
        ivr.invalid_audio = validated_data.get('invalid_audio', ivr.invalid_audio)
        self._set_destination_options(nodo_ivr, destination_options)
        self._set_fixed_destinations(nodo_ivr, data=fixed_destinations, option=self.UPDATE)
        ivr.save()
        return ivr

    def create(self, validated_data):
        destination_options = self._get_destination_options(validated_data)
        fixed_destinations = self._get_fixed_destinations(validated_data)
        self._set_audios(validated_data, instance=None)
        ivr = IVR.objects.create(**validated_data)
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr, commit=False)
        nodo_ivr.content_object = ivr
        nodo_ivr.save()
        self._set_destination_options(nodo_ivr, destination_options)
        self._set_fixed_destinations(nodo_ivr, data=fixed_destinations, option=self.CREATE)
        return ivr

    class Meta:
        model = IVR
        fields = ('id', 'nombre', 'descripcion', 'time_out', 'time_out_retries', 'invalid_retries',
                  'main_audio', 'time_out_audio', 'invalid_audio',
                  'type_main_audio', 'type_time_out_audio', 'type_invalid_audio',
                  'main_audio_ext', 'time_out_audio_ext', 'invalid_audio_ext',
                  'time_out_destination', 'time_out_destination_type',
                  'invalid_destination', 'invalid_destination_type',
                  'destination_options', 'destination_options_json')
