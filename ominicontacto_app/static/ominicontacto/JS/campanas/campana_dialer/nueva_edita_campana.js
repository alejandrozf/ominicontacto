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
    var fechaInicio = $('#id_fecha_inicio').val();
    var fechaFinal = $('#id_fecha_fin').val();
    var languageCode = $('#languageCode').val();
    $('#id_fecha_inicio').datetimepicker({format: 'L', locale: languageCode});
    $('#id_fecha_fin').datetimepicker({format: 'L', locale: languageCode});
    if (fechaInicio != "" && fechaFinal != "") {
    /* si los entradas de fecha tenían valor se los restituimos */
        $('#id_fecha_inicio').val(fechaInicio);
        $('#id_fecha_fin').val(fechaFinal);
    }
});

$(function(){
            interaccionUrl();
        });
