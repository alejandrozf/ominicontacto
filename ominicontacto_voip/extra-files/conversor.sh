#!/bin/bash
# Script para convertir grabaciones a mp3 pensado para correr diariamente en horas de la noche

Date="`which date`"
Lame="`which lame`"
Ano="`${Date} +%Y -d today`"
Mes="`${Date} +%m -d today`"
Dia="`${Date} +%d -d yesterday`"
Convertir=0
Mover_interno=0
Mover_externo=0
IP="172.16.20.12"

#Path donde estan las grabaciones en .wav, verlo en el nginx.conf, alias grabaciones
Path_origen=/opt/omnileads/asterisk/var/spool/asterisk/monitor
Path_destino=/opt/omnileads/asterisk/var/spool/asterisk/oml

if [ ! -d ${Path_destino} ]; then
    mkdir -p ${Path_destino}
fi

echo "Inicio: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`

if [ $Convertir == 0 ] && [ $Mover_interno == 0 ] && [ $Mover_externo == 0 ]; then
    echo "Cambiar el valor de las variables"
    echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
    exit 1
fi

if [ $Mover_interno == 1 ] && [ $Mover_externo == 1 ]; then
    echo "No puedes mover las grabaciones a una carpeta interna y a un servidor externo al mismo tiempo "
    echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
    exit 1
fi

if [ $Convertir == 1 ]; then

    cd ${Path_origen}
    Files="`ls -ltr|awk '{print $9}'`"

    for File in ${Files};do
        if [ -f $Lame ]; then
            #$Lame --silent -m m -b 8 --tt ${NombreSinMP3}.${sufijo} --add-id3v2 ${File} ${NombreSinMP3}.${sufijo}
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

if [ $Mover_interno == 1 ] || [ $Mover_interno == 0 ]; then
    cd ${Path_origen}
    Files="`ls -ltr|awk '{print $9}'`"
    for File in ${Files};do
        if [ $Mover_externo == 1 ]; then
                ssh-copy-id -i ~/.ssh/id_rsa.pub -o ConnectTimeout=10 root@$IP
            scp ${Path_origen}/${File} root@${IP}:${Path_destino}/${Ano}-${Mes}-${Dia}
            ResultadoCopia=`echo $?`
                if [ ${ResultadoCopia} -ne 0 ];then
                    echo "Falló al copiar el audio, favor verificar conexion o si la carpeta destino existe"
                    break
                else
                    rm -rf $File
                fi
        else
            cd ${Path_destino}
            Fecha="${Ano}-${Mes}-${Dia}"
            if [ ! -d ${Fecha} ]; then
                mkdir ${Fecha}
            fi
            cp ${Path_origen}/${File} ${Path_destino}/${Ano}-${Mes}-${Dia}
            ResultadoCopia=`echo $?`
            if [ ${ResultadoCopia} -ne 0 ];then
                echo "Falló al copiar el audio"
                exit 1
            else
                cd ${Path_origen}
                rm -rf $File
            fi
        fi
    done
fi
echo "Se realizó el procedimiento con éxito"
echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
