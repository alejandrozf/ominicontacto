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
/* global Urls */

$(function () {
    var campanasPreviewActivas = $('#campanas_preview_activas').val();
    var $nuevoContactoPreview = $('#nuevoContactoPreview');
    if (campanasPreviewActivas == 'True') {
        $nuevoContactoPreview.attr('class', 'btn btn-info btn-sm');
    }

    if ($nuevoContactoPreview.length > 0) {
        $nuevoContactoPreview.on('click', function () {
            var ultimaCampPreviewSeleccionada = sessionStorage.getItem('ultimaCampanaPreviewSeleccionada');
            $('#dataView').attr('src', Urls.campana_preview_activas_miembro());
            setTimeout(function () {
                $('#dataView').contents().find('#preview-' + ultimaCampPreviewSeleccionada).click();
            }, 1000);
        });
    }
});
