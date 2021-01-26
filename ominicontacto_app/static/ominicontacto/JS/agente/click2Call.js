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
/* global Urls gettext*/

class Click2CallDispatcher {
    /*
    *  Esta clase será la encargada de despachar los pedidos de click to call que ejecute el
    *  usuario. Se deshabilita mientras el UserAgent no este registrado, cuando haya una llamada
    *  en curso, etc...
    */
    constructor (oml_api, agent_id) {
        this.AGENT = 'AGENT';
        this.EXTERNAL = 'EXTERNAL';
        this.enabled = false;
        this.oml_api = oml_api;
        this.agent_id = agent_id;
        this.verificando_calificacion = false;
        // Cooldown to avoid click2call requests flooding
        this.click2call_cooldown = undefined;

        this.agent_forces_disposition = $('#obligar-calificacion').val() == 'True';
        this.last_call_configures_force_disposition = false;
        this.last_call_forces_disposition = false;
    }

    enable() {
        this.enabled = true;
        $('#sumTime').css('background-color', 'palegreen');
    }

    disable() {
        this.enabled = false;
        $('#sumTime').css('background-color', 'forestgreen');
    }

    get disposition_forced() {
        if (this.last_call_configures_force_disposition)
            return this.last_call_forces_disposition;
        else
            return this.agent_forces_disposition;
    }

    call_contact(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call'){
        if (!this.enabled || this.verificando_calificacion)
            return;
        if (this.click2call_cooldown){
            console.log('Call disabled. Awaiting cooldown...');
            return;
        }
        if (this.disposition_forced){
            if (this.verificando_calificacion){
                return;
            }
            this.verificando_calificacion = true;
            var self = this;
            this.oml_api.llamadaCalificada(
                function(){
                    self._make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call');
                    self.verificando_calificacion = false;
                },
                function(call_data){
                    self.make_disposition(call_data);
                    self.verificando_calificacion = false;
                },
                function(){
                    alert(gettext('Error al intentar ejecutar el llamado.'));
                    self.verificando_calificacion = false;
                }
            );
        }
        else{
            this._make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call');
        }
    }

    _make_call(campaign_id, campaign_type, contact_id, phone, click2call_type='click2call') {
        if (this.enabled) {
            var self = this;
            this.click2call_cooldown = setTimeout(function() {self.click2call_cooldown = undefined;}, 2000);
            this.oml_api.startClick2Call(this.agent_id, campaign_id, campaign_type,
                contact_id, phone, click2call_type);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }

    make_disposition(calldata){
        $('#obligarCalificarCall').modal('show');
        $('#obligarCalificarCall_submit').click(function(){
            var call_data_json = JSON.stringify(calldata);
            var url = Urls.calificar_llamada(encodeURIComponent(call_data_json));
            $('#dataView').attr('src', url);
            $('#obligarCalificarCall').modal('hide');
        });
    }

    call_agent(agent_id){
        if (this.click2call_cooldown){
            console.log('Call disabled. Awaiting cooldown...');
            return;
        }
        if (this.disposition_forced){
            var self = this;
            if (this.verificando_calificacion){
                return;
            }
            this.verificando_calificacion = true;
            this.oml_api.llamadaCalificada(
                function(){
                    self.make_agent_call(agent_id);
                    self.verificando_calificacion = false;
                },
                function(call_data){
                    $('#modalCallOffCamp').modal('hide');
                    self.make_disposition(call_data);
                    self.verificando_calificacion = false;
                },
                function(){
                    alert(gettext('Error al intentar ejecutar el llamado.'));
                    self.verificando_calificacion = false;
                }
            );
        }
        else{
            this.make_agent_call(agent_id);
        }
    }

    make_agent_call(agent_id) {
        if (this.enabled) {
            var self = this;
            this.click2call_cooldown = setTimeout(function() {self.click2call_cooldown = undefined;}, 2000);
            this.oml_api.startCallOutsideCampaign(this.AGENT, agent_id);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }
    
    call_external(phone){
        if (this.click2call_cooldown){
            console.log('Call disabled. Awaiting cooldown...');
            return;
        }
        if (this.disposition_forced){
            if (this.verificando_calificacion){
                return;
            }
            var self = this;
            this.oml_api.llamadaCalificada(
                function(){
                    self.make_external_call(phone);
                    self.verificando_calificacion = false;
                },
                function(call_data){
                    $('#modalCallOffCamp').modal('hide');
                    self.make_disposition(call_data);
                    self.verificando_calificacion = false;
                },
                function(){
                    alert(gettext('Error al intentar ejecutar el llamado.'));
                    self.verificando_calificacion = false;
                }
            );
        }
        else{
            this.make_external_call(phone);
        }
    }

    make_external_call(phone) {
        if (this.enabled) {
            var self = this;
            this.click2call_cooldown = setTimeout(function() {self.click2call_cooldown = undefined;}, 2000);
            this.oml_api.startCallOutsideCampaign(this.EXTERNAL, phone);
        }
        else {
            console.log('Alertar al usuario que no es posible hacer una click2call');
        }
    }
}
