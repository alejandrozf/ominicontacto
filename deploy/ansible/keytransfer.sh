#!/bin/bash

#
# Autor: Andres Felipe Macias
#
arg1=$1
current_directory=`pwd`
ips=()
servidores=()
SSHtransfer() {
  while true; do
      echo -e "Transfering the public key to $servidor server \n"
      ssh-copy-id -p $ssh_port -i ~/.ssh/id_rsa.pub -o ConnectTimeout=10 root@$ip
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
  inventory_copy_location="`cd $current_directory/../../.. && pwd`"
  echo "Creating a copy of inventory file in $inventory_copy_location"
  my_inventory=$current_directory/../../../my_inventory
  if [ ! -f  $my_inventory ]; then
    cp inventory $my_inventory
  else
    cp $my_inventory inventory
  fi
  cd $current_directory
  if [ "$arg1" == "--aio" ]; then
    servers_ammount="`cat inventory | grep "ansible_host=" | grep -v \"cluster server\" |wc -l`"
  elif [ "$arg1" == "--cluster" ]; then
    servers_ammount="`cat inventory | grep "ansible_host=" | grep \"cluster server\" |wc -l`"
  fi
  cat /dev/null > /var/tmp/servers_installed
  for i in `seq 1 $servers_ammount`; do
    if [ "$arg1" == "--aio" ]; then
      line="`cat inventory | grep ansible_host | grep -v \"cluster server\" | sed -n ${i}p`"
    elif [ "$arg1" == "--cluster" ]; then
      line="`cat inventory | grep ansible_ssh_port | grep \"cluster server\" | sed -n ${i}p`"
    fi
    servidor="`echo $line |awk -F \" \" '{print $1}'`"
    ip="`echo $line |awk -F \" \" '{print $4}' |awk -F "=" '{print $2}' `"
    ssh_port="`echo $line |grep ansible_ssh_port |awk -F " " '{print $2}'|awk -F "=" '{print $2}'`"
    ips[i]=$ip
    servidores[i]=$servidor
    if [[ $line = \#* ]]; then
      continue
    else
      echo -e "    Hostname: ${servidores[i]} -  IP: ${ips[i]}" >> /var/tmp/servers_installed
      if [[ $line != *"ansible_connection=local"* ]]; then
        SSHtransfer
      fi
    fi
  done
  printf "\033c"
}
Info
