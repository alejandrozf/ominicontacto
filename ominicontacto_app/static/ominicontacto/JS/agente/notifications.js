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



class NotificationSocket
{
    constructor() {
        /* eventsCallbacks */
        this.eventsCallbacks = {
            onNotificationForzarDespausa: $.Callbacks(),
            onNotificationForzarPausa: $.Callbacks(),
            onNotificationPhoneJsLogout: $.Callbacks()
        };
    }

    startNotificationSocket() {
        const url = 'wss://' + window.location.host + '/channels/agent-console';
        const rws = new ReconnectingWebSocket(url, [], {
            connectionTimeout: 10000,
            maxReconnectionDelay: 3000,
            minReconnectionDelay: 1000,
        });
        var self = this;
        rws.addEventListener('message', function(e) {
            const data = JSON.parse(e.data);
            if (data.type == 'pause')
                self.eventsCallbacks.onNotificationForzarPausa.fire(data.args);
            if (data.type == 'unpause')
                self.eventsCallbacks.onNotificationForzarDespausa.fire(data.args);
            if (data.type == 'logout')
                self.eventsCallbacks.onNotificationPhoneJsLogout.fire();
                
        });
      
    }

}
