# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from ominicontacto_app.asterisk_config import AsteriskConfigReloader

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Reescribe los archivos de configuración del sistema a partir de variables de
    entorno
    """

    help = u'Actualiza archivos de configuración del sistema'

    def _escribir_archivo(self, content, ruta_remota):
        f = open(ruta_remota, "w+")
        f.write(content)
        f.close()

    def _actualizar_template_asterisk_oml_manager(self):
        template_asterisk_oml_manager = (
            "[{0}]\n"
            "secret =  {1}\n"
            "deny = 0.0.0.0/0.0.0.0\n"
            "permit = 127.0.0.1/255.255.255.255\n"
            "permit = {2}/255.255.255.255\n"
            "permit = {3}/255.255.255.255\n"
            "read = all\n"
            "write = all\n"
        )
        config_asterisk_oml_manager = template_asterisk_oml_manager.format(
            settings.AMI_USER, settings.AMI_PASSWORD,
            settings.OML_OMNILEADS_IP, settings.DIALER_IP
        )
        ruta_archivo = '{0}/etc/asterisk/oml_manager.conf'.format(settings.ASTERISK_LOCATION)
        self._escribir_archivo(
            config_asterisk_oml_manager, ruta_archivo)

    def _actualizar_template_asterisk_oml_sip_general(self):
        template_asterisk_oml_sip_general = (
            "[agents](!)\n"
            "type=wizard\n"
            "transport=agent-transport\n"
            "accepts_registrations=yes\n"
            "sends_registrations=no\n"
            "accepts_auth=no\n"
            "sends_auth=no\n"
            "endpoint/context=from-oml\n"
            "endpoint/disallow=all\n"
            "endpoint/allow=alaw\n"
            "endpoint/direct_media=no\n"
            "endpoint/force_rport=no\n"
            "endpoint/disable_direct_media_on_nat=yes\n"
            "endpoint/direct_media_method=invite\n"
            "endpoint/ice_support=no\n"
            "endpoint/moh_suggest=default\n"
            "endpoint/send_rpid=yes\n"
            "endpoint/rewrite_contact=yes\n"
            "endpoint/send_pai=yes\n"
            "endpoint/allow_transfer=yes\n"
            "endpoint/trust_id_inbound=yes\n"
            "endpoint/device_state_busy_at=1\n"
            "endpoint/trust_id_outbound=yes\n"
            "endpoint/send_diversion=yes\n"
            "aor/qualify_frequency=30\n"
            "aor/authenticate_qualify=no\n"
            "aor/max_contacts=2\n"
            "aor/remove_existing=yes\n"
            "aor/minimum_expiration=30\n"
            "aor/support_path=yes\n"
            "endpoint/deny=0.0.0.0/0.0.0.0\n"
            "endpoint/permit={0}/255.255.255.255\n"
            "\n"
            "#include oml_pjsip_agents.conf\n"
            "#include oml_pjsip_trunks.conf"
        )
        config_asterisk_oml_sip_general = template_asterisk_oml_sip_general.format(
            settings.KAMAILIO_IP)
        ruta_archivo = '{0}/etc/asterisk/oml_pjsip_wizard.conf'.format(settings.ASTERISK_LOCATION)
        self._escribir_archivo(
            config_asterisk_oml_sip_general, ruta_archivo)

    def _actualizar_archivos_kamailio(self):
        template_config_kamailio = (
            "#!substdef \"!MY_IP_ADDR!{0}!g\"\n"
            "#!substdef \"!MY_DOMAIN!{1}!g\"\n"
            "#!substdef \"!MY_ASTERISK!{2}!g\"\n"
            "#!substdef \"!USER!root!g\"\n"
            "#!substdef \"!RTPENGINE_HOST!{3}!g\"\n"
            "#!substdef \"!REDIS_URL!{4}!g\"\n"

            "#!substdef \"!MY_UDP_PORT!5060!g\"\n"
            "#!substdef \"!MY_TCP_PORT!5060!g\"\n"
            "#!substdef \"!MY_TLS_PORT!5061!g\"\n"
            "#!substdef \"!MY_WS_PORT!1080!g\"\n"
            "#!substdef \"!MY_WSS_PORT!14443!g\"\n"
            "#!substdef \"!MY_MSRP_PORT!6060!g\"\n"
            "#!substdef \"!MY_MSRPTCP_PORT!6061!g\"\n"
            "\n"
            "#!substdef \"!MY_UDP_ADDR!udp:MY_IP_ADDR:MY_UDP_PORT!g\"\n"
            "#!substdef \"!MY_TCP_ADDR!tcp:MY_IP_ADDR:MY_TCP_PORT!g\"\n"
            "#!substdef \"!MY_TLS_ADDR!tls:MY_IP_ADDR:MY_TLS_PORT!g\"\n"
            "#!substdef \"!MY_WS_ADDR!tcp:MY_IP_ADDR:MY_WS_PORT!g\"\n"
            "#!substdef \"!MY_WSS_ADDR!tls:MY_IP_ADDR:MY_WSS_PORT!g\"\n"
            "#!substdef \"!MY_MSRP_ADDR!tls:MY_IP_ADDR:MY_MSRP_PORT!g\"\n"
            "#!substdef \"!MY_MSRPTCP_ADDR!tcp:MY_IP_ADDR:MY_MSRPTCP_PORT!g\"\n"
            "#!substdef \"!MSRP_MIN_EXPIRES!1800!g\"\n"
            "#!substdef \"!MSRP_MAX_EXPIRES!3600!g\"\n"
            "#!substdef \"!INSTALL_PREFIX!!g\"\n"
            "#!substdef \"!MODULES_LOCATION!/usr/lib/x86_64-linux-gnu/kamailio/modules/!g\"\n"
            "#!substdef \"!PKEY_LOCATION!/etc/kamailio/certs/key.pem!g\"\n"
            "#!substdef \"!CERT_LOCATION!/etc/kamailio/certs/cert.pem!g\"\n"
            "#!substdef \"!CA_LOCATION!/etc/kamailio/certs/demoCA/cert.pem!g\"\n"
            "#!substdef \"!SECRET_KEY!SUp3rS3cr3tK3y!g\""
        )
        config_kamailio = template_config_kamailio.format(settings.KAMAILIO_HOSTNAME,
                                                          settings.KAMAILIO_HOSTNAME,
                                                          settings.ASTERISK_HOSTNAME,
                                                          settings.RTPENGINE_HOSTNAME,
                                                          settings.REDIS_HOSTNAME
                                                          )
        ruta_archivo = '{0}/etc/kamailio/kamailio-local.cfg'.format(settings.KAMAILIO_LOCATION)
        self._escribir_archivo(config_kamailio, ruta_archivo)

    def handle(self, *args, **options):
        try:
            # self._actualizar_archivos_kamailio()
            self._actualizar_template_asterisk_oml_manager()
            self._actualizar_template_asterisk_oml_sip_general()
            # regeneramos asterisk con la nueva configuracion
            asterisk_reloader = AsteriskConfigReloader()
            asterisk_reloader.reload_asterisk()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
