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

*/
var DISPARADOR_SERVER = '3';    // SistemaExterno.SERVER
var FORMATO_MULTIPART = '1';    // SistemaExterno.MULTIPART
var FORMATO_JSON = '4';         // SistemaExterno.JSON
var OBJETIVO_EMBEBIDO = '1';    // SistemaExterno.JSON
var METODO_GET = '1';           // SistemaExterno.GET

$(function () {
    inicializarCampos();
});

function inicializarCampos() {
    var $disparador = $('#id_disparador');
    $disparador.on('change', actualizarEstadoObjetivo);
    actualizarEstadoObjetivo();
    var $metodo = $('#id_metodo');
    $metodo.on('change', actualizarEstadoFormato);
    actualizarEstadoFormato();
    var $formato = $('#id_formato');
    $formato.on('change', actualizarObjetivo);
    actualizarObjetivo();

}

function actualizarEstadoObjetivo() {
    var $disparador = $('#id_disparador');
    var $formato = $('#id_formato');
    var $objetivo = $('#id_objetivo');
    if ($disparador.val() == DISPARADOR_SERVER || $formato.val() == FORMATO_JSON){
        $objetivo.prop('disabled', true);
        $objetivo.val('');
        $objetivo.find('option[value=""]').prop('disabled', false);
    }
    else{
        $objetivo.prop('disabled', false);
        if ($objetivo.val() == '') {
            $objetivo.val(OBJETIVO_EMBEBIDO);
        }
        $objetivo.find('option[value=""]').prop('disabled', true);
    }
}

function actualizarEstadoFormato() {
    var $metodo = $('#id_metodo');
    var $formato = $('#id_formato'); 
    if ($metodo.val() == METODO_GET){
        $formato.prop('disabled', true);
        $formato.val('');
        $formato.find('option[value=""]').prop('disabled', false);
    }
    else {
        $formato.prop('disabled', false);
        if ($formato.val() == '') {
            $formato.val(FORMATO_MULTIPART);
        }
        $formato.find('option[value=""]').prop('disabled', true);
    }
}

function actualizarObjetivo(){
    var $metodo = $('#id_metodo');
    var $objetivo = $('#id_objetivo');
    var $formato = $('#id_formato');
    if ($metodo.val() != METODO_GET){
        if ($formato.val() == FORMATO_JSON){
            $objetivo.prop('disabled', true);
        }
        else{
            $objetivo.prop('disabled', false);
        }
    }   
}
