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

class OMLAPI {

	constructor() {

	};

    changeStatus(status, id_agente) {
        // {% url 'agente_cambiar_estado'%}
        var URL = Urls.agente_cambiar_estado(status, id_agente);
    	// TODO: Este request debería ser por POST
    	// {% url 'agente_cambiar_estado' status id_agente %}
        $.ajax({
            type: "get",
            url: URL,
//            url: "/agente/cambiar_estado?estado=" + status + "&pk_agente=" + idagente,
            contentType: "text/html",
            success: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
            }
        });
    };

    getCampanasActivas(callback) {
        // {% url 'service_campanas_activas'%}
        var URL = Urls.service_campanas_activas();
        $.ajax({
            type: "get",
            url: URL,
            contentType: "text/html",
            success: function(msg) {
            	callback(msg.campanas);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
            }
        });
    };

    getAgentes(callback) {
        // {% url 'service_agentes_de_grupo'%}
        var URL = Urls.service_agentes_de_grupo();
        $.ajax({
            type: "get",
            url: URL,
            contentType: "text/html",
            success: function(msg) {
            	callback(msg.agentes);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
            }
        });
    };

    marcarLlamada(descripcion, uuid_llamada) {
        // {% url 'grabacion_marcar'%}
        var URL = Urls.grabacion_marcar();
        // var URL = "grabacion/marcar/";
        var post_data = {
            "callid": uuid_llamada,
            "descripcion": descripcion
        };
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
            }
        });
    };

    updateCallHistory(callback) {
        // {% url 'historico_de_llamadas_de_agente'%}
        var URL = Urls.historico_de_llamadas_de_agente();
        $.ajax({
            type: "get",
            url: URL,
            contentType: "text/html",
            success: function(msg) {
                callback(msg);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
            }
        });
    };

    startClick2Call(agent_id, campaign_id, campaign_type, contact_id, phone, click2call_type) {
        // {% url 'agente_llamar_contacto'%}
        var URL = Urls.agente_llamar_contacto();
        var post_data = {
            "pk_agente": agent_id,
            "pk_campana": campaign_id,
            "tipo_campana": campaign_type,
            "pk_contacto": contact_id,
            "telefono": phone,
            "click2call_type": click2call_type,
        };
        $.ajax({
            url: URL,
            type: 'POST',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
                alert(gettext("No se pudo iniciar la llamada. Intente Nuevamente."))
            }
        });
    };

    startCallOutsideCampaign(destination_type, destination) {
        // {% url 'agente_llamar_sin_campana'%}
        var URL = Urls.agente_llamar_sin_campana();
        var post_data = {
            "tipo_destino": destination_type,
            "destino": destination,
        };
        $.ajax({
            url: URL,
            type: 'POST',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(gettext("Error al ejecutar => ") + textStatus + " - " + errorThrown);
                alert(gettext("No se pudo iniciar la llamada. Intente Nuevamente."))
            }
        });
    };

}
