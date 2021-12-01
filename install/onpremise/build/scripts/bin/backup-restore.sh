#!/bin/bash
# Backup and restore script for OMniLeads

# Variables initialization
InstallationPrefix="/opt/omnileads"
BinDate="`which date`"
BinPgDump="`which pg_dump`"
BinPgRestore="`which pg_restore`"
Date="`${BinDate} +%y%m%d`"
Hour="`${BinDate} +%H%M%S`"
BackupOML="0"
BackupAsterisk="0"
BackupKamailio="0"
BackupPSQL="0"
RestoreOML="0"
RestoreAsterisk="0"
RestoreKamailio="0"
RestorePSQL="0"
Target="local"
##########################

# Functions definition

# Function for creating backup
Backup() {
  TmpDirectory="/tmp/${Date}-${Hour}-oml-backup/${Date}-${Hour}-oml-backup"
  mkdir -p ${TmpDirectory}
  cd ${TmpDirectory}

  # OMniLeads application backup
  if [ "${BackupOML}" == "1" ];then
    echo "Creating backup: OMniLeads application..."
    mkdir -p ${TmpDirectory}/omniapp
    cp -a ${InstallationPrefix}/media_root/ ${TmpDirectory}/omniapp
    if [ -f ${InstallationPrefix}/bin/addons_installed.sh ];then
      echo "Creating backup: OMniLeads addons..."
      mkdir -p ${TmpDirectory}/omniapp/addons
      source ${InstallationPrefix}/bin/addons_installed.sh
      cp -a ${InstallationPrefix}/bin/addons_installed.sh ${TmpDirectory}/omniapp/addons
      for Addon in "${ADDONS_INSTALLED[@]}";do
        cp -a ${InstallationPrefix}/addons/${Addon} ${TmpDirectory}/omniapp/addons
      done
    fi
    echo "Creating backup: File omnileads_envars.sh..."
    cp -a /etc/profile.d/omnileads_envars.sh ${TmpDirectory}/omniapp/omnileads_envars.sh.backup
    tar czvf ${TmpDirectory}/omniapp.tar.gz omniapp > /dev/null 2>&1
    rm -rf ${TmpDirectory}/omniapp/
    sleep 3
  fi

  # Asterisk backup
  if [ "${BackupAsterisk}" == "1" ];then
    echo "Creating backup: Asterisk..."
    AsteriskLocation="${InstallationPrefix}/asterisk"
    mkdir -p ${TmpDirectory}/asterisk
    mkdir -p ${TmpDirectory}/asterisk/etc
    mkdir -p ${TmpDirectory}/asterisk/agi-bin
    mkdir -p ${TmpDirectory}/asterisk/sounds
    cp -a --preserve=links ${AsteriskLocation}/etc/asterisk/*custom* ${TmpDirectory}/asterisk/etc
    cp -a --preserve=links ${AsteriskLocation}/etc/asterisk/*override* ${TmpDirectory}/asterisk/etc
    cp -a ${AsteriskLocation}/var/lib/asterisk/agi-bin/*custom*.py ${TmpDirectory}/asterisk/agi-bin > /dev/null 2>&1
    cp -a ${AsteriskLocation}/var/lib/asterisk/sounds/* ${TmpDirectory}/asterisk/sounds
    tar czvf ${TmpDirectory}/asterisk.tar.gz asterisk > /dev/null 2>&1
    rm -rf ${TmpDirectory}/asterisk/
    sleep 3
  fi

  # Kamailio backup
  if [ "${BackupKamailio}" == "1" ];then
    echo "Creating backup: Kamailio..."
    KamailioLocation="${InstallationPrefix}/kamailio"
    mkdir ${TmpDirectory}/kamailio
    cp -a --preserve=links ${KamailioLocation}/etc/ ${TmpDirectory}/kamailio
    tar czvf ${TmpDirectory}/kamailio.tar.gz kamailio > /dev/null 2>&1
    rm -rf ${TmpDirectory}/kamailio/
    sleep 3
  fi

  # Database backup
  if [ "${BackupPSQL}" == "1" ];then
    echo "Creating backup: PostgreSQL..."
    Database="`cat /etc/profile.d/omnileads_envars.sh|grep 'PGDATABASE='|awk -F'=' '{print $2}'`"
    mkdir ${TmpDirectory}/postgresql
    ${BinPgDump} -F t ${Database} -f ${TmpDirectory}/postgresql/database_backup
    echo "Creating backup: File omnileads_envars.sh..."
    cp -a /etc/profile.d/omnileads_envars.sh ${TmpDirectory}/postgresql/omnileads_envars.sh.backup
    tar czvf ${TmpDirectory}/postgresql.tar.gz postgresql > /dev/null 2>&1
    rm -rf ${TmpDirectory}/postgresql/
    sleep 3
  fi

  # Creation of final backup file
  cd /tmp/${Date}-${Hour}-oml-backup/
  tar czvf ${Date}-${Hour}-oml-backup.tar.gz ${Date}-${Hour}-oml-backup > /dev/null 2>&1
  mv ${Date}-${Hour}-oml-backup.tar.gz ${BackupDirectory}
  rm -rf /tmp/${Date}-${Hour}-oml-backup/

  BackupFile="`basename ${BackupDirectory}/${Date}-${Hour}*`"
  echo -e "Backup done!"
  echo -e "Backup file created: ${BackupDirectory}/${BackupFile}"
  echo -e "To restore this backup file: ./backup-restore.sh --restore=${BackupFile}"
}

# Function for restoring backup
Restore() {
  BackupFile=${File}
  BackupDirectoryName="`echo ${BackupFile}|awk -F "." '{print $1}'`"

  if [ ! -f "${BackupDirectory}/${BackupFile}" ];then
    echo -e "The file \"${BackupDirectory}/${BackupFile}\" doesn't exist."
    exit 1
  fi

  cd ${BackupDirectory}
  tar xzvf ${BackupFile} > /dev/null 2>&1
  cd ${BackupDirectoryName}
  Components=($(ls -d *.tar.gz))
  for Component in "${Components[@]}";do
    tar xzvf ${Component} > /dev/null 2>&1
  done

  # OMniLeads application restore
  if [ -d omniapp ] && [ "${RestoreOML}" == "1" ];then
    echo "Restoring backup: OMniLeads application..."
    cd omniapp
    cp omnileads_envars.sh.backup ${BackupDirectory}/omnileads_envars.sh.bkp.${BackupDirectoryName}
    cp -a media_root/* ${InstallationPrefix}/media_root
    if [ -f addons/addons_installed.sh ];then
      cp -a addons/addons_installed.sh ${InstallationPrefix}/bin/
      cp -a addons/*_app ${InstallationPrefix}/addons/
      Addons=($(ls -d ${InstallationPrefix}/addons/*_app))
      for Addon in "${Addons[@]}";do
        echo "Reinstalling addon ${Addon}..."
        cd ${Addon} && ./install.sh > /dev/null 2>&1
      done
    fi
    echo -e "The file 'omnileads_envars.sh.backup' was found on your backup file, so it was copied to ${BackupDirectory}, in case you need to check variables from your previous OMniLeads instance."
    cd ${BackupDirectory}/${BackupDirectoryName}/
  fi

  # Asterisk restore
  if [ -d asterisk ] && [ "${RestoreAsterisk}" == "1" ];then
    echo "Restoring backup: Asterisk..."
    AsteriskLocation="${InstallationPrefix}/asterisk"
    cd asterisk
    cp -a --preserve=links etc/*custom* ${AsteriskLocation}/etc/asterisk/
    cp -a --preserve=links etc/*override* ${AsteriskLocation}/etc/asterisk/
    cp -a agi-bin/*custom* ${AsteriskLocation}/var/lib/asterisk/agi-bin/ > /dev/null 2>&1
    cp -a sounds/* ${AsteriskLocation}/var/lib/asterisk/sounds/
    cd ${BackupDirectory}/${BackupDirectoryName}/
  fi

  # Kamailio restore
  if [ -d kamailio ] && [ "${RestoreKamailio}" == "1" ];then
    echo "Restoring backup: Kamailio..."
    KamailioLocation="${InstallationPrefix}/kamailio"
    cd kamailio
    cp -a --preserve=links etc/* ${KamailioLocation}/etc/ > /dev/null 2>&1
    cd ${BackupDirectory}/${BackupDirectoryName}/
  fi

  # Database restore, if it's included
  if [ -d postgresql ] && [ "${RestorePSQL}" == "1" ];then
    echo "Restoring backup: Database..."
    cd postgresql
    Database="`cat ${BackupDirectory}/${BackupDirectoryName}/postgresql/omnileads_envars.sh.backup|grep 'PGDATABASE='|awk -F'=' '{print $2}'`"
    ${BinPgRestore} -F t -d ${Database} database_backup -c
    sudo sed -i "s/^PGDATABASE=.*/PGDATABASE=${Database}/g" /etc/profile.d/omnileads_envars.sh
    source /etc/profile.d/omnileads_envars.sh
    cd ${BackupDirectory}/${BackupDirectoryName}/
  fi

  # Final task: regenerar_asterisk
  echo "Running 'regenerar_asterisk'..."
  /opt/omnileads/bin/manage.sh regenerar_asterisk > /dev/null 2>&1

  rm -rf ${BackupDirectory}/${BackupDirectoryName}/

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
    # Option for restoring backup
    --restore=*)
      Restore="True"
      File="${Option#*=}"
      shift
		;;
    # Option for creating/restoring backup: OMniLeads application
    --omniapp)
      BackupOML="1"
      RestoreOML="1"
      shift
    ;;
    # Option for creating/restoring backup: Asterisk
    --asterisk)
      BackupAsterisk="1"
      RestoreAsterisk="1"
      shift
    ;;
    # Option for creating/restoring backup: Kamailio
    --kamailio)
      BackupKamailio="1"
      RestoreKamailio="1"
      shift
    ;;
    # Option for creating/restoring backup: PostgreSQL
    --postgresql)
      BackupPSQL="1"
      RestorePSQL="1"
      shift
    ;;
    --target=*)
      Target="${Option#*=}"
    ;;
    # Option for printing help information
    --help)
      echo "Usage:
      There are 4 main components that can be backed up and restored: OMniLeads application, Asterisk, Kamailio, PostgreSQL.
      To create a full backup: './backup-restore.sh --backup'.
      To create a backup only for OMniLeads application component: './backup-restore.sh --backup --omniapp'.
      To create a backup only for Asterisk component: './backup-restore.sh --backup --asterisk'.
      To create a backup only for Kamailio component: './backup-restore.sh --backup --kamailio'.
      To create a backup only for PostgreSQL component: './backup-restore.sh --backup --postgresql'.
      To create a backup for specific components, select those components. Eg: './backup-restore.sh --backup --asterisk --kamailio'.
      To restore a backup: './backup-restore.sh --restore=BackupFile.tar.gz'. This command, will restore all components that exist on the backup file.
      To restore OMniLeads application component: './backup-restore.sh --restore=BackupFile.tar.gz --omniapp'.
      To restore Asterisk component: './backup-restore.sh --restore=BackupFile.tar.gz --asterisk'.
      To restore Kamailio component: './backup-restore.sh --restore=BackupFile.tar.gz --kamailio'.
      To restore PostgreSQL component: './backup-restore.sh --restore=BackupFile.tar.gz --postgresql'.
      To restore specific components, select those components. Eg: './backup-restore.sh --restore=BackupFile.tar.gz --asterisk --kamailio'.
      To select a specific destination directory for backup file, or a specific source directory to find the backup file to be restored, the option '--target=Directory'
      can be used. By default, if it's not specified, this option is set to '--target=/opt/omnileads/backup'. But it can be used for both backup and restore options. Eg:
      ./backup-restore.sh --backup --target=/usr/src
      ./backup-restore.sh --restore=211110-161018-oml-backup.tar.gz --target=/usr/src
      "
      exit 0
    ;;
    # Case for invalid options
    *)
      echo "The parameter '${Option}' is not a valid option. For more information, execute './backup-restore.sh --help'."
      exit 1
    ;;
	esac
