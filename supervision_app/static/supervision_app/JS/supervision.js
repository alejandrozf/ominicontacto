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
/* global create_node */
/* global gettext */
/* global moment */

var table_agentes;
var table_data = [];
const MENSAJE_CONEXION_WEBSOCKET = 'Stream subscribed!';

$(function() {
    createDataTable();
    subcribeFilterChange();

    const contactadosSocket = new WebSocket(
        'wss://' +
        window.location.host +
        '/consumers/stream/supervisor/' +
        $('input#supervisor_id').val() +
        '/' +
        'agentes'
    );

    contactadosSocket.onmessage = function(e) {
        if (e.data != MENSAJE_CONEXION_WEBSOCKET) {
            try {
                var data = JSON.parse(e.data);
                var arrData = {};
                for (let index = 0; index < data.length; index++) {
                    var element = JSON.parse(data[index]
                        .replaceAll('\'', '"')
                        .replaceAll('"[', '[')
                        .replaceAll(']"', ']'));
                    processStreamRow(element, arrData);
                }

                var newData = crossData(table_agentes.data().toArray(), arrData);
                table_agentes.clear();
                table_agentes.rows.add(newData).draw();
                table_data = newData;
            } catch (err) {
                console.log(err);
            }
        }
    };
});

function processStreamRow(row, resultSet) {
    var id = row.id;
    if (id && !resultSet[id]) {
        resultSet[id] = normalizaRow(row);
    }
}

function crossData(tableData, newData) {
    var resData = [...tableData];
    for (let key in newData) {
        var found = false;
        for (let index = 0; index < resData.length; index++) {
            try {
                if (resData[index].id == newData[key].id) {
                    if (newData[key].status == '' || newData[key].status == 'OFFLINE') {
                        resData.splice(index, 1);
                    } else {
                        if (newData[key].status == 'UNAVAILABLE') {
                            newData[key].status = resData[index].status + '-' + newData[key].status;
                        }
                        resData[index] = newData[key];
                    }
                    found = true;
                }
            } catch (err) {
                continue;
            }
        }
        if (!found && newData[key].status != '' && newData[key].status != 'OFFLINE') {
            resData.push(newData[key]);
        }

    }
    return resData;
}

function normalizaRow(row) {
    var normalRow = {};
    normalRow.nombre = row.NAME;
    normalRow.status = row.STATUS;
    normalRow.sip = row.SIP;
    normalRow.pause_id = row.PAUSE_ID;
    normalRow.campana_llamada = (row.CAMPAIGN != null) ? row.CAMPAIGN : '';
    normalRow.contacto = (row.CONTACT_NUMBER != null) ? row.CONTACT_NUMBER : '';
    normalRow.tiempo = parseInt(row.TIMESTAMP);
    normalRow.grupo = row.GROUP;
    normalRow.campana = row.CAMPANAS;
    normalRow.id = row.id;

    return normalRow;
}

function createDataTable() {
    table_agentes = $('#tableAgentes').DataTable({
        'initComplete': function() {
            const TIME_COL_NUMBER = 6;
            var x = setInterval(function() {
                table_agentes.rows({ page: 'current', search: 'applied' }).every(function(index) {
                    var cell = this.cell(index, TIME_COL_NUMBER);
                    cell.data(cell.data());
                });
            }, 2000);
        },
        data: table_data,
        columns: [
            { 'data': 'nombre' },
            { 'data': 'grupo', 'visible': false },
            { 'data': 'campana[, ]', 'visible': false },
            { 'data': 'campana_llamada' },
            { 'data': 'contacto' },
            {
                'data': 'status',
                'render': function(data) { //( data, type, row, meta)
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
                    if (data.search('ONVIDEO') != -1) {
                        $status.attr('class', 'oncall');
                    }
                    if (data.search('DIALING') != -1) {
                        $status.attr('class', 'dialing');
                    }
                    if (data.search('UNAVAILABLE') != -1) {
                        $status.attr('class', 'unavailable');
                    }
                    return $status.prop('outerHTML');
                },
            },
            {
                'data': 'tiempo',
                'render': function(data) { // ( data, type, row, meta)
                    var duration = moment.duration(Math.round((Date.now() / 1000) - data), 'seconds');
                    return moment.utc(duration.as('milliseconds')).format('HH:mm:ss');
                },
            },
            {
                'data': 'id',
                'render': function(data, type, row) { // (data, type, row, meta)
                    return obtenerNodosAcciones(row['id'], row['status']);
                },
            },

        ],
        'searchCols': [
            null,
            { 'search': filtro_grupo(), },
            { 'search': filtro_campana(), },
            null,
            null,
            null,
            null,
            null,
        ],

        language: {
            search: gettext('Buscar: '),
            infoFiltered: gettext('(filtrando de un total de _MAX_ contactos)'),
            paginate: {
                first: gettext('Primero '),
                previous: gettext('Anterior '),
                next: gettext(' Siguiente'),
                last: gettext(' Último'),
            },
            lengthMenu: gettext('Mostrar _MENU_ entradas'),
            info: gettext('Mostrando _START_ a _END_ de _TOTAL_ entradas'),
        }
    });
}

function obtenerNodosAcciones(pk_agent, status) {

    var $whisper = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': '#',
        'onclick': 'executeSupervisorAction(\'' + pk_agent + '\', \'CHANSPYWISHPER\')'
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
        'href': '#',
        'onclick': 'executeSupervisorAction(\'' + pk_agent + '\', \'CHANSPY\')'
    });
    var $spanSpy = create_node('span', {
        'class': 'fas fa-user-secret',
        'aria-hidden': 'true',
        'title': gettext('Espiar'),
    });
    $spy.append($spanSpy);

    var in_pause = status.indexOf('PAUSE') == 0;
    var pause_action = in_pause ? 'AGENTUNPAUSE' : 'AGENTPAUSE';
    var pause_text = in_pause ? 'Unpause' : 'Pause';
    var $pause = create_node('a', {
        'class': 'btn btn-light btn-sm',
        'role': 'button',
        'href': '#',
        'onclick': 'executeSupervisorAction(\'' + pk_agent + '\', \'' + pause_action + '\')'
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
        'href': '#',
        'onclick': 'executeSupervisorAction(\'' + pk_agent + '\', \'AGENTLOGOUT\')'
    });
    var $spanLogout = create_node('span', {
        'class': 'fas fa-sign-out-alt',
        'aria-hidden': 'true',
        'title': gettext('Logout'),
    });
    $logout.append($spanLogout);

    var $div = create_node('div');
    $div.append($spy);
    $div.append($whisper);
    $div.append($pause);
    $div.append($logout);

    return $div.prop('outerHTML');
}

function filtro_grupo() {
    var grupo = $('#filter_group option:selected').html();
    return grupo;
}

function filtro_campana() {
    var campana = $('#filter_campana option:selected').html();
    return campana;
}

function subcribeFilterChange() {

    $('#filter_group').change(function() {
        var selection = $('#filter_group').find('option:selected');
        $('#filter_group option').not(selection).removeAttr('selected');
        selection.attr('selected', true);
        $('#tableAgentes').DataTable().destroy();
        createDataTable();
    });

    $('#filter_campana').change(function() {
        var selection = $('#filter_campana').find('option:selected');
        $('#filter_campana option').not(selection).removeAttr('selected');
        selection.attr('selected', true);
        $('#tableAgentes').DataTable().destroy();
        createDataTable();
    });
}