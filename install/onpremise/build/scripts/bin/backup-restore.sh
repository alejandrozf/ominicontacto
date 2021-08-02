#!/bin/bash
# Backup and restore script for OMniLeads

# Variables initialization
BinDate="`which date`"
BinPgDump="`which pg_dump`"
BinPgRestore="`which pg_restore`"
Date="`${BinDate} +%y%m%d`"
Hour="`${BinDate} +%H%M%S`"
InstallationPrefix="`cat /etc/profile.d/omnileads_envars.sh|grep 'INSTALL_PREFIX='|awk -F'=' '{print $2}'`"
AsteriskLocation="${InstallationPrefix}/asterisk"
KamailioLocation="${InstallationPrefix}/kamailio"
##########################

# Functions definition

# Function for creating backup
Backup() {
  TmpDirectory="/tmp/${Date}-${Hour}-oml-backup/${Date}-${Hour}-oml-backup"
  mkdir -p ${TmpDirectory}
  cd ${TmpDirectory}

  # OMniLeads application backup
  echo "Creating backup: OMniLeads application..."
  mkdir -p ${TmpDirectory}/omniapp
  cp -a ${InstallationPrefix}/media_root/ ${TmpDirectory}/omniapp
  if [ -f ${InstallationPrefix}/bin/addons_installed.sh ];then
    source ${InstallationPrefix}/bin/addons_installed.sh
    cp -a ${InstallationPrefix}/bin/addons_installed.sh ${TmpDirectory}/omniapp
    echo "Creating backup: OMniLeads addons..."
    for Addon in "${ADDONS_INSTALLED[@]}";do
      cp -a ${InstallationPrefix}/addons/${Addon} ${TmpDirectory}/omniapp
    done
  fi
  echo "Creating backup: File omnileads_envars.sh..."
  cp -a /etc/profile.d/omnileads_envars.sh ${TmpDirectory}/omniapp/omnileads_envars.sh.backup
  tar czvf ${TmpDirectory}/omniapp.tar.gz omniapp > /dev/null 2>&1
  rm -rf ${TmpDirectory}/omniapp/
  sleep 3

  # Asterisk backup
  echo "Creating backup: Asterisk..."
  mkdir -p ${TmpDirectory}/asterisk
  mkdir -p ${TmpDirectory}/asterisk/etc
  mkdir -p ${TmpDirectory}/asterisk/agi-bin
  mkdir -p ${TmpDirectory}/asterisk/sounds
  cp -a --preserve=links ${AsteriskLocation}/etc/asterisk/*custom* ${TmpDirectory}/asterisk/etc
  cp -a --preserve=links ${AsteriskLocation}/etc/asterisk/*override* ${TmpDirectory}/asterisk/etc
  cp -a ${AsteriskLocation}/var/lib/asterisk/agi-bin/*.py ${TmpDirectory}/asterisk/agi-bin
  cp -a ${AsteriskLocation}/var/lib/asterisk/sounds/* ${TmpDirectory}/asterisk/sounds
  tar czvf ${TmpDirectory}/asterisk.tar.gz asterisk > /dev/null 2>&1
  rm -rf ${TmpDirectory}/asterisk/
  sleep 3

  # Kamailio backup
  echo "Creating backup: Kamailio..."
  mkdir ${TmpDirectory}/kamailio
  cp -a --preserve=links ${KamailioLocation}/etc/ ${TmpDirectory}/kamailio
  tar czvf ${TmpDirectory}/kamailio.tar.gz kamailio > /dev/null 2>&1
  rm -rf ${TmpDirectory}/kamailio/
  sleep 3

  # Database backup, if it's included
  if [ "${NoDatabase}" != "True" ];then
    echo "Creating backup: Database..."
    Database="`cat /etc/profile.d/omnileads_envars.sh|grep 'PGDATABASE='|awk -F'=' '{print $2}'`"
    mkdir ${TmpDirectory}/postgresql
    ${BinPgDump} -F t ${Database} -f ${TmpDirectory}/postgresql/database_backup
    tar czvf ${TmpDirectory}/postgresql.tar.gz postgresql > /dev/null 2>&1
    rm -rf ${TmpDirectory}/postgresql/
    sleep 3
  fi

  # Creation of final backup file
  cd /tmp/${Date}-${Hour}-oml-backup/
  tar czvf ${Date}-${Hour}-oml-backup.tar.gz ${Date}-${Hour}-oml-backup > /dev/null 2>&1
  mv ${Date}-${Hour}-oml-backup.tar.gz ${InstallationPrefix}/backup
  rm -rf /tmp/${Date}-${Hour}-oml-backup/

  BackupFile="`basename ${InstallationPrefix}/backup/${Date}-${Hour}*`"
  echo -e "Backup done!"
  echo -e "Backup file created: ${InstallationPrefix}/backup/${BackupFile}"
  echo -e "To restore this backup file: ./backup-restore.sh --restore=${BackupFile}"
}

# Function for restoring backup
Restore() {
  set -e
  BackupFile=${File}
  BackupDirectory="`echo ${BackupFile}|awk -F "." '{print $1}'`"
  cd ${InstallationPrefix}/backup
  tar xzvf ${BackupFile} > /dev/null 2>&1
  cd ${BackupDirectory}
  Components=($(ls -d *.tar.gz))
  for Component in "${Components[@]}";do
    tar xzvf ${Component} > /dev/null 2>&1
  done

  # OMniLeads application restore
  echo "Restoring backup: OMniLeads application..."
  cd omniapp
  cp omnileads_envars.sh.backup ${InstallationPrefix}/backup/omnileads_envars.sh.bkp.${BackupDirectory}
  cp -a media_root/* ${InstallationPrefix}/media_root
  if [ -f addons_installed.sh ];then
    cp -a addons_installed.sh ${InstallationPrefix}/bin/
    cp -a *_app ${InstallationPrefix}/addons/
    Addons=($(ls -d ${InstallationPrefix}/addons/*_app))
    for Addon in "${Addons[@]}";do
      echo "Reinstalling addon ${Addon}..."
      cd ${Addon} && ./install.sh > /dev/null 2>&1
    done
  fi
  cd ${InstallationPrefix}/backup/${BackupDirectory}/

  # Asterisk restore
  echo "Restoring backup: Asterisk..."
  cd asterisk
  cp -a agi-bin/* ${AsteriskLocation}/var/lib/asterisk/agi-bin/
  cp -a --preserve=links etc/*custom* ${AsteriskLocation}/etc/asterisk/
  cp -a --preserve=links etc/*override* ${AsteriskLocation}/etc/asterisk/
  cp -a sounds/* ${AsteriskLocation}/var/lib/asterisk/sounds/
  cd ..

  # Kamailio restore
  echo "Restoring backup: Kamailio..."
  cd kamailio
  cp -a --preserve=links etc/* ${KamailioLocation}/etc/ > /dev/null 2>&1
  cd ..

  # Database restore, if it's included
  if [[ "${Components[@]}" =~ "postgresql" ]];then
    echo "Restoring backup: Database..."
    cd postgresql
    Database="`cat ${InstallationPrefix}/backup/${BackupDirectory}/omniapp/omnileads_envars.sh.backup|grep 'PGDATABASE='|awk -F'=' '{print $2}'`"
    ${BinPgRestore} -F t -d ${Database} database_backup -c
    sudo sed -i "s/^PGDATABASE=.*/PGDATABASE=${Database}/g" /etc/profile.d/omnileads_envars.sh
    source /etc/profile.d/omnileads_envars.sh
  fi

  # Final task: regenerar_asterisk
  echo "Running 'regenerar_asterisk'..."
  /opt/omnileads/bin/manage.sh regenerar_asterisk > /dev/null 2>&1

  rm -rf ${InstallationPrefix}/backup/${BackupDirectory}/

  echo -e "The file 'omnileads_envars.sh.backup' was found on your backup file, so it was copied to ${InstallationPrefix}/backup, in case you need to check variables from your previous OMniLeads instance."
  echo -e "Restore done!"
}
######################

# Beginning

Options="$@"

if [ "$#" == 0 ];then
  echo "You must enter a valid option. For more information, execute './backup-restore.sh --help'."
  exit 0
fi

for Option in ${Options};do
  case ${Option} in
    # Option for creating backup
    --backup)
      Backup="True"
      shift
    ;;
    # Option to exclude database when creating backup
    --no-database)
      NoDatabase="True"
      shift
    ;;
    # Option for restoring backup
    --restore=*)
      Restore="True"
      File="${Option#*=}"
      shift
		;;
    # Option for printing help information
    --help)
      echo "Usage:
      To create a full backup file: ./backup-restore.sh --backup
      To create a backup file, excluding database: ./backup-restore.sh --backup --no-database
      To restore a backup file: ./backup-restore.sh --restore=BackupFile.tar.gz"
      exit 0
    ;;
    # Case for invalid options
    *)
      echo "The parameter '${Option}' is not a valid option. For more information, execute './backup-restore.sh --help'."
      exit 1
    ;;
	esac
done

if [ "${Backup}" == "True" ];then
  Backup
  exit 0
fi
if [ "${Restore}" == "True" ];then
  Restore
  exit 0
fi

# End
