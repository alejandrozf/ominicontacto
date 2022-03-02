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



class NotificationSocket
{
    constructor() {
        /* eventsCallbacks */
        this.eventsCallbacks = {
            onNotificationForzarDespausa: $.Callbacks()
        };
    }

    startNotificationSocket() {
        /** Bloqueo funcionalidad oml-2103 por problemas con django-channels  **/
        return;
    }

    startNotificationSocket2() {
        var notificationSocket = new WebSocket('wss://' + window.location.host + '/channels/agent-console');
        var self = this;
        notificationSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type == 'unpause-call')
                self.eventsCallbacks.onNotificationForzarDespausa.fire(data.args);
                
        };
      
    }

}
