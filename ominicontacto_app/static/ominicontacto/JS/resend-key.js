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

/* global Urls gettext */

/**
 * Script para reenviar una llave
 */
$('#sendKey').on('click', function(){
    $.post(Urls.reenviar_key_registro(), function(data){
        if (data.status == 'OK') {
            $.growl.notice({
                'title': gettext('Llave enviada por email'),
                'message': gettext('Los datos de la llave fueron enviados con éxito a su email'),
                'duration': 5000});
        }
        else {
            if (data.status == 'ERROR-CONN-SAAS') {
                $.growl.error({
                    'title': gettext('Error en conexión externa'),
                    'message': gettext('No fue posible conectar con el servidor de llaves'),
                    'duration': 5000});
            }
            else {
                $.growl.error({
                    'title': gettext('Error autenticación'),
                    'message': gettext('Los datos enviados desde la instancia no son correctos'),
                    'duration': 5000});
            }
        }
    }).fail(function() {
        $.growl.error({
            'title': gettext('Error de conexión'),
            'message': gettext('No se pudo conectar al servidor'),
            'duration': 5000});
    });
});
