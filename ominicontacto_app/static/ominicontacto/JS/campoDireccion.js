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

/*global google Urls*/

const $selectDBContactos = $('#camp_bd_contactos');

$(function () {
    $selectDBContactos.change(actualizarOpcionesCampoDireccion);
    $('#id_0-campo_direccion_choice').on('change', actualizarCampoDireccion);
    actualizarOpcionesCampoDireccion();
});

function actualizarOpcionesCampoDireccion() {
    $('#id_0-campo_direccion_choice').find('option').remove().end()
        .append('<option value="">---------</option>').val('');

    if($selectDBContactos.val() == '') {
        $('#id_0-campo_direccion_choice').prop('disabled', true);
    }
    else{
        $('#id_0-campo_direccion_choice').prop('disabled', false);
        var bd_contacto_pk = $selectDBContactos.val();
        var campo_direccion = document.getElementById('id_0-campo_direccion').value;
        $.get(Urls.api_database_metadata_columns_fields(bd_contacto_pk), function (data) {
            data.forEach(function(e, i){
                if (e == campo_direccion){
                    $('#id_0-campo_direccion_choice').append($('<option selected=selected ></option>').val(e).text(e)); 
                }
                else{
                    $('#id_0-campo_direccion_choice').append($('<option></option>').val(e).text(e));
                }
            });
        });
        campo_direccion = document.getElementById('id_0-campo_direccion').value;
        $('#id_0-campo_direccion_choice').val(campo_direccion).change();
    }
}
function actualizarCampoDireccion() {
    var select_campo_direccion = document.getElementById('id_0-campo_direccion_choice');
    var option = select_campo_direccion.options[select_campo_direccion.selectedIndex];
    if (option) {
        document.getElementById('id_0-campo_direccion').value = option.value;
    }
       
}