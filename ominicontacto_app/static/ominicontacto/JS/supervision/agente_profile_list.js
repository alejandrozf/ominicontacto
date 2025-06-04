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

var agents_table;
var GROUP_COL = 4;

$(function () {
    initializeAgentsTable();
    inicializarFiltroGrupos();
});

function initializeAgentsTable() {
    agents_table = $('#agents-table').DataTable({
        language: {
            search: gettext('Filtrar:'),
            paginate: {
                first: gettext('Primero'),
                previous: gettext('Anterior'),
                next: gettext('Siguiente'),
                last: gettext('Último')
            },
            lengthMenu: gettext('Mostrar _MENU_ entradas'),
            info: gettext('Mostrando _START_ a _END_ de _TOTAL_ entradas'),
        },
        order: [[ 1, 'asc' ]],
        columnDefs: [
            {'orderable': false, 'targets': [0]},
            {'searchable': false, 'targets': [5, 6]},
            {'orderable': false, 'targets': [5, 6]}
        ],
    });
}

function inicializarFiltroGrupos() {
    var select = $('#group-filter').on('change', function () {
        buscarGrupo($(this).val());
    });

    var column = agents_table.column(GROUP_COL);
    column.data().unique().sort().each(function (d, j) {
        select.append('<option value="' + d + '">' + d + '</option>');
    });
}

function buscarGrupo(nombre_grupo) {
    var val = $.fn.dataTable.util.escapeRegex(nombre_grupo);
    agents_table.column(GROUP_COL).search(val ? '^' + val + '$' : '', true, false).draw();
}

function obtener_campanas_agente(pk_agent) {
    var $campanasAgenteModal = $('#campanasAgenteModal');
    var filter = '?status=[2,5,6]&agent=' + pk_agent;
    var table = $('#campanasAgenteTable').DataTable( {
        ajax: {
            url: Urls.api_campanas_de_supervisor() + filter,
            dataSrc: '',
        },
        columns: [
            { 'data': 'id'},
            { 'data': 'nombre',},
            { 'data': 'objetivo'},
        ],
        paging: false,
    } );
    $campanasAgenteModal.modal('show');
    table.destroy();
}
