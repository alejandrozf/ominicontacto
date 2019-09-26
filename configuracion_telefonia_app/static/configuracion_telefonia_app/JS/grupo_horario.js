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
/* global REMOVER_CAMPO */
/* global AGREGAR_VALIDACION */
$(function() {
    $('.tiempo').datetimepicker({format: 'HH:mm'});
});
var validacionTiempo = $('#validaciontiempo').val();
$('.validacionTiempoTr').formset({
    addText: AGREGAR_VALIDACION,
    deleteText: REMOVER_CAMPO,
    prefix: validacionTiempo,
    addCssClass: 'btn btn-outline-primary',
    deleteCssClass: 'btn btn-outline-danger deleteFormset',
    formCssClass: 'dynamic-formset',
    added: function (row) {
        $(row.find('.tiempo')).each(function () {
            $(this).datetimepicker({format: 'HH:mm'});
        });
    }
});
