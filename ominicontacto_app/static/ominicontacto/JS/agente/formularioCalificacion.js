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
    var $mostrarFormCalificacion = $('#mostrarFormCalificacion');
    var $opcion_calificar = $('#id_opcion_calificacion');
    $opcion_calificar.removeAttr('required');
    $mostrarFormCalificacion.on('click', function () {
        $('div[data="toHide"]').each( function () {
            var $formCalificacion = $(this);
            var checkedValue = $mostrarFormCalificacion.is(':checked');
            // se pasa el valor de la selección o no del formulario al input
            // por otra parte, de acuerdo a este valor, se muestra o no el formulario de calificación
            $mostrarFormCalificacion.val(checkedValue);
            if (checkedValue == false) {
                $formCalificacion.attr('class', 'hidden');
            }
            else {
                $formCalificacion.attr('class', '');
                $opcion_calificar.attr('required');
            }
        });
    });
});
