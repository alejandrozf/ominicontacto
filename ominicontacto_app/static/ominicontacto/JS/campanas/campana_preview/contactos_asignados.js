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
/* global gettext */

var contactos_asignados;

$(function () {
    createDataTable();
    // setInterval(function () { table_agentes.ajax.reload(); }, 5000);
    liberar_reservar_contacto();
});
function createDataTable() {
    var pk_campana = $('#campana_id').val();
    contactos_asignados = $('#contactoAsignadoTable').DataTable({
        ajax: {
            url: Urls.api_contactos_asignados_campana_preview(pk_campana),
            dataSrc: '',
        },
        columnDefs: [ {
            orderable: false,
            className: 'select-checkbox',
            targets:   0,
        } ],
        select: {
            style:    'multi',
            selector: 'td:first-child'
        },
        order: [[ 1, 'asc' ]],
        
        columns: [
            {   'data': null,
                'defaultContent': '',
                'aTargets': [ -1 ]
            },
            {   'data': 'id',},
            { 'data': 'telefono'},
            { 'data': 'id_externo'},
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
        },
    });
}

function liberar_reservar_contacto(){
    var liberar_reservar_form = $('#liberar_reservar_form');
    var reservar = $('#reservar');
    var liberar = $('#liberar');
    $('#reservar, #liberar').click(function(){
        if (this.id == 'reservar'){
            if ($('#agentes').children('option:selected').val() == ''){
                $('#alertAgente').removeClass('hidden');
            }
            else{
                agente_seleccionado();
            }
            if (contactos_asignados.rows({selected:true}).count()==0){
                $('#alertContacto').removeClass('hidden');
            }
            else{
                contactos_seleccionados();
            }
       
            if ($('#agentes').children('option:selected').val() != '' && contactos_asignados.rows({selected:true}).count()!=0){
                liberar_reservar_form.prepend('<input type="hidden" name="accion" id="accion" value="reservar">');
                liberar_reservar_form.submit();
            } 
        }
        if (this.id == 'liberar'){

            if ($('#agentes').children('option:selected').val() == ''){
                $('#alertAgente').removeClass('hidden');
            }
            else{
                agente_seleccionado();
            }
            if (contactos_asignados.rows({selected:true}).count()==0){
                $('#alertContacto').removeClass('hidden');
            }
            else{
                contactos_seleccionados();
            }
      
            if ($('#agentes').children('option:selected').val() != '' && contactos_asignados.rows({selected:true}).count()!=0){
                liberar_reservar_form.prepend('<input type="hidden" name="accion" id="accion" value="liberar">');
                liberar_reservar_form.submit();
            } 
        } 
    });  
}

function agente_seleccionado(){
    var liberar_reservar_form = $('#liberar_reservar_form');
    var id_agente = $('#agentes').children('option:selected').val();
    liberar_reservar_form.prepend('<input type="hidden" name="id_agente" id="id_agente" value="'+id_agente+'">');
}

function contactos_seleccionados(){
    var contacts_selected = contactos_asignados.rows({selected:true}).indexes();
    var id_contactos = contactos_asignados.cells(contacts_selected, 1).data();
    var array_ids = id_contactos.toArray();
    
    var liberar_reservar_form = $('#liberar_reservar_form');
    liberar_reservar_form.prepend('<input type="hidden" name="contacts_selected" id="contacts_selected" value="['+array_ids+']">');
    return id_contactos;
}


