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

var table_salientes;
var table_data = [];
var dataAux = [];
var campanas_supervisor = [];
var campanas_id_supervisor = [];

$(function() {
    createDataTable();
    campanas_supervisor = $('input#campanas_list').val().split(',');
    campanas_id_supervisor = $('input#campanas_list_id').val().split(',');

    const contactadosSocket = new WebSocket(
        'wss://' +
        window.location.host +
        '/consumers/stream/supervisor/' +
        $('input#supervisor_id').val() +
        '/' +
        'salientes'
    );

    contactadosSocket.onmessage = function(e) {
        if (e.data != 'Stream subscribed!') {
            try {
                var data = JSON.parse(e.data);
                processData(data);
                table_salientes.clear();
                table_salientes.rows.add(dataAux).draw();
                table_data = dataAux;
            } catch (err) {
                console.log(err);
            }
        }
    };

    function processData(data) {
        dataAux = [...table_data];
        for (let index = 0; index < data.length; index++) {
            var row = JSON.parse(data[index]
                .replaceAll('\'', '"')
                .replaceAll('"{', '{')
                .replaceAll('}"', '}'));

            var existe = false;
            if (row['NOMBRE']) {
                for (let j in dataAux) {
                    if (dataAux[j]['nombre'] == row['NOMBRE']) {
                        dataAux[j] = row['ESTADISTICAS'];
                        existe = true;
                    }
                }
                if (!existe) {
                    dataAux.push(row['ESTADISTICAS']);
                }
            }
        }
    }

});

function createDataTable() {
    table_salientes = $('#tableSalientes').DataTable({
        data: table_data,
        columns: [
            { 'data': 'nombre' },
            { 'data': 'efectuadas' },
            { 'data': 'conectadas' },
            { 'data': 'no_conectadas' },
            { 'data': 'gestiones' },
            { 'data': 'porcentaje_objetivo' },

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
