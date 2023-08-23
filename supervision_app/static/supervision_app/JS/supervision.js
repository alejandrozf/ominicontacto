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
/* global create_node */
/* global gettext */
/* global moment */

var table_agentes;
var table_data = [];
const MENSAJE_CONEXION_WEBSOCKET = 'Stream subscribed!';

$(function() {
    createDataTable();
    subcribeFilterChange();

    const url = `wss://${window.location.host}/consumers/stream/supervisor/${$('input#supervisor_id').val()}/agentes`;
    const rws = new ReconnectingWebSocket(url, [], {
        connectionTimeout: 10000,
        maxReconnectionDelay: 3000,
        minReconnectionDelay: 1000,
    });
    rws.addEventListener('message', function(e) {
        if (e.data != MENSAJE_CONEXION_WEBSOCKET) {
            try {
                processData(e.data);
            } catch (err) {
                console.log(err);
            }
        }
    });
});

function processData(rawData) {
    const data = JSON.parse(rawData);
    let arrData = {};
    data.forEach(element => {
        try {
            const agent = JSON.parse(element
                .replaceAll('\'', '"')
                .replaceAll('’', '\'')
                .replaceAll('"[', '[')
                .replaceAll(']"', ']'));
            const rowData = normalizaRow(agent);
            const previousData = arrData[rowData.id];
            if (rowData.id != null && ((previousData != null && previousData.tiempo <= rowData.tiempo) || !previousData)) {
                arrData[rowData.id] = rowData;
            }
        } catch(err) {
            console.log('Error parsing data');
            console.log(err);
        }
    });
    if (arrData != {}) {
        updateTable(arrData);
    }
}

function updateTable(newData) {
    for (const agent in newData) {
        updateRow(newData[agent]);
    }
    table_agentes.draw(false);
}

function updateRow(data) {
    let row = table_agentes
        .row('#' + data.id);
    let dataRow = row.data();
    if (dataRow == null && checkStatus2Show(data.status)) {
        table_agentes.row.add(data);
    } else if (dataRow != null && checkStatus2Show(data.status)) {
        const prefixStatus = (data.status.search('UNAVAILABLE') != -1 && dataRow.status.search('UNAVAILABLE') == -1) ? dataRow.status : '';
        const prefixSeparator = (prefixStatus != '') ? '-' : '';
        data.status = prefixStatus + prefixSeparator + data.status;
        row.data(data);
    } else if (!checkStatus2Show(data.status)) {
        row.remove(false);
    }

}

function checkStatus2Show(status) {
    return !(['OFFLINE', ''].includes(status));
}

function normalizaRow(row) {
    var normalRow = {};
    normalRow.nombre = row.NAME;
    normalRow.status = row.STATUS;
    normalRow.sip = row.SIP;
    normalRow.pause_id = row.PAUSE_ID;
    normalRow.campana_llamada = row.CAMPAIGN || '';
    normalRow.contacto = row.CONTACT_NUMBER || '';
    normalRow.tiempo = parseInt(row.TIMESTAMP);
    normalRow.grupo = row.GROUP;
    normalRow.campana = row.CAMPANAS;
    normalRow.id = row.id || null;

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
        stateSave: true,
        rowId: 'id',
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
                    if (data.search('DISABLED') != -1) {
                        $status.attr('class', 'unavailable');
                    }
                    if (data.search('RINGING') != -1) {
                        $status.attr('class', 'ringing');
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
            { 'search': filtro_campana(), 'regex': true },
            null,
            null,
            null,
            null,
            null,
        ],
        lengthMenu: [[10, 25, 50, 100, 200, 500, -1], [10, 25, 50, 100, 200, 500 , gettext('Todos')]],
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
        },
        'orderMulti': true,
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
        'class': 'fas fa-volume-up',
        'aria-hidden': 'true',
        'title': gettext('Monitoreo'),
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

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

function filtro_campana() {
    var campana = $('#filter_campana option:selected').html();
    if (campana == '') return '';
    var campana_rgx = escapeRegExp(campana);
    return '(' + campana_rgx + ',|' + campana_rgx + '$)';
}

function subcribeFilterChange() {

    // Seleccionar filtro viejo de grupos.
    let old_filter = table_agentes.column(1).search();
    if (old_filter) {
        $('#filter_group').find('[value="'+old_filter+'"]').attr('selected', 'selected');
    }

    $('#filter_group').change(function() {
        var selection = $('#filter_group').find('option:selected');
        $('#filter_group option').not(selection).removeAttr('selected');
        selection.attr('selected', true);
        table_agentes.columns(1).search(selection.html()).draw();
    });

    // Seleccionar filtro viejo de campañas.
    old_filter = table_agentes.column(2).search();
    old_filter = old_filter.slice(2,-2); // Elimino los valores '\\b\\b'
    if (old_filter) {
        $('#filter_campana').find('[value="'+old_filter+'"]').attr('selected', 'selected');
    }

    $('#filter_campana').change(function() {
        var selection = $('#filter_campana').find('option:selected');
        $('#filter_campana option').not(selection).removeAttr('selected');
        selection.attr('selected', true);
        var regex = '\\b' + selection.html() + '\\b';
        table_agentes.columns(2).search(regex, true, false).draw();
    });
}
