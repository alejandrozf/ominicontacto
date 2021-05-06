#!/bin/bash
iptables=$(which iptables)
DOCKER=$(which docker)
RTP_START="40000"
RTP_FINISH="50000"
CIP=$($DOCKER inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' omlacd)
source .env
CUSTOMER=$COMPOSE_PROJECT_NAME

start() {
  $iptables -A DOCKER -t nat -p udp -m udp ! -i docker0 --dport ${RTP_START}:${RTP_FINISH} -j DNAT --to-destination ${CIP}:${RTP_START}-${RTP_FINISH}
  $iptables -A DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport ${RTP_START}:${RTP_FINISH} -j ACCEPT
  $iptables -A POSTROUTING -t nat -p udp -m udp -s ${CIP}/32 -d ${CIP}/32 --dport ${RTP_START}:${RTP_FINISH} -j MASQUERADE
  sleep 10
  if [ ! -f /tmp/ast_conf_files ]; then
    mkdir -p /tmp/ast_conf_files
  fi
  cp -a /tmp/ast_conf_files/*_{custom.conf,override.conf} /opt/omnileads/volumes/${CUSTOMER}_ast_conf_files/_data
  rm -rf /tmp/*_{custom.conf,override.conf}
}

stop(){
  $iptables -D DOCKER -p udp -m udp -d ${CIP}/32 ! -i docker0 -o docker0 --dport ${RTP_START}:${RTP_FINISH} -j ACCEPT
  # Moviendo los archivos custom y override de asterisk a un directorio temporal
  cp -a /opt/omnileads/volumes/prodenv_ast_conf_files/_data/*_{custom.conf,override.conf} /tmp/ast_conf_files
  $DOCKER volume rm ${CUSTOMER}_ast_conf_files
}

$@
