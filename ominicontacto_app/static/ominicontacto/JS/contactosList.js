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

/* global Urls gettext create_node PREVIEW DIALER */
$(document).ready(function () {

    var $inputContacto = $('#pk_contacto');
    var pk_campana = $('#pk_campana').attr('value');
    var tipo_campana = $('#campana_tipo').attr('value');
    var length_row_data = 0;

    function getColumsNameOfDBContactos() {
        return $('#db_metadata_columnas').val().split(' ');
    }

    function getTargets(size_data) {
        var targets = [];
        for (let i = 2; i < (2 + size_data); i++) {
            targets.push(i);
        }
        return targets;
    }

    function getColumnDefsByMetadata() {
        var columnDefs = [];
        var columnNames = getColumsNameOfDBContactos();
        var targets = getTargets(columnNames.length);
        columnDefs.push({
            'className': 'text-center',
            'targets': [length_row_data - 1]
        });
        for (let i = 0; i < targets.length; i++) {
            columnDefs.push({
                'className': `d-none db_metadata_body_${columnNames[i]}`,
                'targets': targets[i]
            });
        }
        return columnDefs;
    }

    function setInfoWhenChangePage() {
        getColumsNameOfDBContactos().forEach(element => {
            var headElement = document.getElementById(`db_metadata_head_${element}`);
            var elementsByClass = document.getElementsByClassName(`db_metadata_body_${element}`);
            if (document.getElementById(`check_${element}`).checked) {
                headElement.classList.remove('d-none');
                for (const e of elementsByClass) {
                    e.classList.remove('d-none');
                }
            } else {
                headElement.classList.add('d-none');
                for (const e of elementsByClass) {
                    e.classList.add('d-none');
                }
            }
        });
    }

    function obtener_nodos_acciones(row, data, index) {
        var pk_contacto = data[0];
        var nodos_acciones = [];

        // se crean los nodos que permiten el acceso a la modificación del contacto
        var $modificar_contacto = create_node('a', {
            'class': 'btn btn-light btn-sm',
            'role': 'button',
            'href': Urls.contacto_update(pk_campana, pk_contacto),
        });
        var $span_modificar_contacto = create_node('span', {
            'class': 'icon-pencil',
            'aria-hidden': 'true',
            'title': gettext('Modificar'),
        });
        $modificar_contacto.append($span_modificar_contacto);
        nodos_acciones.push($modificar_contacto);

        // se crean los nodos que permiten llamar al contacto solo si no son Preview ni Dialer
        if (tipo_campana != PREVIEW && tipo_campana != DIALER) {
            var $llamar_contacto = create_node('button', {
                'class': 'contacto-lista btn btn-light btn-sm',
            });
            var $span_llamar_contacto = create_node('span', {
                'class': 'icon-phone',
                'aria-hidden': 'true',
                'title': gettext('Llamar'),
            });
            $llamar_contacto.append($span_llamar_contacto);
            $llamar_contacto
                .on('click', function () {
                    $inputContacto.attr('value', pk_contacto);
                    $('#lista_llamar_contacto').trigger('click');
                });
            nodos_acciones.push($llamar_contacto);
        }
        /*
        else {
          var $llamar_contacto = create_node('button', {
            'class': 'contacto-lista btn btn-light btn-sm',
          });
        }/**/

        // se crean los nodos que permiten mandar un mail al contacto
        // (actualmente esta funcionalidad está sin implementar)
        var $mailto_contacto = create_node('a', {
            'class': 'btn btn-light btn-sm',
            'role': 'button',
            'href': '#',
        });
        var $span_mailto_contacto = create_node('span', {
            'class': 'icon-solid-mail',
            'aria-hidden': 'true',
            'title': gettext('Enviar email'),
        });
        $mailto_contacto.append($span_mailto_contacto);
        nodos_acciones.push($mailto_contacto);

        return nodos_acciones;
    }

    $('#agenteContactosTable')
        .DataTable({
            // Convierte a datatable la tabla de contactos
            'createdRow': function (row, data, index) {
                var nodo_acciones = obtener_nodos_acciones(row, data, index);
                $(row).find('td').last().append(nodo_acciones);
                length_row_data = data.length;
            },
            'columnDefs': [
                ...getColumnDefsByMetadata()
            ],
            serverSide: true,
            processing: true,
            lengthChange: true,
            ajax: {
                url: Urls.api_contactos_campana(pk_campana),
                data: function(data) {
                    delete data.columns;
                }
            },
            ordering: false,
            paging: true,
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
    // Evento para pintar la información que se
    // quedó seleccionada al momento de pintar el datatable
    $('#agenteContactosTable').on('draw.dt', () => {
        setInfoWhenChangePage();
    });
});
