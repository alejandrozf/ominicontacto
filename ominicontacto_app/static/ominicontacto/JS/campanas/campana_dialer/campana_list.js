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
/* global gettext interpolate */
/* global OMLAPI */
/* global tableToDataTable */
/* global OmnidialerStats */

var oml_api = undefined;
var campana_list_reload_interval = undefined;
var wombat_reloader = undefined;
var stats = undefined;
var wombat_enabled = undefined;
var campaigns_data = undefined;
var hidden_campaigns = {};
var campaignInModal = undefined;
var manager = undefined;

$(function(){
    campaigns_data = JSON.parse($('#campaigns_data').prop('innerText'));
    wombat_enabled = JSON.parse($('#wombat_enabled').prop('innerText'));
    oml_api = new OMLAPI();
    manager = new CampaignButtonManager();
    configure_campaign_actions_links();

    if (wombat_enabled){
        if ($('#wombat_state').length > 0)
            wombat_reloader = new WombatReloader();
    }
    else {
        var notifications = new NotificationSocket();
        notifications.startNotificationSocket();
        stats = new OmnidialerStatsUpdater(notifications);
    }
    $('#modal_ventana').on('hidden.bs.modal', function(e) {
        campaignInModal = undefined;
    });
    
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

    if (wombat_enabled) {
        startWindowRefresh();
    }
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
        campaignInModal = pk_campana;
        $('#modal_ventana').html(data);
        $('#modal_ventana').fadeIn('slow');
    });
}

function mostrar_campanas_dialer_ocultas() {
    oml_api.getHiddenDialerCampaigns(function (data) {
        $('#campaign_block_4').replaceWith(data);
        hidden_campaigns = JSON.parse($('#hidden_campaigns').prop('innerText'));
        for (let camp_id in hidden_campaigns){
            manager.setCampaignButtons(camp_id, '4');
        }
    });
}

function configure_campaign_actions_links(){
    for (let camp_id in campaigns_data){
        manager.setCampaignButtons(camp_id, campaigns_data[camp_id].status);
    }
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
            this.configureButtons();
        }
    }

    configureButtons() {
        if (this.wombat_state == STATE_READY) {
            this.enableReload();
        }
        else {
            this.disableReload();
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
        this.wombat_state = data['WD-state'];
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
            this.wombat_state = data['WD-state'];
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
        if (data['WD-state'] == STATE_READY) {
            this.wombat_state = data['WD-state'];
            $('#wombat_uptime').html('(' + data['uptime'] + ')');
            this.reloaded();
        }
        else {
            var self = this;
            setTimeout(function() { self.getReloadState(); }, 16000);
        }
    }

    reloaded(data) {
        this.enableReload();
        startWindowRefresh();
    }

    enableReload() {
        $('#wombat_ready').show();
        $('#wombat_reloading').hide();
        $('#submit_restart_wombat').prop('disabled', false);
    }

    disableReload() {
        $('#wombat_ready').hide();
        $('#wombat_reloading').show();
        $('#submit_restart_wombat').prop('disabled', true);
    }
}


class NotificationSocket {
    constructor() {
        /* eventsCallbacks */
        this.eventsCallbacks = {
            onNotification: $.Callbacks(),
        };
    }

    startNotificationSocket() {
        const url = 'wss://' + window.location.host + '/channels/omnidialer';
        const rws = new ReconnectingWebSocket(url, [], {
            connectionTimeout: 10000,
            maxReconnectionDelay: 3000,
            minReconnectionDelay: 1000,
        });
        var self = this;
        rws.addEventListener('message', function(e) {
            const event_data = JSON.parse(e.data);
            if (event_data.type == 'stats')
                self.eventsCallbacks.onNotification.fire(event_data.args);
        });
    }
}

class OmnidialerStatsUpdater {
    constructor(notifications) {
        let self = this;
        this.notifications = notifications;
        this.notifications.eventsCallbacks.onNotification.add(function(event_data){
            switch (event_data.type) {
            case 'STATS':
                self.updateStats(event_data.camp_id, event_data);
                break;
            case 'EXPIRATION':
                self.notifyExpiration(event_data.camp_id);
                break;
            case 'CONTACTS_CONSUMED':
                self.notifyContactsConsumed(event_data.camp_id);
                break;
            case 'ALMOST_NO_CONTACTS':
                self.notifyAlmostNoContacts(event_data.camp_id);
                break;
            case 'STATUSCHANGE':
                self.notifyStatusChange(event_data.camp_id, event_data.status);
                break;
            // case 'EVENT':
            //     self.notifyEvent(event_data.camp_id);
            //     break;
            // default:
            //     console.log('Irrelevant type: ', event_data.type);
            //     break;
            }
        });
    }

    notifyExpiration(camp_id){
        $.growl.notice({
            'title': campaigns_data[camp_id]['name'],
            message: gettext('La campaña ha expirado'),
            duration: 5000
        });
    }

    notifyContactsConsumed(camp_id){
        $.growl.notice({
            'title': campaigns_data[camp_id]['name'],
            message: gettext('Se han consumido todos los contactos de la campaña'),
            duration: 5000
        });
    }

