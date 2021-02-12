#!/bin/bash
# Script para realizar backup/restore de la herramienta

# Inicialización de variables
FECHA=`date +%Y%m%d`

PG_DUMP=$(which pg_dump)
PG_RESTORE=$(which pg_restore)
INSTALL_PREFIX="/opt/omnileads"
ASTERISK_LOCATION="$INSTALL_PREFIX/asterisk"
KAMAILIO_LOCATION="$INSTALL_PREFIX/kamailio"

Backup() {

    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup

    #Asterisk Files
    echo "Making backup of asterisk files"
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/etc
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/agi-bin
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/sounds
    cp -a --preserve=links $ASTERISK_LOCATION/etc/asterisk/oml_extensions* /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/etc
    cp $ASTERISK_LOCATION/var/lib/asterisk/agi-bin/*.py /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/agi-bin
    cp -a $ASTERISK_LOCATION/var/lib/asterisk/sounds/* /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/sounds
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/
    sleep 3

    #Omniapp files
    echo "Making backup of csv's and system audios"
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp
    cp -a $INSTALL_PREFIX/media_root/ /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
    if [ -f $INSTALL_PREFIX/bin/addons_installed.sh ]; then
       source $INSTALL_PREFIX/bin/addons_installed.sh;
       cp -a $INSTALL_PREFIX/bin/addons_installed.sh /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
       echo "Making backup of addons installed"
       for i in "${ADDONS_INSTALLED[@]}"; do
         cp -a $INSTALL_PREFIX/addons/$i /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
      done
    fi
    echo "Making backup of omnileads_envars.sh file"
    cp -a /etc/profile.d/omnileads_envars.sh /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/omnileads_envars.backup
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
    sleep 3

    #Kamailio Files
    echo "Making backup of kamailio configuration file"
    mkdir /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio
    cp -a --preserve=links $KAMAILIO_LOCATION/etc/ /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio/
    sleep 3

    #Databases
    if [ "$NO_DATABASE" != "True" ]; then
      echo "Making dump of {{ postgres_database }} database"
      mkdir /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database
      $PG_DUMP -F t {{ postgres_database }} -f /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/base_backup
      tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/* > /dev/null 2>&1
      rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/
    fi

    # Tar the last directory
    cd /tmp/omnileads-backup
    tar czvf $FECHA-omnileads-backup.tgz $FECHA-omnileads-backup/ > /dev/null 2>&1
    mv /tmp/omnileads-backup/$FECHA-omnileads-backup.tgz $INSTALL_PREFIX/backup
    rm -rf /tmp/omnileads-backup/

    backup_location="`basename $INSTALL_PREFIX/backup/${FECHA}*`"
    echo -e "\n Backup made in this file: $backup_location "
    echo -e "Now you can restore doing: ./backup-restore.sh --restore=$backup_location"
}

Restore() {
    set -e
    tar_backup=$FILE
    tar_directory=`echo $FILE | awk -F "." '{print $1}'`
    cd $INSTALL_PREFIX/backup
    tar xzvf $tar_backup > /dev/null 2>&1
    cd $tar_directory
    ARRAY=($(ls -d *.tgz))
    for i in "${ARRAY[@]}"; do
        tar xzvf $i > /dev/null 2>&1
    done
    cd tmp/omnileads-backup/$tar_directory/

    #Restore of asterisk files
    echo "Restoring asterisk files and audios"
    cd asterisk
    cp -a agi-bin/* $ASTERISK_LOCATION/var/lib/asterisk/agi-bin/
    cp -a --preserve=links etc/oml_extensions* $ASTERISK_LOCATION/etc/asterisk/
    cp -a sounds/* $ASTERISK_LOCATION/var/lib/asterisk/sounds/

    #Restore of omniapp files
    echo "Restoring omniapp csv's and system audios"
    cd ../omniapp
    cp -a media_root/* $INSTALL_PREFIX/media_root
    cp -a omnileads_envars.backup /opt/omnileads/bin
    if [ -f addons_installed.sh ]; then
      cp -a addons_installed.sh $INSTALL_PREFIX/bin/
      cp -a *_app $INSTALL_PREFIX/addons/
      ARRAY_ADDONS=($(ls -d $INSTALL_PREFIX/addons/*_app))
      for i in "${ARRAY_ADDONS[@]}"; do
        echo "Reinstalling addon $i"
        cd $i && ./install.sh
      done
    fi

    #Restore of kamailio files
    echo "Restoring kamailio files"
    cd $INSTALL_PREFIX/backup/${tar_directory}/tmp/omnileads-backup/${tar_directory}/kamailio/etc
    cp -a --preserve=links kamailio $KAMAILIO_LOCATION/etc/kamailio > /dev/null 2>&1

    #Restore of Database
    if [[ " ${ARRAY[@]} " =~ "postgres_database" ]]; then
      echo "Restoring {{ postgres_database }} database"
      cd ../../postgres_database
      $PG_RESTORE -F t -d {{ postgres_database }} base_backup -c
    fi
    rm -rf $INSTALL_PREFIX/backup/$tar_directory

    echo "Restore sucessfull a copy file of your envars were made in $INSTALL_PREFIX/bin/omnileads_envars.backup"
}

for i in "$@"
do
  case $i in
		--restore=*) # Opcion para realizar restore, argumento: Nombre del tgz
      FILE="${i#*=}"
      RESTORE="True"
      shift
		;;
		--backup) #Opcion para realizar backup
      BACKUP="True"
      shift
		;;
    --no-database)
      NO_DATABASE="True"
      shift
    ;;
    --help)
      verbose=$1
      shift
    ;;
    *)
      echo "One or more invalid options, use ./backup-restore.sh --help"
      exit 1
    ;;
	esac
done

if [ "$BACKUP" == "True" ];then Backup; fi
if [ "$RESTORE" == "True" ];then Restore; fi
