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

