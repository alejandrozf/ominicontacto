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


$(function() {

    let input = 'auto_unpause';
    let setter_id = $(`#id_set_${input}`);
    let input_id = $(`#id_${input}`);
    $(setter_id).click(() => {setDisabledStatusNumber(setter_id, input_id);});
    setDisabledStatusNumber(setter_id, input_id);

    const inputs = ['obligar_calificacion', 'auto_attend_inbound', 'auto_attend_dialer'];
    for(let i in inputs) {
        let input = inputs[i];
        let setter_id = $(`#id_set_${input}`);
        let input_id = $(`#id_${input}`);
        $(setter_id).click(() => {setDisabledStatusCheckBox(setter_id, input_id);});
        setDisabledStatusCheckBox(setter_id, input_id);
    }
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
