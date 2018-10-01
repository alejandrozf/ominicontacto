#!/bin/bash
# Script para convertir grabaciones a mp3 pensado para correr diariamente en horas de la noche
# Modo de uso: tiene 2 argumentos que son obligatorias poner.
# Ejemplo: ./convertir.sh 1 1

Date="`which date`"
Lame="`which lame`"
Ano="`${Date} +%Y -d yesterday`"
Mes="`${Date} +%m -d yesterday`"
Dia="`${Date} +%d -d yesterday`"
Convertir=$1 # 1 si se quiere convertir a mp3 los audios, 0 si se quieren en wav
Mover_audios=$2 # 2 para mover a server remoto, 1 si se quiere mover path destino, 0 si se quiere mantener en path origen
IP=$3 # server remoto para enviar audios
Path_remoto=$4 # carpeta remota a la que se quieren pasar los audios

#Path donde estan las grabaciones en .wav, verlo en el nginx.conf, alias grabaciones
Path_origen={{ asterisk_location }}/var/spool/asterisk/monitor/${Ano}-${Mes}-${Dia}
Path_destino={{ asterisk_location }}/var/spool/asterisk/oml

if [ ! -d ${Path_destino} ]; then
    mkdir -p ${Path_destino}
fi

echo "Inicio: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`

if [ $Convertir == 0 ] && [ $Mover_audios == 0 ]; then
    echo "No se hace nada"
    echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
    exit 1
fi

if [ $# -lt 2 ]; then
  echo "Falta uno o mas argumentos"
  echo "Usage: ./conversor.sh 1 0: convierte audios a mp3 y no cambia de ubicacion los audios"
  echo "       ./conversor.sh 0 1: no convierte audios a mp3 y cambia de ubicacion los audios a path destino"
  echo "       ./conversor.sh 1 1: convierte audios a mp3 y cambia de ubicacion los audios a path destino"
  echo "       ./conversor.sh 1 2 usuario@IP \$PATH_REMOTO: convierte audios a mp3 y cambia de ubicacion los audios a \$PATH_REMOTO en server de \$IP"
  echo "       ./conversor.sh 0 2 usuario@IP \$PATH_REMOTO: no convierte audios a mp3 y cambia de ubicacion los audios a \$PATH_REMOTO en server de \$IP"
  echo "Ingresar tercer argumento con el formato usuario@IP "
  exit 1
fi

#re1='^[0-1]+$'
#re2='^[0-2]+$'
re1="`echo "$1" | grep -E ^\-?[0-1]*\.?[0-1]+$`"
re2="`echo "$2" | grep -E ^\-?[0-2]*\.?[0-2]+$`"
if [ "$re1" == "" ] || [ "$re2" == "" ]; then
    echo "Hay alguna opción invalida, volver a correr script "
    echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
    exit 1
fi

if [ $Convertir == 1 ]; then
    cd ${Path_origen}
    Files="`ls -ltr|awk '{print $9}'`"

    for File in ${Files};do
        if [ -f $Lame ]; then
            Sufijo="`ls ${File}|cut -d "." -f 3,3`"
            if [ $Sufijo == "mp3" ]; then
                echo -n
            else
                nice ${Lame} --quiet --preset phone $File
                ResultadoConversion=`echo $?`
                    if [ ${ResultadoConversion} -ne 0 ];then
                        echo "Falló al convertir el audio"
                        exit 1
                    else
                        rm -rf $File
                    fi
            fi
        fi
    done
fi

if [ $Mover_audios != 0 ]; then
    cd ${Path_origen}
      if [ $Mover_audios == 1 ]; then
        cd ${Path_destino}
        cp -r ${Path_origen} ${Path_destino}/${Ano}-${Mes}-${Dia}
        ResultadoCopia=`echo $?`
        if [ ${ResultadoCopia} -ne 0 ];then
            echo "Falló al copiar el audio"
            exit 1
        else
            cd ${Path_origen}
            rm -rf ./*
        fi
      elif [ $Mover_audios == 2 ]; then
        if [ ! -z "$IP" ] && [ ! -z "$Path_remoto" ]; then
            ssh-copy-id -i ~/.ssh/id_rsa.pub -o ConnectTimeout=10 $IP
            scp -r ${Path_origen} ${IP}:${Path_remoto} > /dev/null
            ResultadoCopia=`echo $?`
                if [ ${ResultadoCopia} -ne 0 ];then
                    echo "Falló al copiar el audio, favor verificar conexion o si la carpeta destino existe"
                    break
                else
                    rm -rf ${Path_origen}

                fi
        else
            echo  "no se especificó IP o path remoto, se sale del script"
            exit 1
        fi
      fi
  fi

echo "Se realizó el procedimiento con éxito"
echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
