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
/*
 * Funciones JS para ser usadas en los distintos ABMs de creación de nodos y rutas entrantes
 */
/* exported nodosEntrantesCambioPorTipo */

var url_obtener_destinos_tipo = '/configuracion_telefonia/ruta_entrante/obtener_destinos_tipo/';
var opcionEnBlanco = '<option value="">---------</option>';

function asignarNodosEntrantesPorTipo($tipoDestino, $destinoEntrante) {
  // Extrae todos los nodos extrantes de un tipo y los inserta en un nodo y
  // escribe la información del tipo en
  var tipo_destino = $tipoDestino.val();
  if (tipo_destino == '') {
    $destinoEntrante.html('');
    $destinoEntrante.attr('tipo', tipo_destino);
  }
  else {
    $.get(url_obtener_destinos_tipo + tipo_destino, function (data) {
      $destinoEntrante.html('');
      $destinoEntrante.append(opcionEnBlanco);
      $.each(data, function (key, value) {
        $destinoEntrante.append('<option value='+ value.id +'>' + value.nombre + '</option>');
      });
    });
    $destinoEntrante.attr('tipo', tipo_destino);
  }
}

function nodosEntrantesCambioPorTipo($tipoDestino, $destinoEntrante) {
  // permite que cuando se seleccione un valor tipo de nodo entrante en '$tipoDestino' se
  // obtengan todos los valores de nodos de destinos entrantes en '$destinoEntrante'
  // además sólo habilita el nodo '$destinoEntrante' cuando '$tipoDestino' toma valor
  var valorInicialDestino = $destinoEntrante.val();
  if ((valorInicialDestino == null) || (valorInicialDestino == '')) {
    $destinoEntrante.prop('disabled', 'disabled');
  }

  $tipoDestino.on('change', function () {
    $destinoEntrante.prop('disabled', false);
    asignarNodosEntrantesPorTipo($tipoDestino, $destinoEntrante);
  });
}
