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

/

/*
 * Script que realiza bindings a todos los botones de mostrar/ocultar en la lista de formularios,
 * en cada click actualiza el estado del atributo 'oculto' de formulario en cuestión en BD y modifica convenientemente
 * la UI del elemento
 */

function actualizarFormulario(id, $this, mostrarOcultos) {
  var url = Urls.formulario_mostrar_ocultar(id);
  $.post(url).success(function(data) {
    actualizarNodoFormulario($this, data, mostrarOcultos);
  });
}

function actualizarNodoFormulario($this, data, mostrarOcultos) {
  var oculto = data.oculto;

  if (mostrarOcultos == "True" && oculto == false) {
    // cambiar icono a "ocultar"
    var $span = $this.find('span');
    $span.attr('class', 'icon icon-eye');
    $span.text(gettext('Ocultar'));
  }
  else {
    if (mostrarOcultos == "True" && oculto == true) {
      // cambiar icono a "mostrar"
      var $span = $this.find('span');
      $span.attr('class', 'icon icon-eye-slash');
      $span.text(gettext('Mostrar'));
    }
    else {
      // sólo se muestran los 'visibles', se elimina el nodo
      // directamente
      $this.parents('.formularioElem').remove();
    }
  }
}


$('.mostrarOcultar').each(function (index, value) {
  var $this = $(this);
  var id = $this.attr('id');
  var mostrarOcultos = $this.attr('data-mostrar-ocultos');
  $this.on('click', function () {
    actualizarFormulario(id, $this, mostrarOcultos);
  });
});
