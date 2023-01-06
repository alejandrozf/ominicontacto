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

/*
Sincroniza la seleccion del campo de desactivacion en el formulario principal
y actualiza el valor en los campos correspondientes a este mismo valor
*/

$(function() {
    var $campoDesactivacion = $('#campoDesactivacion');
    var $campoDesactivacionExport = $('#campoDesactivacionExport');
    var $campoDesactivacionImport = $('#campoDesactivacionImport');

    $campoDesactivacion.on('change', function () {
        var valorCampoDesactivacion = $(this).val();
        $campoDesactivacionExport.val(valorCampoDesactivacion);
        $campoDesactivacionImport.val(valorCampoDesactivacion);
    });

    var valorCampoDesactivacion = $campoDesactivacion.val();
    $campoDesactivacionExport.val(valorCampoDesactivacion);
    $campoDesactivacionImport.val(valorCampoDesactivacion);
});
