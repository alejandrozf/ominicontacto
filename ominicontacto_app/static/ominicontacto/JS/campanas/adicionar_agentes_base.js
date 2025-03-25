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
/* global AGREGAR_AGENTE REMOVER_CAMPO obtenerAgentesGrupos eliminarPrimeraFilaVacia asociarDatosRow*/
var $adicionarAgente = $('#adicionarAgente');
var wizard = $('#wizard').val();
$('.linkFormset').formset({
    addText: AGREGAR_AGENTE,
    deleteText: REMOVER_CAMPO,
    prefix: wizard,
    addCssClass: 'addFormset btn btn-outline-primary',
    deleteCssClass: 'deleteFormset btn btn-outline-danger',
    addMultRows: {'button': $adicionarAgente,
        'function': obtenerAgentesGrupos,
        'post_function': eliminarPrimeraFilaVacia},
    added: function (row) {asociarDatosRow(row);}
});

$(document).ready(function(){
    function sorter(data) {
        return data.sort(function (a, b) {
            if (a.text > b.text) {
                return 1;
            }
            if (a.text < b.text) {
                return -1;
            }
            return 0;
        });
    }
    $('select.form-control').each(function() {
        $(this).select2({sorter});
    });
    $('.addFormset').click(function(){
        $('select.form-control').each(function() {
            $(this).select2({sorter});
        });
    });
});
