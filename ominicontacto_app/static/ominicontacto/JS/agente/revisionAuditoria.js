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
/* global Urls gettext */

function toggleRevision(audit_id) {
    var revised = $('#toggle_revision').attr('revised');
    if (revised == 'waiting') return;

    var current_status = revised == 'True';
    var new_revised_status = !current_status;

    $('#toggle_revision').hide();
    $('#toggle_revision').removeClass('btn-warning');
    $('#toggle_revision').removeClass('btn-primary');
    $('#toggle_revision').attr('revised', 'waiting');
    var message;

    var URL = Urls.api_set_estado_revision();
    $.ajax({
        url: URL,
        type: 'POST',
        dataType: 'json',
        data: {
            audit_id: audit_id,
            revised: new_revised_status,
        },

        success: function(data){
            if (data['status'] == 'OK') {
                var audit_status = data['audit_status'];
                if (audit_status) {
                    audit_status = 'True';
                    $('#toggle_revision').addClass('btn-primary');
                    $('#toggle_revision').html('Revisada');
                    message = gettext('Auditoría marcada como revisada');

                    $('#toggle_revision').attr('revised', audit_status);
                    $('#toggle_revision').show();
                    $.growl.notice({
                        'title': gettext('Revisada'),
                        'message': message,
                        'duration': 5000});
                }
                else {
                    audit_status = 'False';
                    $('#toggle_revision').addClass('btn-warning');
                    $('#toggle_revision').html('No revisada');
                    message = gettext('Auditoría marcada como no revisada');

                    $('#toggle_revision').attr('revised', audit_status);
                    $('#toggle_revision').show();
                    $.growl.notice({
                        'title': gettext('No revisada'),
                        'message': message,
                        'duration': 5000});
                }
            }
            else {
                // Show error message
                $.growl.error({
                    'title': gettext('Error al marcar auditoría'),
                    'message': gettext(data['message']),
                    'duration': 5000});
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $.growl.error({
                'title': gettext('Error al marcar auditoría'),
                'message': gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown,
                'duration': 5000
            });
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
}