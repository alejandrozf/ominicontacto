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

$(document).ready(function(){
    $('#tableAgentes').tooltip({
        altPosition: {
            minOuterHeight: 60,
            tagName: 'select',
            callback: function() { return this.element.val().length > 20; },
            position: {my: 'left+100 top', at: 'right top', collision: 'flipfit'} // Right side
        }
    });
    $('#modalSendChat').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const recipient_id = button.data('recipient-id');
        const recipient_type = button.data('recipient-type');
        const modal = $(this);
        modal.find('[name=recipient-id]').val(recipient_id);
        modal.find('[name=recipient-type]').val(recipient_type);
        modal.find('[name=message-text]').val('');
    });
    $('#modalSendChat').on('click', '.btn.btn-primary', function (event) {
        $.ajax({
            url: Urls.api_enviar_mensaje_agentes(),
            type: 'POST',
            data: $(event.delegateTarget).find('form').serialize(),
            success: function(data) {
                console.log('success >> api_enviar_mensaje_agentes');
                $(event.delegateTarget).modal('hide');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            },
        });
    });
});
