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


$(function() {
    const inputs = [
        'auto_unpause', 'obligar_calificacion', 'auto_attend_inbound', 'auto_attend_dialer'];
    for(let i in inputs) {
        let input = inputs[i];
        let setter_id = $(`#id_set_${input}`);
        let input_id = $(`#id_${input}`);
        if (input == 'auto_unpause'){
            $(setter_id).click(() => {setDisabledStatusNumber(setter_id, input_id);});
            setDisabledStatusNumber(setter_id, input_id);
        }
        else{
            $(setter_id).click(() => {setDisabledStatusCheckBox(setter_id, input_id);});
            setDisabledStatusCheckBox(setter_id, input_id);
        }
    }

    $('#id_obligar_calificacion').on('change', actualizarEstadoAutoUnpause);
    $('#id_set_obligar_calificacion').on('change', actualizarEstadoAutoUnpause);
    actualizarEstadoAutoUnpause();

});

function setDisabledStatusNumber(setter_id, input_id) {
    if (setter_id.prop('checked')){
        input_id.removeAttr('readonly');
    }
    else{
        input_id.attr('readonly', 'readonly');
    }
}

function setDisabledStatusCheckBox(setter_id, input_id) {
    if (setter_id.prop('checked')){
        input_id.prop('disabled', false);
    }
    else{
        input_id.prop('disabled', true);
    }
}

function actualizarEstadoAutoUnpause() {
    var disable_unpause = $('#id_set_obligar_calificacion').is(':checked');
    disable_unpause = disable_unpause && $('#id_obligar_calificacion').is(':checked');
    if (disable_unpause){
        $('#id_auto_unpause').attr('readonly', 'readonly');
        $('#id_set_auto_unpause').prop('disabled', true);
    }
    else{
        $('#id_auto_unpause').removeAttr('readonly');
        $('#id_set_auto_unpause').prop('disabled', false);
        setDisabledStatusNumber($('#id_set_auto_unpause'), $('#id_auto_unpause'));
    }
}
