#!/bin/bash
# Script para convertir grabaciones a mp3 pensado para correr diariamente en horas de la noche
# Modo de uso: tiene 2 argumentos que son obligatorias poner.
# Ejemplo: ./convertir.sh 1 1

Date="`which date`"
Lame="`which lame`"
Ano="`${Date} +%Y -d yesterday`"
Mes="`${Date} +%m -d yesterday`"
Dia="`${Date} +%d -d yesterday`"

echo "Inicio: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`

if [ ${MONITORFORMAT} != "mp3" ]; then
  echo "Not necessary to convert files, because variable MONITORFORMAT is not mp3"
  exit 0
fi

if [ ! -d /tmp/$Ano-$Mes-$Dia ];then
  mkdir /tmp/$Ano-$Mes-$Dia
fi
cd /tmp/$Ano-$Mes-$Dia

case ${CALLREC_DEVICE} in
    s3-aws)
        aws s3 sync s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia ./
        ;;
    s3-no-check-cert)
        aws --endpoint ${S3_ENDPOINT} --no-verify-ssl s3 sync s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia ./
        ;;
    *)
        aws --endpoint ${S3_ENDPOINT} s3 sync s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia ./
        ;;
esac

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

case ${CALLREC_DEVICE} in
    s3-aws)
        aws s3 sync ./ s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia --delete
        ;;
    s3-no-check-cert)
        aws --endpoint ${S3_ENDPOINT} --no-verify-ssl s3 sync ./ s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia --delete
        ;;
    *)
        aws --endpoint ${S3_ENDPOINT} s3 sync ./ s3://${S3_BUCKET_NAME}/$Ano-$Mes-$Dia --delete
        ;;
esac

ResultadoCopia=`echo $?`
if [ ${ResultadoCopia} -ne 0 ];then
      echo "Falló al copiar el audio"
      exit 1
else
      cd .. && rm -rf ./$Ano-$Mes-$Dia
fi


echo "Se realizó el procedimiento con éxito"
echo "Fin: "`${Date} +%A\ %d\ "de"\ %B\ "de"\ %Y\ %T\ %Z"."`
