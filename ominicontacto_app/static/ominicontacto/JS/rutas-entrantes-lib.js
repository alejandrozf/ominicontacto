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
