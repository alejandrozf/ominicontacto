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

$(function () {
    $('#id_obligar_calificacion').on('change', actualizarEstadoAutoUnpause);
    actualizarEstadoAutoUnpause();
    
    $('#id_limitar_agendas_personales').on('change', actualizarEstadoCantidadAgendasPersonales);
    actualizarEstadoCantidadAgendasPersonales();
});

function actualizarEstadoAutoUnpause() {
    if ($('#id_obligar_calificacion').is(':checked'))
        $('#id_auto_unpause').prop('disabled', true);
    else
        $('#id_auto_unpause').prop('disabled', false);
}

function actualizarEstadoCantidadAgendasPersonales() {
    if ($('#id_limitar_agendas_personales').is(':checked'))
        $('#id_cantidad_agendas_personales').prop('disabled', false);
    else
        $('#id_cantidad_agendas_personales').prop('disabled', true);
}
