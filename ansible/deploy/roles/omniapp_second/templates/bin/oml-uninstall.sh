#!/bin/bash

echo "###############################################################"
echo "##                OMniLeads uninstall script                 ##"
echo "###############################################################"
echo ""
echo "Once this script finish there is no recovery of OMniLeads in this server"
echo -en "Are you sure do yo want to uninstall? [Y/N] "; read respuesta
if [[ $respuesta == "Y" ]] || [[ $respuesta == "y" ]] || [[ $respuesta == "yes" ]]; then
  echo "ok ..... deleting ...."
elif [[ $respuesta == "N" ]] || [[ $respuesta == "n" ]] || [[ $respuesta == "no" ]]; then
  exit 0
else
  echo "Invalid option, retry"
  exit 1
fi
echo "** [oml-uninstall] Stopping Omnileads services"
service omnileads stop
service asterisk stop
service kamailio stop
service nginx stop
service rtpengine stop
service redis stop
echo "** [oml-uninstall] Deleting Omnileads database"
psql -U {{ usuario }} -d postgres -c "DROP DATABASE {{ postgres_database }}"
service mariadb stop
service postgresql-{{ postgresql_version }} stop
service queuemetrics stop
echo "** [oml-uninstall] Erasing all content in {{ install_prefix }} (this will include recordings)"
rm -rf {{ install_prefix }}
echo "** [oml-uninstall] Erasing rtpengine binary"
rm -rf /usr/local/bin/rtpengine
echo "** [oml-uninstall] Erasing asterisk and kamailio binaries"
rm -rf /usr/sbin/asterisk /usr/sbin/kamcmd /usr/sbin/kamctl
echo "** [oml-uninstall] Erasing wombat dialer application"
rm -rf /usr/local/queuemetrics/tomcat/webapps/wombat
echo "** [oml-uninstall] Erasing nginx configuration for OMniLeads"
rm -rf /etc/nginx/conf.d/ominicontacto.conf
echo "** [oml-uninstall] Uninstalling services"
yum remove postgresql96* redis nginx tomcat8 mariadb-server -y
