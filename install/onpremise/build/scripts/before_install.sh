#!/bin/bash
# Script that runs before install of kamailio
echo "Checking if omnileads user/group exists"
existe=$(grep -c '^omnileads:' /etc/passwd)
if [ $existe -eq 0 ]; then
  echo "Creating omnileads group"
  groupadd omnileads
  echo "Creating omnileads user"
  useradd omnileads -d /opt/omnileads -s /bin/bash -g omnileads
else
  echo "The user/group omnileads already exists"
fi
if grep -Fxq "omnileads ALL=(ALL:ALL)  ALL" /etc/sudoers; then
  echo "Sudo file already modified"
else
  echo "Modifying sudoers file"
  echo "omnileads ALL=(ALL:ALL)  ALL" >> /etc/sudoers
  echo "omnileads ALL=(ALL) NOPASSWD: /usr/sbin/asterisk" >> /etc/sudoers
fi
# Line for adding cp command on sudoers file, used by backup/restore script
if grep -Fxq "omnileads ALL=(ALL) NOPASSWD: /usr/sbin/asterisk" /etc/sudoers; then
  sed -i "s/omnileads ALL=(ALL) NOPASSWD: \/usr\/sbin\/asterisk/omnileads ALL=(ALL) NOPASSWD: \/usr\/bin\/rsync, \/usr\/sbin\/asterisk, \/usr\/bin\/sed/g" /etc/sudoers
fi
if grep -Fxq "omnileads ALL=(ALL) NOPASSWD: /usr/bin/rsync, /usr/sbin/asterisk" /etc/sudoers; then
  sed -i "s/omnileads ALL=(ALL) NOPASSWD: \/usr\/bin\/rsync, \/usr\/sbin\/asterisk/omnileads ALL=(ALL) NOPASSWD: \/usr\/bin\/rsync, \/usr\/sbin\/asterisk, \/usr\/bin\/sed/g" /etc/sudoers
fi
echo "Applying sysctl optimizations for OMniLeads"
sysctl -w net.core.somaxconn=2048
sysctl vm.overcommit_memory=1
if grep -Fxq "net.core.somaxconn=2048" /etc/sysctl.conf; then
  echo "Sysctl.conf file already modified"
else
  echo "Writing the optimizations in /etc/sysctl.conf"
  echo "net.core.somaxconn=2048" >> /etc/sysctl.conf
  echo "vm.overcommit_memory=1" >> /etc/sysctl.conf
fi
