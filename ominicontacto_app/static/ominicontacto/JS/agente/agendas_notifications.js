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
/* globals gettext */


class AgendasNotifier {
    constructor(next_agendas) {
        this.set_agendas(next_agendas);
    }

    set_agendas(next_agendas) {
        this.num_agendas = 0;
        clearTimeout(this.timeout);
        this.timeout = undefined;
        this.agendas = next_agendas;
        this.process_notifications();
    }

    process_notifications(showing_current=false) {
        var now = new Date();
        var min_diff = undefined;
        this.num_agendas = 0;
        for (var i in this.agendas) {
            var date = new Date(this.agendas[i]);
            if (now < date){
                this.num_agendas++;
                var diff = date - now;
                if (min_diff == undefined)
                    min_diff = diff;
                else {
                    min_diff = Math.min(min_diff, diff);
                }
            }
        }
        if (showing_current) {
            // Add 1 for the current agenda being showed
            $('#num_agendas').html(` (${this.num_agendas + 1})`);
        }
        else{
            if (this.num_agendas == 0)
                this.clear_notifications();
            else
                $('#num_agendas').html(` (${this.num_agendas})`);       
        }
        if (this.num_agendas > 0) {
            var self = this;
            this.timeout = setTimeout(function() {self.show_notifications();}, min_diff);
        }
    }

    show_notifications() {
        $.growl.warning({'title': gettext('Agenda programada'),
            'message': gettext('Tiene una agenda programada para este momento.'),
            'duration': 5000});
        $('#btn_agendas').fadeTo(100, 0.1).fadeTo(200, 1.0).fadeTo(100, 0.1).fadeTo(200, 1.0).fadeTo(100, 0.1).fadeTo(200, 1.0);
        $('#btn_agendas').addClass('btn-warning-agenda');

        this.process_notifications(true);
    }

    clear_notifications() {
        $('#btn_agendas').removeClass('btn-warning-agenda');
        $('#num_agendas').html('');
    }
}