done

if [ "${Backup}" == "True" ] && [ "${Restore}" == "True" ];then
  echo "Options \"--backup\" and \"--restore\", can't be selected at the same time."
  exit 1
fi

# Storage for backup/restore file
case ${Target} in
  # Storage for backup/restore: local
  local)
    BackupDirectory="${InstallationPrefix}/backup"
  ;;
  *)
    if [ ! -d ${Target} ];then
      echo "The directory \"${Target}\" doesn't exist."
      exit 1
    fi
    BackupDirectory="${Target}"
  ;;
esac

if [ "${Backup}" == "True" ];then
  if [ "${BackupOML}" == "0" ] && [ "${BackupAsterisk}" == "0" ] && [ "${BackupKamailio}" == "0" ] && [ "${BackupPSQL}" == "0" ];then
    BackupOML="1"
    BackupAsterisk="1"
    BackupKamailio="1"
    BackupPSQL="1"
  fi
  Backup
  exit 0
fi

if [ "${Restore}" == "True" ];then
  if [ "${RestoreOML}" == "0" ] && [ "${RestoreAsterisk}" == "0" ] && [ "${RestoreKamailio}" == "0" ] && [ "${RestorePSQL}" == "0" ];then
    RestoreOML="1"
    RestoreAsterisk="1"
    RestoreKamailio="1"
    RestorePSQL="1"
  fi
  Restore
  exit 0
fi

# End
