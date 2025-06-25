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
/* global gettext */
/* global OMLAPI */
/* global tableToDataTable */

var oml_api = undefined;
var campana_list_reload_interval = undefined;
var wombat_reloader = undefined;

$(function(){
    oml_api = new OMLAPI();
    configure_campaign_actions_links();
    if ($('#wombat_state').length > 0)
        wombat_reloader = new WombatReloader();
    
    tableToDataTable(
        [
            null,
            { orderable: false },
            { orderable: false },
            { orderable: false },
            { orderable: false },
            { orderable: false },
            { orderable: false },
            { orderable: false },
        ]
    );
});

$(function(){

    startWindowRefresh();
    $('.btn-submit').click(function (){
        var campana_id = $(this).attr('id');
        var action = $(this).attr('name');
        submit_form(campana_id, action);
    });

    function submit_form(campana_id, action){
        $('#campana_id').val(campana_id);
        $('#form_estados_campanas').attr('action', action);
        $('#form_estados_campanas').submit();
    }
});

function startWindowRefresh() {
    campana_list_reload_interval = setInterval(function() {
        window.location.reload(true);
    }, 180000);
}

function stopWindowRefresh() {
    if (campana_list_reload_interval != undefined) {
        clearInterval(campana_list_reload_interval);
        campana_list_reload_interval = undefined;
    }
}

function mostrar_detalle_campana(pk_campana) {
    if ($('#modal_ventana').attr('first-time') == 'true'){
        $('#modal_ventana').attr('first-time', 'false');
    }
    else{
        $('#modal_ventana').fadeOut('slow');
    }
    $('#modal_ventana').html('');

    oml_api.getDialerCampaignDetails(pk_campana, function(data) {
        $('#modal_ventana').html(data);
        $('#modal_ventana').fadeIn('slow');
    });
}

function mostrar_campanas_dialer_ocultas() {
    oml_api.getHiddenDialerCampaigns(function (data) {
        $('#t_body_borradas').html(data);
    });
}

function configure_campaign_actions_links(){
    $('.action_for_campaign').on('click', submit_action_for_campaign);
}

function submit_action_for_campaign() {
    let url = $(this).attr('value');
    $('#option_dialer').attr('action', url);
    let campaign_id = $(this).attr('camp-id');
    if (campaign_id != undefined)
        $('#campana_pk').val(campaign_id);
    else
        $('#campana_pk').val('');
    $('#option_dialer').submit();
}


const STATE_DOWN = 'DOWN';
const STATE_STARTING = 'STARTING';
const STATE_READY = 'READY';

class WombatReloader {

    constructor() {
        this.wombat_state = $('#wombat_state').val();
        this.setUp();
    }

    setUp() {
        if (this.wombat_state != undefined) {
            var self = this;
            $('#submit_restart_wombat').click(function() {self.reload_wombat();});
            $('#submit_stop_wombat').click(function() {self.stop_wombat();});
            $('#submit_start_wombat').click(function() {self.start_wombat();});
            $('#submit_sync_wombat').click(function() {self.getWombatState();});
            this.configureButtons();
        }
    }

    configureButtons() {
        if (this.wombat_state == STATE_READY) {
            this.enableReload();
        }
        else {
            this.disableReload();
            let delta = $('#wombat_uptime').html();
            delta = delta.replaceAll(new RegExp('[${():}]', 'gi'), '');
            delta = delta.replace(/^.*,(?=[^,]*$)/, '');
            if (delta > 30){
                $('#submit_restart_wombat').prop('disabled', false);
            }
        }
    }

    reload_wombat() {
        stopWindowRefresh();
        var self = this;
        this.disableReload();
        oml_api.restartWombatDialer(
            function(data) { self.reloadingStart(data); },
            function(data) { self.reloadError(data); }
        );
    }

    reloadingStart(data) {
        var self = this;
        this.wombat_state = data['OML-state'];
        setTimeout(function() { self.getReloadState(); }, 10000);
    }

    reloadError(data) {
        var self = this;
        if (data===undefined) {
            $.growl.error({
                'title': gettext('Error de conexión'),
                'message': gettext('No fue posible refrescar.'),
                'duration': 5000});
            startWindowRefresh();
        }
        else {
            this.wombat_state = data['OML-state'];
            console.log(data['message']);
            setTimeout(function() { self.getReloadState(); }, 10000);
        }
    }

    getReloadState() {
        var self = this;
        oml_api.getWombatState(
            function(data) { self.checkReloadState(data); },
            function(data) { self.reloadError(data); }
        );
    }

    checkReloadState(data) {
console.log(data)
        if (data['OML-state'] == STATE_READY) {
            this.wombat_state = data['OML-state'];
            $('#wombat_uptime').html('(' + data['uptime'] + ')');
            this.reloaded();
        }
        else {
            var self = this;
            setTimeout(function() { self.getReloadState(); }, 16000);
        }
    }

    getWombatState() {
        var self = this;
        oml_api.getWombatState(
            function(data) { self.updateState(data); },
            function(data) { self.commandError(data); }
        );
    }

    stop_wombat() {
        var self = this;
        oml_api.stopWombatDialer(
            function(data) { self.updateState(data); },
            function(data) { self.commandError(data); }
        );
    }

    start_wombat() {
        var self = this;
        oml_api.startWombatDialer(
            function(data) { self.updateState(data); },
            function(data) { self.commandError(data); }
        );
    }

    updateState(data) {
        console.log('UPDATE STATE:');
        console.log(data);
        console.log(data['state']);
        $('#wombat_uptime').html('(' + data['uptime'] + ')');
        if (data['state'] == 'READY'){
            this.enableReload();
            $('#submit_stop_wombat').prop('disabled', false);
            $('#submit_start_wombat').prop('disabled', true);
        }
        else if (data['state'] == 'DOWN'){
            this.disableReload();
            $('#wombat_state_label').html(gettext('Detenido'));
            $('#submit_stop_wombat').prop('disabled', true);
            $('#submit_start_wombat').prop('disabled', false);
        }
        else {
            this.disableReload();
            $('#wombat_state_label').html(data['state']);
            $('#submit_stop_wombat').prop('disabled', false);
            $('#submit_start_wombat').prop('disabled', false);
        }

    }

    commandError(error) {
        $.growl.error({
            'title': gettext('Error en el comando'),
            'message': gettext('Fallo en la ejecución del comando.'),
            'duration': 5000});
    }


    reloaded(data) {
        this.enableReload();
        startWindowRefresh();
    }

    enableReload() {
        $('#wombat_state_label').html(gettext('Listo'));
        $('#wombat_state_label').css('color', 'green');
        $('#submit_restart_wombat').prop('disabled', false);
        
    }

    disableReload() {
        $('#wombat_state_label').html(gettext('Refrescando'));
        $('#wombat_state_label').css('color', 'red');
        $('#submit_restart_wombat').prop('disabled', true);
    }

}

