/*
 * Código js relacionado con vista de creación/modificación de IVRs
 */

/*  global nodosEntrantesCambioPorTipo */

$(document).ready(function(){
  var $destinoTimeOutTipo = $('#destinoTimeOutTipo');
  var $destinoTimeOut = $('#destinoTimeOut');
  var $destinoInvalido = $('#destinoInvalido');
  var $destinoInvalidoTipo = $('#destinoInvalidoTipo');
  nodosEntrantesCambioPorTipo($destinoTimeOutTipo, $destinoTimeOut);
  nodosEntrantesCambioPorTipo($destinoInvalidoTipo, $destinoInvalido);
  $('.opcionDestinoTr').each(function() {
    var $tipoDestino = $(this).find('.tipoDestino');
    var $destino = $(this).find('.destino');
    nodosEntrantesCambioPorTipo($tipoDestino, $destino);
  });

});
