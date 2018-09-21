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
