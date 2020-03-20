#!/bin/bash
# Script para realizar backup/restore de la herramienta

# Inicialización de variables
FECHA=`date +%Y%m%d`

pg_dump=`which pg_dump`
pg_restore=`which pg_restore`

Backup() {

    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup

    #Asterisk Files
    echo "Making backup of asterisk files"
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/etc
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/agi-bin
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/sounds
    cp -a --preserve=links {{ asterisk_location }}/etc/asterisk/oml_extensions* /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/etc
    cp {{ asterisk_location }}/var/lib/asterisk/agi-bin/*.py /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/agi-bin
    cp -a {{ asterisk_location }}/var/lib/asterisk/sounds/oml/ /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/sounds
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/asterisk/
    sleep 3

    #Omniapp files
    echo "Making backup of csv's and system audios"
    mkdir -p /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp
    cp -a {{ install_prefix }}media_root/ /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/omniapp/
    sleep 3

    #Kamailio Files
    echo "Making backup of kamailio configuration file"
    mkdir /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio
    cp -a --preserve=links {{ kamailio_location }}/etc/ /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/kamailio/
    sleep 3

    #Databases
    echo "Making dump of {{ postgres_database }} database"
    mkdir /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database
    $pg_dump -F t {{ postgres_database }} -f /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/base_backup
    tar czvf /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/* > /dev/null 2>&1
    rm -rf /tmp/omnileads-backup/$FECHA-omnileads-backup/postgres_database/

    # Tar the last directory
    tar czvf $FECHA-omnileads-backup.tgz /tmp/omnileads-backup/$FECHA-omnileads-backup/ > /dev/null 2>&1
    cd /tmp/omnileads-backup && tar czvf $FECHA-omnileads-backup.tgz $FECHA-omnileads-backup
    mv /tmp/omnileads-backup/$FECHA-omnileads-backup.tgz {{ install_prefix }}backup
    rm -rf /tmp/omnileads-backup/

    backup_location="`basename {{ install_prefix }}backup/${FECHA}*`"
    echo -e "\n Backup made in this file: $backup_location "
    echo -e "Now you can restore doing: ./backup-restore.sh -r $backup_location"
}

Restore() {
    set -e
    ARRAY=(asterisk.tgz kamailio.tgz postgres_database.tgz omniapp.tgz)
    tar_backup=$1
    tar_directory=`echo $1 | awk -F "." '{print $1}'`
    cd {{ install_prefix }}backup
    tar xzvf $tar_backup > /dev/null 2>&1
    cd $tar_directory
    for counter in {0..3}; do
        tar xzvf ${ARRAY[counter]} > /dev/null 2>&1
    done
    cd tmp/omnileads-backup/$tar_directory/

    #Restore of asterisk files
    echo "Restoring asterisk files and audios"
    cd asterisk
    cp -a agi-bin/* {{ asterisk_location }}/var/lib/asterisk/agi-bin/
    cp -a --preserve=links etc/oml_extensions* {{ asterisk_location }}/etc/asterisk/
    cp -a sounds/* {{ asterisk_location }}/var/lib/asterisk/sounds/

    #Restore of omniapp files
    echo "Restoring omniapp csv's and system audios"
    cd ../omniapp
    cp -a media_root/* {{ install_prefix }}/media_root

    #Restore of kamailio files
    echo "Restoring kamailio files"
    cd ../kamailio/etc
  #  cp -a certs {{ kamailio_location }}/etc/certs > /dev/null 2>&1
    cp -a --preserve=links kamailio {{ kamailio_location }}/etc/kamailio > /dev/null 2>&1

    #Restore of Database
    echo "Restoring {{ postgres_database }} database"
    cd ../../postgres_database
    $pg_restore -F t -d {{ postgres_database }} base_backup -c

    rm -rf {{ install_prefix }}backup/$tar_directory

}

while getopts "r:b" OPTION;do
	case "${OPTION}" in
		r) # Opcion para realizar restore, argumento: Nombre del tgz
            Restore $OPTARG
		;;
		b) #Opcion para realizar backup
		    Backup
		;;
	esac
done
if [ $# -eq 0  ]; then echo -n; fi
