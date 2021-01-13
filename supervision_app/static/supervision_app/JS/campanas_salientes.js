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

$(function () {
    createDataTable();
    setInterval(function () { table_salientes.ajax.reload(); }, 5000);
});

function createDataTable() {
    table_salientes = $('#tableSalientes').DataTable({
        ajax: {
            url: Urls.api_supervision_campanas_salientes(),
            dataSrc: ''
        },
        columns: [
            { 'data': 'nombre' },
            { 'data': 'efectuadas'},
            { 'data': 'conectadas'},
            { 'data': 'no_conectadas' },
            { 'data': 'gestiones' },

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