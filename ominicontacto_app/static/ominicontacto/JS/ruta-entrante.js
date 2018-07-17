/*
 * Código js relacionado con vista de creación/modificación de una ruta entrante
 */

/* global nodosEntrantesCambioPorTipo */

var $tipoDestino = $('#tipo_destino');
var $destino = $('#destino');

// cuando se escoge un tipo de nodo destino se despliegan en el campo selector de destinos
// todos los nodos destinos de este tipo
nodosEntrantesCambioPorTipo($tipoDestino, $destino);
