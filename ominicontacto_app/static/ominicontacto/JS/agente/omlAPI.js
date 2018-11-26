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

    changeStatus(status, idagente) {
    	// TODO: Este request debería ser por POST
    	// {% url 'agente_cambiar_estado' status id_agente %}
        $.ajax({
            type: "get",
            url: "/agente/cambiar_estado?estado=" + status + "&pk_agente=" + idagente,
            contentType: "text/html",
            success: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                debugger;
                console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
            }
        });
    };

    getCampanasActivas(callback) {
        $.ajax({
            type: "get",
            url: "/service/campana/activas/",
            contentType: "text/html",
            success: function(msg) {
            	callback(msg.campanas);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
            }
        });
    };

    getAgentes(callback) {
        $.ajax({
            type: "get",
            url: "/service/agente/otros_agentes_de_grupo/",
            contentType: "text/html",
            success: function(msg) {
            	callback(msg.agentes);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
            }
        });
    };

    marcarLlamada(descripcion, uuid_llamada) {
        var URl = "grabacion/marcar/";
        var post_data = {
            "uid": uuid_llamada,
            "descripcion": descripcion
        };
        $.ajax({
            url: URl,
            type: 'POST',
            dataType: 'json',
            data: post_data,
            succes: function(msg) {

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
            }
        });
    };

    guardarDuracionLlamada(duracion, idagt, numero_telefono, tipo_llamada, callback) {
        $.ajax({
            type: "get",
            url: "/duracion/llamada/",
            contentType: "text/html",
            data: "duracion=" + duracion + "&agente=" + idagt + "&numero_telefono=" + numero_telefono + "&tipo_llamada=" + tipo_llamada,
            success: function(msg) {
            	callback(msg);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                debugger;
                console.log("Error al ejecutar => " + textStatus + " - " + errorThrown);
            }
        });
    };
}
