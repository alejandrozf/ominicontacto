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

function obtenerNodosAcciones(pk_agent, status) {

    var $whisper = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': "#",
        'onclick': "executeSupervisorAction('" + pk_agent + "', 'CHANSPYWISHPER')"
    });
    var $spanWhisper = create_node('span', {
        'class': 'fas fa-comment',
        'aria-hidden': 'true',
        'title': gettext('Susurrar'),
    });
    $whisper.append($spanWhisper);

    var $spy = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': "#",
        'onclick': "executeSupervisorAction('" + pk_agent + "', 'CHANSPY')"
    });
    var $spanSpy = create_node('span', {
        'class': 'fas fa-user-secret',
        'aria-hidden': 'true',
        'title': gettext('Espiar'),
    });
    $spy.append($spanSpy);

    var in_pause = status.indexOf('PAUSE') == 0;
    var pause_action = in_pause?'AGENTUNPAUSE':'AGENTPAUSE';
    var pause_text = in_pause?'Unpause':'Pause';
    var $pause = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': "#",
        'onclick': "executeSupervisorAction('" + pk_agent + "', '" + pause_action + "')"
    });
    var $spanPause = create_node('span', {
        'class': 'fas fa-pause-circle',
        'aria-hidden': 'true',
        'title': gettext(pause_text),
    });
    $pause.append($spanPause);

    var $logout = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': "#",
        'onclick': "executeSupervisorAction('" + pk_agent + "', 'AGENTLOGOUT')"
    });
    var $spanLogout = create_node('span', {
        'class': 'fas fa-sign-out-alt',
        'aria-hidden': 'true',
        'title': gettext('Logout'),
    });
    $logout.append($spanLogout);

    $div = create_node('div');
    $div.append($spy);
    $div.append($whisper);
    $div.append($pause);
    $div.append($logout);

    return $div.prop('outerHTML');
}


function assignToColumns(data_sin_filtrar) {
    var data = data_sin_filtrar.filter(function (val) {return val['status'] != 'OFFLINE'});
    var table = $('#tableAgentes').dataTable({
        bAutoWidth : false,
        aaData : data,
        columns : [
            {'data' : 'nombre'},
            {'data' : 'status',
             'render': function ( data, type, row, meta) {
                 var $status = create_node('p');
                 $status.text(data);
                 if (data.search('READY') != -1) {
                     $status.attr('class', 'ready');
                 }
                 if (data.search('PAUSE') != -1) {
                     $status.attr('class', 'paused');
                 }
                 if (data.search('ONCALL') != -1) {
                     $status.attr('class', 'oncall');
                 }
                 return $status.prop('outerHTML');
             }

            },
            {'data' : 'tiempo',
             'render': function ( data, type, row, meta ) {
                 var duration = moment.duration(data, 'seconds');
                 return moment.utc(duration.as('milliseconds')).format('HH:mm:ss')
             },
            },
            {'data' : 'id',
             'render': function ( data, type, row, meta ) {
                 return obtenerNodosAcciones(row['id'], row['status']);
             },
            }
        ],
        language: {
            search: gettext("Buscar: "),
            infoFiltered: gettext("(filtrando de un total de _MAX_ contactos)"),
            paginate: {
                first: gettext("Primero "),
                previous: gettext("Anterior "),
                next: gettext(" Siguiente"),
                last: gettext(" Último"),
            },
            lengthMenu: gettext("Mostrar _MENU_ entradas"),
            info: gettext("Mostrando _START_ a _END_ de _TOTAL_ entradas"),
        }
    });
}

function refreshActiveAgentsTable() {
    if ( $.fn.DataTable.isDataTable('#tableAgentes') ) {
        $('#tableAgentes').DataTable().destroy();
    }
    $.ajax({
        url: Urls.api_agentes_activos(),
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            assignToColumns(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
        },
    });
}

$(document).ready(function () {
    refreshActiveAgentsTable()
    setInterval(refreshActiveAgentsTable, 5000);
});
