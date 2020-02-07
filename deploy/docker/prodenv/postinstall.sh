#!/bin/bash
iptables=$(which iptables)
DOCKER=$(which docker) 
CIP=$($DOCKER inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' oml-asterisk-prodenv)
$iptables -A DOCKER -t nat -p udp -m udp ! -i docker0 --dport $RTP_START:$RTP_FINISH -j DNAT --to-destination $CIP:$RTP_START-$RTP_FINISH
$iptables -A DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport $RTP_START:$RTP_FINISH -j ACCEPT
$iptables -A POSTROUTING -t nat -p udp -m udp -s $CIP/32 -d $CIP/32 --dport $RTP_START:$RTP_FINISH -j MASQUERADE
$iptables -I INPUT -p udp -j RTPENGINE --id 0
sleep 15
$DOCKER cp /home/omnileads/prodenv/odbc.ini  oml-asterisk-prodenv:/etc/odbc.ini
$DOCKER cp  /home/omnileads/prodenv/kamailio-local.cfg oml-kamailio-prodenv:/etc/kamailio/kamailio-local.cfg
$DOCKER restart oml-asterisk-prodenv
$DOCKER restart oml-kamailio-prodenv