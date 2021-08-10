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

/* global Urls */
/* global gettext */
/* global PhoneJSController */
/* global table_data */
/* exported executeSupervisorAction */

var phone_controller;
var spied_agent_name;

$(function() {
    var supervisor_id = $('#supervisor_id').val();
    var sipExtension = $('#sipExt').val();
    var sipSecret = $('#sipSec').val();

    phone_controller = new PhoneJSController(supervisor_id, sipExtension, sipSecret);

    window.addEventListener('beforeunload', preventLeaveOnCall);
});

function getSpiedAgentName(agent_id) {
    spied_agent_name = $('#tableAgentes')
        .DataTable()
        .row('#' + agent_id)
        .data()
        .nombre;
}

function executeSupervisorAction(pk_agent, action) {
    getSpiedAgentName(pk_agent);
    // Ignoro acciones mientras este en llamada
    if (phone_controller.is_on_call()) {
        $.growl.warning({
            title: gettext('Atención!'),
            message: gettext('Debe finalizar la acción actual antes de realizar otra.')
        });
        return;
    }

    $.ajax({
        url: Urls.api_accion_sobre_agente(pk_agent),
        type: 'POST',
        dataType: 'json',
        data: { 'accion': action },
        success: function() { // function(data)

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        },
    });
}

function preventLeaveOnCall(event) {
    if (phone_controller.is_on_call()) {
        phone_controller.phone.hangUp();

        $.growl.warning({
            title: gettext('Atención!'),
            message: gettext('Se ha registrado un intento de salir de esta pantalla. Su llamado ha finalizado.')
        });

        // Cancel the event as stated by the standard.
        event.preventDefault();
        // Chrome requires returnValue to be set.
        event.returnValue = gettext('Debe finalizar la acción actual antes de salir de esta pantalla.');
        return gettext('Debe finalizar la acción actual antes de salir de esta pantalla.');
    }
}