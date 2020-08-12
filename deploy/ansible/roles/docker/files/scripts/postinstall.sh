#!/bin/bash
iptables=$(which iptables)
DOCKER=$(which docker)
RTP_START=[[ rtp_start_port ]]
RTP_FINISH=[[ rtp_finish_port ]]
CIP=$($DOCKER inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' oml-[[ asterisk_fqdn ]]-[[ customer ]])

start() {
  $iptables -A DOCKER -t nat -p udp -m udp ! -i docker0 --dport $RTP_START:$RTP_FINISH -j DNAT --to-destination $CIP:$RTP_START-$RTP_FINISH
  $iptables -A DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport $RTP_START:$RTP_FINISH -j ACCEPT
  $iptables -A POSTROUTING -t nat -p udp -m udp -s $CIP/32 -d $CIP/32 --dport $RTP_START:$RTP_FINISH -j MASQUERADE
  sleep 10
  cp -a /tmp/*_{custom.conf,override.conf} [[ install_prefix ]]volumes/prodenv_ast_conf_files/_data
  rm -rf /tmp/*_{custom.conf,override.conf}
}

stop(){
  $iptables -D DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport $RTP_START:$RTP_FINISH -j ACCEPT
  # Moviendo los archivos custom y override de asterisk a un directorio temporal
  cp -a [[ install_prefix ]]volumes/prodenv_ast_conf_files/_data/*_{custom.conf,override.conf} /tmp
  $DOCKER volume rm prodenv_ast_conf_files
}

$@
