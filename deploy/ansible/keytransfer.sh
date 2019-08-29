#!/bin/bash

#
# Autor: Andres Felipe Macias
#
arg1=$1
current_directory=`pwd`
ips=()
servidores=()
is_interface=false
SSHtransfer() {
  while true; do
      echo -e "Transfering the public key to $servidor server \n"
      ssh-copy-id -p $ssh_port -i /root/.ssh/id_rsa.pub -o ConnectTimeout=10 root@$ip
      ResultadoSSH=`echo $?`
      sleep 2
      if [ $ResultadoSSH -eq 0 ];then
          echo "######################################################"
          echo "##   The public key was transferred successfully    ##"
          echo "######################################################"
          echo -e "\n"
          break
      else
          echo -e "\n"
          echo "########################################################################"
          echo "##  There was a problem transfering the key, check it and try again   ##"
          echo "########################################################################"
          echo -e "\n"
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
      if [[ $i != *"ansible_connection=local"* ]] && [[ -z $arg1 ]]; then
        servidor="`echo $i |awk -F \" \" '{print $1}'`"
        ip="`echo $i |awk -F \" \" '{print $4}' |awk -F "=" '{print $2}' `"
        ssh_port="`echo $i |grep ansible_ssh_port |awk -F " " '{print $2}'|awk -F "=" '{print $2}'`"
        SSHtransfer
      elif [[ $i != *"ansible_connection=local"* ]] && [[ ! -z $arg1 ]]; then
        exit 2
      elif [[ $i == *"ansible_connection=local"* ]] && [[ -z $arg1 ]]; then
        exit 3
      elif  [ ! -z $arg1 ]; then
        interfaces=`ip addr show | awk '/inet.*brd/{print $NF}'`
        array=($interfaces)
        for element in "${array[@]}"; do
          if [ "$arg1" == "$element" ]; then is_interface=true; fi
        done
        if [ "$is_interface" == "false" ]; then exit 4; fi
      fi
      for j in `seq 1 $servers_ammount`; do
        ips[j]=$ip
        servidores[j]=$servidor
        echo -e "    Hostname: ${servidores[j]} -  IP: ${ips[j]}" >> /var/tmp/servers_installed
      done
      fi
  done
}
Info
