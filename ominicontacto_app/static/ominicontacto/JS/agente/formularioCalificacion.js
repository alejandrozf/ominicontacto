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
/* global gettext */

$(function () {
    var $opcion_calificar = $('#id_opcion_calificacion');
    $opcion_calificar.removeAttr('required');
    subscribeToChangeOptionCalification($opcion_calificar);
    // si la campaña permite calificaciones a telefonos
    // se sincronizan los select(s) asociados a las calificaciones de los campos seleccionados con
    // los respectivos campos en el formulario de contacto
    // console.log($('#permitirCalificacionTelefono'));
    // console.log($('.calificacionTelefonoValor'));
    $('.calificacionTelefonoValor').each(function(index) {
        var $currentNode = $(this);
        var $clon = $currentNode.clone().attr('id', 'clon' + index);
        $clon.val($currentNode.val());
        var campo = $clon.attr('data-id');
        $('#contacto-' + campo).append($clon);
        // Creo checkbox de positiva.
        let id_positiva = 'positiva-contacto-' + campo;
        let div_positiva = $('<div class="positiva">' + gettext('Positiva') + '<input type="checkbox" ' +
                       'class="form-control" id="' + id_positiva + '"></div>');
        $('#contacto-' + campo).parent().after(div_positiva);
        $('#' + id_positiva).click(function(){
            if ($(this).prop('checked')){
                clearOtherPositiveCheckboxess(this);
                updateDisposition($clon);
            }
        });
        $clon.on('change', function() {
            var valueSelected = $(this).find('option:selected').val();
            $currentNode.val(valueSelected);
            $currentNode.find('option').prop('selected', false);
            $currentNode.find(`option[value="${valueSelected}"]`).prop('selected', true);
            $('#' + id_positiva).prop('checked', false);
        });
    });
});

function subscribeToChangeOptionCalification(opcion_calificar) {
    $(opcion_calificar).change(function(){
        var $nombre_subcalificaciones = JSON.parse($('#id_nombre_subcalificaciones').val());
        $nombre_subcalificaciones.forEach((obj, index) => {
            if (obj['id'] == opcion_calificar.val()){
                $('#id_subcalificacion').empty();
                let option_0 = document.createElement('option');
                option_0.value = '';
                option_0.text = '---------';
                option_0.selected = true;
                $('#id_subcalificacion').append(option_0);
                obj['subcalificaciones'].forEach(opcion => {
                    let option = document.createElement('option');
                    option.value = opcion;
                    option.text = opcion;
                    $('#id_subcalificacion').append(option);
                });
            }
        });
    });
}

function updateDisposition(div_calificacion_telefono){
    let nombre_calificacion = $(div_calificacion_telefono).children().val();
    $('#id_opcion_calificacion').children().each(function (i,option) {
        if(option.text == nombre_calificacion){
            $('#id_opcion_calificacion').val(option.value);
        }
    });
}

function clearOtherPositiveCheckboxess(current_positive) {
    $('[id^="positiva-contacto-"]').each(function(i, positive_checkbox){
        if (positive_checkbox != current_positive){
            $(positive_checkbox).prop('checked', false);
        }
    });
}
