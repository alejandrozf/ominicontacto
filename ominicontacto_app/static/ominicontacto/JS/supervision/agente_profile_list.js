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
