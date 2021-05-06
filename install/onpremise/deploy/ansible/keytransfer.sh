#!/bin/bash

#
# Autor: Andres Felipe Macias
#
INTERFACE=$1
KEY=$2
current_directory=`pwd`
ips=()
is_interface=false
SSHtransfer() {
  while true; do
    echo -e "Transfering the public key to $ip server \n"
    if [ "$KEY" != "none" ] && [ ! -z $KEY ]; then OPTIONS+="-o IdentityFile=$KEY"; fi
    ssh-copy-id -p $ssh_port -i /root/.ssh/id_rsa.pub -o stricthostkeychecking=no -o ConnectTimeout=10 ${OPTIONS} $user@$ip
    ResultadoSSH=`echo $?`
    sleep 2
    if [ $ResultadoSSH -eq 0 ];then
      echo "######################################################"
      echo "##   The public key was transferred successfully    ##"
      echo "######################################################"
      break
    else
      echo "########################################################################"
      echo "##  There was a problem transfering the key, check it and try again   ##"
      echo "########################################################################"
      exit 1
    fi
  done
}

Info() {
  cd $current_directory
  cat /dev/null > /var/tmp/servers_installed
  IFS=$'\n'
  servers=( $(cat inventory | grep ansible_user=) )
  for i in ${servers[@]}; do
    if [[ ! $i = \#* ]]; then
      let "servers_ammount=servers_ammount+1"
      if [[ $i != *"ansible_connection=local"* ]] && ([ "$INTERFACE" == "none" ] || [ -z $INTERFACE ]); then
        ip="`echo $i |awk -F \" \" '{print $1}'`"
        ssh_port="`echo $i |grep ansible_ssh_port |awk -F " " '{print $2}'|awk -F "=" '{print $2}'`"
        user="`echo $i |grep ansible_ssh_port |awk -F " " '{print $3}'|awk -F "=" '{print $2}'`"
        if [ -z $IS_CICD ]; then SSHtransfer; fi
      elif [[ $i != *"ansible_connection=local"* ]] && ([ "$INTERFACE" != "none" ] || [ ! -z $INTERFACE ]); then
        exit 2
      elif [[ $i == *"ansible_connection=local"* ]] && ([ "$INTERFACE" == "none" ] || [ -z $INTERFACE ]); then
        exit 3
      elif  [ "$INTERFACE" != "none" ]; then
        interfaces=`ip addr show | awk '/inet.*brd/{print $NF}'`
        array=($interfaces)
        for element in "${array[@]}"; do
          if [ "$INTERFACE" == "$element" ]; then is_interface=true; fi
        done
        if [ "$is_interface" == "false" ]; then exit 4; fi
      fi
      for j in `seq 1 $servers_ammount`; do
        ips[j]=$ip
        echo -e "IP: ${ips[j]}" >> /var/tmp/servers_installed
      done
      fi
  done
}
Info
