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
/* global gettext Urls moment get_ranges */

$(function() {
    var start = moment().subtract(29, 'days');
    var end = moment();
    function cb(start, end) {
        $('#id_fecha').html(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
    }

    $('#id_fecha').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
    });

    $('#id_fecha').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

    var ranges = get_ranges();

    // Init daterange plugin
    $('#id_fecha').daterangepicker(
        {
            locale: {
                format: 'DD/MM/YYYY'
            },
            autoUpdateInput: false,
            ranges: ranges,
        }, cb);

    cb(start, end);
});

function reassignAgenda() {
    $('#modalReassign').modal('hide');
    var URL = Urls.api_reasignar_agenda_contacto();
    $.ajax({
        url: URL,
        type: 'POST',
        dataType: 'json',
        data: {
            agenda_id: $('#id_agenda').val(),
            agent_id: $('#id_agent').val(),
        },
        success: function(data){
            if (data['status'] == 'OK') {
                $('#agente_agenda_' + data['agenda_id']).html(data['agent_name']);
                $.growl.notice({
                    'title': gettext('Agenda reasignada'),
                    'message': gettext('Agente: ' + data['agent_name']),
                    'duration': 5000});
            }
            else {
                // Show error message
                $.growl.error({
                    'title': gettext('Error al reasignar'),
                    'message': gettext(data['message']),
                    'duration': 5000});
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $.growl.error({
                'title': gettext('Error al reasignar'),
                'message': gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown,
                'duration': 5000
            });
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });
}

function openAgendaReasignWindow(agenda_id){
    $('#id_agenda').val(agenda_id);
    $('#contact_data').html('');

    var URL = Urls.api_data_agenda_contacto(agenda_id);
    $.ajax({
        url: URL,
        type: 'GET',
        dataType: 'json',
        data: {
            agenda_id: $('#id_agenda').val(),
            agent_id: $('#id_agent').val(),
        },
        success: function(data){
            if (data['status'] == 'OK') {
                var data_html = makeDataRow(gettext('Observaciones'), data['observations']);
                var contact_data = data['contact_data'];
                for (var column in contact_data) {
                    data_html += makeDataRow(column, contact_data[column]);
                }
                $('#contact_data').append(data_html);
            }
            else {
                // Show error message
                $.growl.error({
                    'title': gettext('Error al obtener datos de contacto'),
                    'message': gettext(data['message']),
                    'duration': 5000});
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $.growl.error({
                'title': gettext('Error al obtener datos de contacto'),
                'message': gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown,
                'duration': 5000
            });
            console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
        }
    });

    $('#modalReassign').modal('show');
}

function makeDataRow(title, data) {
    return '<tr><td><strong>' + title + '</strong></td><td>' + data + '</td></tr>';
}