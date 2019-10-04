/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

/*
 * Código js relacionado con vista de creación/modificación de IVRs
 */

/* global nodosEntrantesCambioPorTipo */
/* global AGREGAR_DESTINO */
/* global REMOVER_CAMPO */

$(document).ready(function(){
    var $destinoTimeOutTipo = $('#destinoTimeOutTipo');
    var $destinoTimeOut = $('#destinoTimeOut');
    var $destinoInvalido = $('#destinoInvalido');
    var $destinoInvalidoTipo = $('#destinoInvalidoTipo');
    nodosEntrantesCambioPorTipo($destinoTimeOutTipo, $destinoTimeOut);
    nodosEntrantesCambioPorTipo($destinoInvalidoTipo, $destinoInvalido);
    $('.opcionDestinoTr').each(function() {
        var $tipoDestino = $(this).find('.tipoDestino');
        var $destino = $(this).find('.destino');
        nodosEntrantesCambioPorTipo($tipoDestino, $destino);
    });

});

$(function() {
    var opcionDestino = $('#opciondestino').val();
    $('.opcionDestinoTr').formset({
        addText: AGREGAR_DESTINO,
        deleteText: REMOVER_CAMPO,
        prefix: opcionDestino,
        addCssClass: 'btn btn-outline-primary',
        deleteCssClass: 'btn btn-outline-danger deleteFormset',
        formCssClass: 'dynamic-formset',
        added: function (row) {
            row.each(function() {
                var $tipoDestino = $(this).find('.tipoDestino');
                var $destino = $(this).find('.destino');
                nodosEntrantesCambioPorTipo($tipoDestino, $destino);
            });
        }
    });
});

function toggleAudioSource(nombre_radio, id_audio, id_archivo ) {
    var selection = $('input:radio[name ="' + nombre_radio + '"]:checked').val();
    if (selection == '1'){
        $('#' + id_audio).prop('disabled', false);
        $('#' + id_archivo).prop('disabled', true);
    }
    else {
        $('#' + id_audio).prop('disabled', true);
        $('#' + id_archivo).prop('disabled', false);
    }
}

$(function() {
    $('#id_audio_ppal_escoger').change(function(){
        toggleAudioSource('audio_ppal_escoger',
            'id_audio_principal',
            'id_audio_ppal_ext_audio');
    });
    $('#id_time_out_audio_escoger').change(function(){
        toggleAudioSource('time_out_audio_escoger',
            'id_time_out_audio',
            'id_time_out_ext_audio');
    });
    $('#id_invalid_destination_audio_escoger').change(function(){
        toggleAudioSource('invalid_destination_audio_escoger',
            'id_invalid_audio',
            'id_invalid_destination_ext_audio');
    });
    toggleAudioSource('audio_ppal_escoger',
        'id_audio_principal',
        'id_audio_ppal_ext_audio');
    toggleAudioSource('time_out_audio_escoger',
        'id_time_out_audio',
        'id_time_out_ext_audio');
    toggleAudioSource('invalid_destination_audio_escoger',
        'id_invalid_audio',
        'id_invalid_destination_ext_audio');
});
