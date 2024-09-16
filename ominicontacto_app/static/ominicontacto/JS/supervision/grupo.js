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
    $('#id_obligar_calificacion').on('change', actualizarEstadoAutoUnpause);
    actualizarEstadoAutoUnpause();
    
    $('#id_limitar_agendas_personales').on('change', actualizarEstadoCantidadAgendasPersonales);
    actualizarEstadoCantidadAgendasPersonales();

    $('#id_limitar_agendas_personales_en_dias').on('change', actualizarEstadoDiasAgendasPersonales);
    actualizarEstadoDiasAgendasPersonales();

    $('#id_restringir_tipo_llamadas_manuales').on('change', actualizarRestringirManuales);
    actualizarRestringirManuales();

});

function actualizarEstadoAutoUnpause() {
    if ($('#id_obligar_calificacion').is(':checked'))
    {
        $('#id_auto_unpause').prop('disabled', true);
        $('#id_obligar_despausa').prop('disabled', false);
    }else{
        $('#id_auto_unpause').prop('disabled', false);
        $('#id_obligar_despausa').prop('disabled', true);
    }

}

function actualizarEstadoCantidadAgendasPersonales() {
    if ($('#id_limitar_agendas_personales').is(':checked'))
        $('#id_cantidad_agendas_personales').prop('disabled', false);
    else
        $('#id_cantidad_agendas_personales').prop('disabled', true);
}

function actualizarEstadoDiasAgendasPersonales() {
    if ($('#id_limitar_agendas_personales_en_dias').is(':checked'))
        $('#id_tiempo_maximo_para_agendar').prop('disabled', false);
    else
        $('#id_tiempo_maximo_para_agendar').prop('disabled', true);
}

function actualizarRestringirManuales() {
    if ($('#id_restringir_tipo_llamadas_manuales').is(':checked')) {
        $('#id_permitir_llamadas_manuales_a_manuales').prop('disabled', false);
        $('#id_permitir_llamadas_manuales_a_dialer').prop('disabled', false);
        $('#id_permitir_llamadas_manuales_a_entrante').prop('disabled', false);
        $('#id_permitir_llamadas_manuales_a_preview').prop('disabled', false);
    }
    else {
        $('#id_permitir_llamadas_manuales_a_manuales').prop('disabled', true);
        $('#id_permitir_llamadas_manuales_a_dialer').prop('disabled', true);
        $('#id_permitir_llamadas_manuales_a_entrante').prop('disabled', true);
        $('#id_permitir_llamadas_manuales_a_preview').prop('disabled', true);
    }
}
