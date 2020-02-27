#!/bin/bash
iptables=$(which iptables)
DOCKER=$(which docker) 
RTP_START=[[ rtp_start_port ]]
RTP_FINISH=[[ rtp_finish_port ]]
CIP=$($DOCKER inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' oml-[[ asterisk_fqdn ]]-[[ customer ]])
$iptables -A DOCKER -t nat -p udp -m udp ! -i docker0 --dport $RTP_START:$RTP_FINISH -j DNAT --to-destination $CIP:$RTP_START-$RTP_FINISH
$iptables -A DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport $RTP_START:$RTP_FINISH -j ACCEPT
$iptables -A POSTROUTING -t nat -p udp -m udp -s $CIP/32 -d $CIP/32 --dport $RTP_START:$RTP_FINISH -j MASQUERADE
sleep 15
$DOCKER cp /home/[[ usuario ]]/[[ customer ]]/odbc.ini  oml-[[ asterisk_fqdn ]]-[[ customer ]]:/etc/odbc.ini
$DOCKER cp /home/[[ usuario ]]/[[ customer ]]/oml_res_odbc.conf  oml-[[ asterisk_fqdn ]]-[[ customer ]]:/etc/asterisk/oml_res_odbc.conf
$DOCKER cp  /home/[[ usuario ]]/[[ customer ]]/kamailio-local.cfg oml-[[ kamailio_fqdn ]]-[[ customer ]]:/etc/kamailio/kamailio-local.cfg
$DOCKER restart oml-[[ asterisk_fqdn ]]-[[ customer ]]
$DOCKER restart oml-[[ kamailio_fqdn ]]-[[ customer ]]