    notifyAlmostNoContacts(camp_id){
        $.growl.warning({
            'title': campaigns_data[camp_id]['name'],
            message: gettext('Pocos contactos por llamar'),
            duration: 5000
        });
    }

    notifyStatusChange(camp_id, status){
        $('#camp-data-' + camp_id).appendTo('#campaign_table_' + status + ' tbody');
        manager.setCampaignButtons(camp_id, status);
        // # 'type': 'STATUSCHANGE', 'camp_id': id_campaign, 'status': new_status
    }

    updateStats(camp_id, stats_data){
        if (campaignInModal == camp_id){
            if (Object.hasOwn(stats_data, 'ATTEMPTED_CALLS')){
                $('#id_ATTEMPTED_CALLS').html(stats_data.ATTEMPTED_CALLS);
            }
            if (Object.hasOwn(stats_data, 'CONTACTED SUCCESSFULLY')){
                let finalized_ok = Number(stats_data['CONTACTED SUCCESSFULLY']);
                $('#id_CONTACTED_SUCCESSFULLY').val(finalized_ok);
                let finalized = finalized_ok + Number($('#id_FINALIZED_WITH_NO_CONTACT').val());
                $('#id_FINALIZED').html(finalized);
            }
            if (Object.hasOwn(stats_data, 'FINALIZED WITH NO CONTACT')){
                let finalized_no = Number(stats_data['FINALIZED WITH NO CONTACT']);
                $('#id_FINALIZED_WITH_NO_CONTACT').val(finalized_no);
                let finalized = finalized_no + Number($('#id_CONTACTED_SUCCESSFULLY').val());
                $('#id_FINALIZED').html(finalized);
            }
            if (Object.hasOwn(stats_data, 'PENDING_INITIAL_CONTACT_ATTEMPTS')){
                let pending_initial = Number(stats_data['PENDING_INITIAL_CONTACT_ATTEMPTS']);
                $('#id_PENDING_INITIAL_CONTACT_ATTEMPTS').val(pending_initial);
                let pending_attempts = Number($('#id_NO_CONTACTS_WITH_PENDING_ATTEMPTS').html());
                let pending = pending_initial + pending_attempts;
                $('#id_PENDING').html(pending);
            }
            if (Object.hasOwn(stats_data, 'NO CONTACTS WITH PENDING ATTEMPTS')){
                let pending_attempts = Number(stats_data['NO CONTACTS WITH PENDING ATTEMPTS']);
                $('#id_NO_CONTACTS_WITH_PENDING_ATTEMPTS').html(pending_attempts);
                let pending_initial = Number($('#id_PENDING_INITIAL_CONTACT_ATTEMPTS').val());
                let pending = pending_attempts + pending_initial;
                $('#id_PENDING').html(pending);
            }
        }
    }

    notifyEvent(camp_id, event_data){
        // # 'type': 'EVENT', 'camp_id': id_campaign, 'data': ari_event_data
    }

}

class CampaignButtonManager {
    /* Sets campaign controls according to Campaign State */
    setCampaignButtons(camp_id, camp_status){
        let visible_items = STATE_ITEMS[camp_status];
        ITEMS.forEach(item => {
            if (visible_items.indexOf(item) == -1) {
                $('#camp-' + camp_id + '-' + item).hide();
            }
            else {
                $('#camp-' + camp_id + '-' + item).show();
            }
            // For deleted campaigns
            if (item == 'hide'){
                let hidden = Object.hasOwn(hidden_campaigns, camp_id) && hidden_campaigns[camp_id];
                if (hidden){
                    $('#camp-' + camp_id + '-hide').hide();
                }
            }
            if (item == 'show'){
                let hidden = Object.hasOwn(hidden_campaigns, camp_id) && hidden_campaigns[camp_id];
                if (!hidden){
                    $('#camp-' + camp_id + '-show').hide();
                }
            }
        });
    }
}

const ITEMS = [
    'name', 'detail', 'database', 'start', 'activate', 'edit', 'queue', 'pause', 'recycle', 'end',
    'grant', 'add-one', 'add-many', 'block', 'agendas', 'incidence', 'config', 'delete',
    'show', 'hide'];

const STATE_ITEMS = {
    // Active
    '2': [
        'detail', 'edit', 'queue', 'pause', 'recycle', 'end', 'grant', 'add-one', 'add-many',
        'block', 'agendas', 'incidence', 'config', 'delete'
    ],
    // Paused
    '5': ['detail', 'activate', 'edit', 'queue', 'recycle', 'end', 'grant', 'incidence', 'config',
        'delete'
    ],
    // Inactive
    '6': ['name', 'database', 'start', 'edit', 'queue', 'end', 'grant', 'incidence', 'config',
        'delete'
    ],
    // Ended
    '3': ['detail', 'database', 'start', 'recycle', 'grant', 'delete'
    ],
    // Deleted
    '4': ['name', 'incidence', 'config', 'delete', 'show', 'hide'
    ],
};
