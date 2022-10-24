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

function progresoDescarga() {
  // Al hacer click en el boton de submit, si el valor del form no es vacío
  // muestro el gif de espera
  $('#id_registrar').click(function () {
    var valorSeleccionIdioma = $('#id_audio_idioma').val()
    if (valorSeleccionIdioma != '') {
      $('#waitGif').attr('class', '');
    }
  });
}

$(document).ready(function () {
  progresoDescarga();
});
