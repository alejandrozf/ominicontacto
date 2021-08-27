#!/bin/bash
# Script that runs after kamailio remove
INSTALL_PREFIX=/opt/omnileads
echo "Removing omniapp folders"
rm -rf $INSTALL_PREFIX/{wombat-json,media_root/reporte_campana,static,log,run,ominicontacto}
