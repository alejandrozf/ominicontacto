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
/* global gettext */

$(function () {
    var configuracion_sitio_externo = $('#configuracionSitioExterno').val();
    if (configuracion_sitio_externo){
        configuracion_sitio_externo = JSON.parse(configuracion_sitio_externo);
        configurarInteraccion(configuracion_sitio_externo);
    }
});

function configurarInteraccion(configuracion_sitio_externo){

    if (!configuracion_sitio_externo.formato_es_JSON){
        var form = $('#form_sitio_externo');
        form.prop('action', configuracion_sitio_externo.url);
        form.prop('method', configuracion_sitio_externo.metodo);
        if (configuracion_sitio_externo.metodo == 'POST'){
            form.prop('enctype', configuracion_sitio_externo.formato);
        }
        if (configuracion_sitio_externo.abre_pestana)
            form.prop('target', '_blank');
        $.each(configuracion_sitio_externo.parametros, function(nombre, valor) {
            form.append('<input type="hidden" name="' + nombre + '" value="' + valor + '" />');
        });
        if (configuracion_sitio_externo.dispara_agente){
            $('#submit_interaccion').prop('type', 'submit');
        }
        else {
            form.submit();
        }
    }
    else {
        if (configuracion_sitio_externo.dispara_agente){
            $('#submit_interaccion').prop('type', 'button');
            $('#submit_interaccion').click(function(){ejecutarInteraccionJSON(configuracion_sitio_externo);});
        }
        else {
            ejecutarInteraccionJSON(configuracion_sitio_externo);
        }
    }
}

function ejecutarInteraccionJSON(configuracion_sitio_externo){
    
    return jQuery.ajax({
        url: configuracion_sitio_externo.url,
        type: 'POST',
        contentType:'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(configuracion_sitio_externo.parametros),
        success: function(data) {
            $.growl.notice({
                'title': gettext('Interacción con sitio externo'),
                'message': gettext('OK'),
                'duration': 5000});
        },
        error: function(data) {
            $.growl.error({
                'title': gettext('Error al ejecutar Interacción con sitio externo'),
                'message': gettext('Consulte a su supervisor'),
                'duration': 5000});
        }
    });
}
