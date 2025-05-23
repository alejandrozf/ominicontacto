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
/* global AGREGAR_CAMPO, REMOVER_CAMPO, SIN_ACCION, GESTION */


var wizard = $('#wizard').val();
/* adiciona plugin 'ext/jquery.formset.js' para generar forms dinamicamente
        en un formset  */
$('.linkFormset').formset({
    addText: AGREGAR_CAMPO,
    deleteText: REMOVER_CAMPO,
    prefix: wizard,
    addCssClass: 'addFormset btn btn-outline-primary',
    deleteCssClass: 'deleteFormset btn btn-outline-danger',
    added: function (row) {
        row.find('.nombre-subcalificaciones > input').val(
            row.prev('tr').find('.nombre-subcalificaciones > input').val()
        );
        /* inicializa el nuevo formulario de opción de calificación */
        $(row.find('.nombre > select')).prop( 'disabled', false );
        var $tipo = $(row.find('.tipo > select'));
        $tipo.prop( 'disabled', false );
        // Crea las opciones de tipo, para que no aparezca la de agenda.
        var tipoOpciones = {};
        tipoOpciones[SIN_ACCION] = '0';
        tipoOpciones[GESTION] = '1';
        $tipo.empty();
        $.each(tipoOpciones, function(key,value) {
            $tipo.append($('<option></option>')
                .attr('value', value).text(key));
        });
        var $formulario = $(row.find('.formulario > select'));
        $formulario.prop( 'disabled', false );
        /* Suscribo al control que deshabilita el campo formulario segun el tipo */
        subscribeToChangeControl($tipo);

        var $nombre = $(row.find('.nombre > select'));
        subscribeToChangeNombre($nombre);
    }
});
/* oculta los links de eliminación para los formularios de opciones de calificación
        que no deben ser eliminados */
$('.readOnly>td').find('.deleteFormset').attr('class', 'hidden');

/* Suscribo al control que deshabilita el campo formulario segun el tipo */
$(function() {
    $('[name$=-tipo]').each(function() {
        subscribeToChangeControl(this);
    });
    $('[name$=-nombre]').each(function() {
        subscribeToChangeNombre(this);
    });
});

function subscribeToChangeControl(type_input) {
    setAssociatedFormDisabledStatus(type_input);
    $(type_input).change(function(){
        setAssociatedFormDisabledStatus(type_input);
    });
}

function setAssociatedFormDisabledStatus(type_input){
    var type = $(type_input).val();
    var form_input_name = $(type_input).prop('name').slice(0,-4) + 'formulario';
    // Si el campo tipo está deshabilitado asumo que no se puede modificar el formulario
    var type_input_disabled = $(type_input).prop('disabled');
    if (type == '1' && !type_input_disabled){
        $('#id_' + form_input_name).prop('disabled', false);
    }
    else {
        $('#id_' + form_input_name).prop('disabled', true);
        $('#id_' + form_input_name).val('');
    }
}

function setSubdispositionsOptions(select_nombre){
    var row_id = $(select_nombre).prop('name').slice(0,-6);
    var form_input_subcalificaciones = row_id + 'subcalificaciones';
    var form_input_nombre_subcalificaciones = row_id + 'nombre_subcalificaciones';
    var lista = JSON.parse($('#id_' + form_input_nombre_subcalificaciones).val().replace(/'/g, '"'));
    lista.forEach((obj, index) => {
        if ($(select_nombre).val() in obj){
            $('#id_' + form_input_subcalificaciones).val(JSON.stringify(obj[$(select_nombre).val()]));
        }
    });
}

function subscribeToChangeNombre(select_nombre) {
    $(select_nombre).change(function(){
        setSubdispositionsOptions(select_nombre);
    });
}
