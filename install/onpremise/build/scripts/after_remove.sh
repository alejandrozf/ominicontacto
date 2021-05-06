#!/bin/bash
# Script that runs after kamailio remove
INSTALL_PREFIX=/opt/omnileads
echo "Removing omniapp folders"
rm -rf $INSTALL_PREFIX/{wombat-json,backup,bin,media_root/reporte_campana,static,log,run,addons,ominicontacto}
