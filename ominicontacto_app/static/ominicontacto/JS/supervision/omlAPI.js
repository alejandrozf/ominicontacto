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
/* global gettext */
/* exported OMLAPI */

class OMLAPI {

    constructor() {

    }

    getDialerCampaignDetails(campaign_id, callback_ok) {
        var URL = Urls.campana_dialer_detalle_wombat();
        $.get(URL, {pk_campana: campaign_id}, callback_ok);
    }

    getHiddenDialerCampaigns(callback_ok) {
        $.get(Urls.campana_dialer_mostrar_ocultas(), callback_ok);
    }

    restartWombatDialer(callback_ok, callback_error) {
        var URL = Urls.api_restart_wombat();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            success: function(data){
                if (data['status'] == 'ERROR') {
                    callback_error(data);
                }
                else
                    callback_ok(data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

    getWombatState(callback_ok, callback_error) {
        var URL = Urls.api_wombat_state();
        $.ajax({
            url: URL,
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data['status'] == 'ERROR') {
                    callback_error(data);
                }
                else
                    callback_ok(data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                callback_error();
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

}