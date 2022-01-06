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
/* global Urls */
/* global gettext */
/* exported OMLAPI */

class OMLAPI {

    constructor() {

    }

    asteriskLogin(callback_ok, callback_error) {
        var URL = Urls.api_agent_asterisk_login();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            success: function(data){
                if (data['status'] == 'ERROR') {
                    callback_error();
                }
                else
                    callback_ok();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    getCampanasActivas(callback) {
        var URL = Urls.service_campanas_activas();
        $.ajax({
            type: 'get',
            url: URL,
            contentType: 'text/html',
            success: function(msg) {
                callback(msg.campanas);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    getAgentes(callback) {
        var URL = Urls.service_agentes_de_grupo();
        $.ajax({
            type: 'get',
            url: URL,
            contentType: 'text/html',
            success: function(msg) {
                callback(msg.agentes);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    makePause(pause_id, callback_ok, callback_error) {
        var URL = Urls.api_make_pause();
        var post_data = {
            'pause_id': pause_id
        };
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: post_data,
            success: function(data){
                if (data['status'] == 'ERROR') {
                    callback_error();
                }
                else
                    callback_ok();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    makeUnpause(pause_id, callback_ok, callback_error) {
        var URL = Urls.api_make_unpause();
        var post_data = {
            'pause_id': pause_id
        };
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: post_data,
            success: function(data){
                if (data['status'] == 'ERROR') {
                    callback_error();
                }
                else
                    callback_ok();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    marcarLlamada(descripcion, uuid_llamada) {
        var URL = Urls.grabacion_marcar();
        var post_data = {
            'callid': uuid_llamada,
            'descripcion': descripcion
        };
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    updateCallHistory(callback) {
        var URL = Urls.historico_de_llamadas_de_agente();
        $.ajax({
            type: 'get',
            url: URL,
            contentType: 'text/html',
            success: function(msg) {
                callback(msg);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    startClick2Call(agent_id, campaign_id, campaign_type, contact_id, phone, click2call_type) {
        var URL = Urls.agente_llamar_contacto();
        var post_data = {
            'pk_agente': agent_id,
            'pk_campana': campaign_id,
            'tipo_campana': campaign_type,
            'pk_contacto': contact_id,
            'telefono': phone,
            'click2call_type': click2call_type,
            '404_on_error': true,
        };
        $.ajax({
            url: URL,
            type: 'POST',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
                alert(gettext('No se pudo iniciar la llamada. Consulte con su Administrador.'));
            }
        });
    }

    startCallOutsideCampaign(destination_type, destination) {
        var URL = Urls.agente_llamar_sin_campana();
        var post_data = {
            'tipo_destino': destination_type,
            'destino': destination,
        };
        $.ajax({
            url: URL,
            type: 'POST',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
                alert(gettext('No se pudo iniciar la llamada. Intente Nuevamente.'));
            }
        });
    }

    sendKeepAlive() {
        var URL = Urls.view_blanco();
        $.ajax({
            url: URL,
            type: 'GET',
            succes: function(msg) {
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    llamadaCalificada(callback_calificada, callback_no_calificada, callback_gestion_form, callback_error) {
        var URL = Urls.api_status_calificacion_llamada();
        $.ajax({
            url: URL,
            type: 'POST',
            success: function(data){
                if (data['calificada'] == 'True'){
                    callback_calificada();
                }
                else if (data['calldata'] == undefined){
                    callback_calificada();
                }
                else if (data['gestion'] == 'True'){
                    var id_calificacion = JSON.parse(data['id_calificacion']);
                    callback_gestion_form(id_calificacion);
                }
                else{
                    var call_data = JSON.parse(data['calldata']);
                    callback_no_calificada(call_data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error => ') + textStatus + ' - ' + errorThrown);
            }

        });
        
    }

    eventHold(){
        var URL = Urls.api_evento_hold();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            success: function(msg){
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });

    }

    eventRinging(ringing=true){
        var URL = Urls.api_make_ringing();
        var post_data = {
            'ringing': ringing,
        };
        $.ajax({
            url: URL,
            type: 'POST',
            data: post_data,
            success: function(msg){
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });

    }
}
