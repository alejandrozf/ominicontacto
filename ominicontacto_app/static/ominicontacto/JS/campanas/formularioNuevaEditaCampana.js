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
$(function () {
  inicializarCampoSitioExterno();

  $('#id_0-bd_contacto').each(function() {
      $(this).select2();});
});

function inicializarCampoSitioExterno() {
  var $sistema_externo = $('#id_0-sistema_externo');
  $sistema_externo.on('change', actualizarEstadoIdExterno);
  actualizarEstadoIdExterno();
}

function actualizarEstadoIdExterno() {
  var $sistema_externo = $('#id_0-sistema_externo');
  var $id_externo = $('#id_0-id_externo');
  if ($sistema_externo.val() == ''){
    $id_externo.prop('disabled', true);
    $id_externo.val('');
  }
  else
    $id_externo.prop('disabled', false)
}
