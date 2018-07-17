/*
 * Código js relacionado con vista de creación/modificación de un nodo de ruta entrante de tipo validación
   fecha/hora
 */

/* global nodosEntrantesCambioPorTipo */

var $tipoDestinoMatch = $('#tipoDestinoMatch');
var $destinoMatch = $('#destinoMatch');
var $tipoDestinoNoMatch = $('#tipoDestinoNoMatch');
var $destinoNoMatch = $('#destinoNoMatch');

// cuando se escoge un tipo de nodo destino se despliegan en el campo selector de destinos
// todos los nodos destinos de este tipo
nodosEntrantesCambioPorTipo($tipoDestinoMatch, $destinoMatch);
nodosEntrantesCambioPorTipo($tipoDestinoNoMatch, $destinoNoMatch);
