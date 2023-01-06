/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License version 3, as published by
 the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

/* global nodosEntrantesCambioPorTipo */

const SIN_INTERACCION_EXTERNA = '1';      // IdentificadorCliente.SIN_INTERACCION_EXTERNA
const INTERACCION_EXTERNA_1 = '2';        // IdentificadorCliente.INTERACCION_EXTERNA_1
const INTERACCION_EXTERNA_2 = '3';        // IdentificadorCliente.INTERACCION_EXTERNA_2

// Actualizacion de campos selectores de destinos segun el tipo.
var $tipoDestinoMatch = $('#tipoDestinoMatch');
var $destinoMatch = $('#destinoMatch');
var $tipoDestinoNoMatch = $('#tipoDestinoNoMatch');
var $destinoNoMatch = $('#destinoNoMatch');

$(function () {
    $('#id_tipo_interaccion').change(actualizarCamposSegunInteraccion);

    // cuando se escoge un tipo de nodo destino se despliegan en el campo selector de destinos
    // todos los nodos destinos de este tipo
    nodosEntrantesCambioPorTipo($tipoDestinoMatch, $destinoMatch);
    nodosEntrantesCambioPorTipo($tipoDestinoNoMatch, $destinoNoMatch);

    actualizarCamposSegunInteraccion();
});

function actualizarCamposSegunInteraccion() {
    var tipo_interaccion = $('#id_tipo_interaccion').val();
    if (tipo_interaccion == SIN_INTERACCION_EXTERNA) {
        $('#id_url').prop('disabled', true);
    }
    else {
        $('#id_url').prop('disabled', false);
    }

    if (tipo_interaccion == INTERACCION_EXTERNA_2) {
        $tipoDestinoMatch.prop('disabled', true);
        $destinoMatch.prop('disabled', true);
    }
    else {
        disableDestinos(false);
    }
}

function disableDestinos(estado) {
    $tipoDestinoMatch.prop('disabled', estado);
    $destinoMatch.prop('disabled', estado);
    $tipoDestinoNoMatch.prop('disabled', estado);
    $destinoNoMatch.prop('disabled', estado);
}
