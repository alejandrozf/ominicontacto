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

$(function () {
    $('#id_usar_tts').change(manageUseTTSChange);
    $('#id_tts_service').change(manageTTSServiceChange);
    manageUseTTSChange();
    manageTTSServiceChange();
});

function manageUseTTSChange(){
    if ($('#id_usar_tts').prop('checked')) {
        $('#id_tts_service').parent().show();
        $('#id_tts_voice').parent().show();
        $('#id_tts_text').parent().show();
        $('#id_audio_original').prop('disabled', true);
    }
    else {
        $('#id_tts_service').parent().hide();
        $('#id_tts_voice').parent().hide();
        $('#id_tts_text').parent().hide();
        $('#id_audio_original').prop('disabled', false);
    }
}

function manageTTSServiceChange() {
    let service = $('#id_tts_service').val();
    let first = undefined;
    $('#id_tts_voice option').each(function() {
        // If service value is prefix of option value
        if ($(this).val().indexOf(service) == 0) {
            $(this).show();
            if (first == undefined){
                first = $(this).val();
            }
        }
        else {
            $(this).hide();
        }
    });
    $('#id_tts_voice').val(first);
}
