#!/bin/bash

#
# Shell script para pasar a esquema deployer-deployed
#
# Autor: Andres Felipe Macias
#
export FROM_INTWO=1
rama=develop
tag=all
usuario=omnileads

echo "Este script automatiza la configuración de ansible para pasarse a esquema deployer - deployed"

IngresaIP() {
echo -en "Ingrese IP del server a deployar: "; read ip
sed -i "2s/.*/$ip ansible_ssh_port=22 ansible_user=$usuario/" hosts

}
IngresaIP
while true; do
    if [ -z $ip ]; then
        echo "Es necesario que ingreses una IP"
        IngresaIP
    else
        export ip=$ip
        break
    fi
done

IngresaUsuario() {
echo -en "Ingrese usuario que instalará los servicios (default: omnileads): "; read nvo_usuario
if [ -z $nvo_usuario ]; then
    echo "Usando usuario por default"
    sed -i "2s/.*/$ip ansible_ssh_port=22 ansible_user=$usuario/" hosts
else
    usuario=$nvo_usuario
    sed -i "2s/.*/$ip ansible_ssh_port=22 ansible_user=$usuario/" hosts

fi
}

IngresaUsuario
while true; do
    echo "Transifiriendo llave pública al usuario $usuario de Centos (si es la primera vez que haces esto tienes que ingresar la contraseña del usuario $usuario)"
    ssh-copy-id -i ~/.ssh/id_rsa.pub -o ConnectTimeout=10 $usuario@$ip
    if [[ $? == 1 ]]
    then
        echo "Ingresaste una IP o usuario inválidas, favor volver a ingresarlas"
        IngresaIP
        IngresaUsuario
    else
        echo "La llave pública se transfirió satisfactoriamente o ya había sido transferida anteriormente"
        break
    fi
done

IngresaPrefix() {
unset my_prefix
unset CHARCOUNT
unset prefix
unset my_array
unset PROMPT
echo -en "Ingrese directorio prefijo de instalación (default: /opt/omnileads/, no olvidar ingresar / final): "
stty -echo
while IFS= read -p "$PROMPT" -r -n 1 prefix; do

    if [[ $prefix == $'\0' ]] ; then
        break
    fi
    # Backspace
    if [[ $prefix == $'\177' ]] ; then
        if [ $CHARCOUNT -gt 0 ] ; then
            CHARCOUNT=$((CHARCOUNT-1))
            PROMPT=$'\b \b'
            my_prefix="${my_prefix%?}"
            unset 'my_array[${#my_array[@]}-1]'
        else
            PROMPT=''
        fi
    else
        CHARCOUNT=$((CHARCOUNT+1))
        PROMPT=$prefix
        my_array=("${my_array[@]}" $prefix)
        my_prefix+="$prefix"
    fi
done
stty echo
}
IngresaPrefix
while true; do
if [ -z $my_prefix ]; then
    echo ""; echo "Usando directorio por default"
    break
else
    if [ ${my_array[-1]} == '/' ]; then
        sed -i "s#\(^install_\).*#install_prefix=$my_prefix#" hosts
        echo ""
        break
    else
        echo ""; echo "Olvidaste ingresar el '/' al final del directorio"
        IngresaPrefix
    fi
fi
done


IngresaRama() {
echo -en "Ingrese rama a deployar (default: develop): "; read nva_rama
}
IngresaRama
if [ -z "$nva_rama" ] ; then
     echo  "Usando valor por default"
else
     while true; do
         cd $(pwd)
         git branch -a|awk -F '/' '{print $3}' > /var/tmp/ramas.txt
         RAMA_POSTA=`cat /var/tmp/ramas.txt`
         for git_rama in $RAMA_POSTA; do
            if [ $git_rama != $nva_rama ]; then
                continue
            else
                rama=$nva_rama
                rama_existe=1
                break
            fi
         done
         if [ -z $rama_existe  ]; then
            echo "La rama que ingresaste no existe, intentalo nuevamente"
            IngresaRama
         else
            echo "La rama que ingresaste es valida"
            break
         fi
     done
fi

IngresaTag() {
echo -en "Ingrese tag de ansible (default: all, opciones: all, postinstall):  "; read nva_tag
}
IngresaTag
while true; do
    if [ -z "$nva_tag" ] ; then
        echo  "Usando valor por default"
        tag=$tag
        break
    else
        if [ $nva_tag == "postinstall" ] || [ $nva_tag == "all" ] || [ $nva_tag == "asterisk" ] || [ $nva_tag == "kamailio" ]; then
            tag=$nva_tag
            break
        else
            echo "Opción inválida, vuelve a intentarlo"
            IngresaTag
        fi
    fi
done

./deploy.sh -r $rama -i -t $tag