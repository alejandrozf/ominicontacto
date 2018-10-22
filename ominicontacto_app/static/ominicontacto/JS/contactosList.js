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
$(document).ready(function(){

  var $inputContacto = $('#pk_contacto');
  var pk_campana = $('#pk_campana').attr('value');
  var tipo_campana = $('#campana_tipo').attr('value');

  function create_node (type, attrs) {
    var $node = $("<" + type + "/>", attrs);
    return $node;
  }

  function obtener_nodos_acciones (row, data, index) {
    var pk_contacto = data[0];
    var nodos_acciones = [];

    // se crean los nodos que permiten el acceso a la modificación del contacto
    var $modificar_contacto = create_node('a', {
          'class': 'btn btn-light btn-sm',
          'role': 'button',
          'href': '/contacto/'+ pk_contacto + '/update/',
        });
    var $span_modificar_contacto = create_node('span', {
          'class': 'icon-pencil',
          'aria-hidden': 'true',
          'title': gettext('Modificar'),
        });
    $modificar_contacto.append($span_modificar_contacto);
    nodos_acciones.push($modificar_contacto);

    // se crean los nodos que permiten llamar al contacto solo si no son Preview ni Dialer
    if (tipo_campana != 'Preview' && tipo_campana != 'Dialer') {
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
        .on('click', function() {
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
    .DataTable( {
      // Convierte a datatable la tabla de contactos
      "createdRow": function ( row, data, index ) {
        nodo_acciones = obtener_nodos_acciones(row, data, index);
        $(row).find('td').last().append(nodo_acciones);
      },
      serverSide: true,
      processing: true,
      ajax: '/api/campana/' + pk_campana + '/contactos/',
      ordering: false,
      paging: true,
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
});
