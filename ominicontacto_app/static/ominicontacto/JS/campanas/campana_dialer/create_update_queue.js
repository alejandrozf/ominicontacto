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
    $('#id_detectar_contestadores').change(actualizarEstadoDeSelectorDeAudios);
    actualizarEstadoDeSelectorDeAudios();
});

function actualizarEstadoDeSelectorDeAudios(){
    var detectar = $('#id_detectar_contestadores').prop("checked");
    if (!detectar){
    	$('#id_audio_para_contestadores').val('');
    }
    $('#id_audio_para_contestadores').prop("disabled", !detectar);
};
