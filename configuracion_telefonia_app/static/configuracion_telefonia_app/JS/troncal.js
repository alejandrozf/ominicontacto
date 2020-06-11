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

/*
 * Código js relacionado con vista de creación/modificación de Troncales SIP
 */

var templates = [
    {
        'name': 'Internet SIP Trunk',
        'template':
          'type=wizard\n\
transport=trunk-nat-transport\n\
accepts_registrations=no\n\
accepts_auth=no\n\
sends_registrations=yes\n\
sends_auth=yes\n\
endpoint/rtp_symmetric=yes\n\
endpoint/force_rport=yes\n\
endpoint/rewrite_contact=yes\n\
endpoint/timers=yes\n\
aor/qualify_frequency=60\n\
endpoint/allow=alaw,ulaw\n\
endpoint/dtmf_mode=rfc4733\n\
endpoint/context=from-pstn\n\
remote_hosts=****IPADDR-or-FQDN:PORT****\n\
endpoint/from_user=****YOUR SIP_USERNAME****\n\
outbound_auth/username=****YOUR SIP_USERNAME****\n\
outbound_auth/password=****YOUR SIP_PASSWORD****'
    },
    {
        'name': 'Dedicated SIP Trunk',
        'template':
          'type=wizard\n\
transport=trunk-transport\n\
accepts_registrations=no\n\
accepts_auth=no\n\
sends_registrations=no\n\
sends_auth=no\n\
endpoint/rtp_symmetric=no\n\
endpoint/force_rport=no\n\
endpoint/rewrite_contact=no\n\
aor/qualify_frequency=60\n\
endpoint/allow=alaw,ulaw\n\
endpoint/dtmf_mode=rfc4733\n\
endpoint/timers=yes\n\
endpoint/language=es\n\
endpoint/context=from-pstn\n\
remote_hosts=****IPADDR-or-FQDN:PORT****\n\
endpoint/from_user=****YOUR SIP_USER****',
    },
    {
        'name': 'PBX OmniLeads (LAN)',
        'template':
          'type=wizard\n\
transport=trunk-transport\n\
accepts_registrations=no\n\
sends_auth=yes\n\
sends_registrations=no\n\
accepts_auth=yes\n\
endpoint/rtp_symmetric=no\n\
endpoint/force_rport=no\n\
endpoint/rewrite_contact=no\n\
endpoint/timers=yes\n\
aor/qualify_frequency=60\n\
endpoint/allow=alaw,ulaw\n\
endpoint/dtmf_mode=rfc4733\n\
endpoint/context=from-pbx\n\
remote_hosts=****IPADDR-or-FQDN:PORT****\n\
inbound_auth/username=****SIP_USER PBX -> OML****\n\
inbound_auth/password=****SIP_PASS PBX -> OML****\n\
outbound_auth/username=****SIP_USER OML -> PBX****\n\
outbound_auth/password=****SIP_PASS OML -> PBX****\n\
endpoint/from_user=****SIP_USER OML -> PBX****',
    },
    {
        'name': 'PBX OmniLeads (NAT)',
        'template':
        'type=wizard\n\
transport=trunk-nat-transport\n\
accepts_registrations=no\n\
sends_auth=yes\n\
sends_registrations=yes\n\
accepts_auth=yes\n\
endpoint/rtp_symmetric=yes\n\
endpoint/force_rport=yes\n\
endpoint/rewrite_contact=yes\n\
endpoint/timers=yes\n\
aor/qualify_frequency=60\n\
endpoint/allow=alaw,ulaw\n\
endpoint/dtmf_mode=rfc4733\n\
endpoint/context=from-pbx\n\
remote_hosts=****IPADDR-or-FQDN:PORT****\n\
inbound_auth/username=****SIP_USER PBX -> OML****\n\
inbound_auth/password=****SIP_PASS PBX -> OML****\n\
outbound_auth/username=****SIP_USER OML -> PBX****\n\
outbound_auth/password=****SIP_PASS OML -> PBX****\n\
endpoint/from_user=****SIP_USER OML -> PBX****',
    },
    {
        'name': 'OML Docker',
        'template':
        'type=wizard\n\
transport=trunk-nat-docker-transport\n\
accepts_registrations=no\n\
sends_auth=yes\n\
sends_registrations=yes\n\
accepts_auth=no\n\
endpoint/rtp_symmetric=yes\n\
endpoint/force_rport=yes\n\
endpoint/rewrite_contact=yes\n\
endpoint/timers=yes\n\
aor/qualify_frequency=60\n\
endpoint/allow=alaw,ulaw\n\
endpoint/dtmf_mode=rfc4733\n\
endpoint/context=from-pbx\n\
remote_hosts=****IPADDR-or-FQDN:PORT****\n\
inbound_auth/username=****SIP_USER PBX -> OML****\n\
inbound_auth/password=****SIP_PASS PBX -> OML****\n\
outbound_auth/username=****SIP_USER OML -> PBX****\n\
outbound_auth/password=****SIP_PASS OML -> PBX****\n\
endpoint/from_user=****SIP_USER OML -> PBX****',
    },
    {
        'name': 'Custom',
        'template': '',
    },
];

function manageTechnologyChange(clear_on_chansip){
    var opcion = $('#id_tecnologia').val();
    // Opcion 0 es para Chansip
    if (opcion == '0') {
        if(clear_on_chansip){
            $('#id_text_config').val('');
        }
        $('#id_register_string').removeAttr('disabled');
        $('#template_options').hide();
    }
    else {
        $('#id_register_string').attr('disabled', true);
        $('#template_options').show();
    }
}

function applyTemplate(i){
    $('#id_text_config').val(templates[i].template);
}

$(function() {
    // Create Template Options
    var options = $('<div id="template_options"><br>\
        <label>Cargar template:</label></div>');

    for (var i in templates){
        var template = templates[i];
        var butt = $('<input type="button" value="' + template.name + '" id="template-buttons" class="btn btn-primary" />');
        options.append(butt);
        options.append('<br>');
        butt.on('click', {'template': template.template}, function(e) {
            $('#id_text_config').val(e.data.template);
        });
    }
    $('#id_tecnologia').parent().append(options);

    $('#id_tecnologia').change(function() {
        manageTechnologyChange(true);
    });
    manageTechnologyChange(false);
});
