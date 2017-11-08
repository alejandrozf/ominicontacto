#!/bin/bash

#
# Shell script para facilitar el deploy de la aplicación desde un servidor de deploy
#
# Autor: Andres Felipe Macias
# Colaborador:  Federico Peker
#

echo "Bienvenido al asistente de instalación de Omnileads"
echo ""
echo "Ingrese 1 si va instalar en Debian, 2 si va a instalar en SangomaOS o 3 si va a instalar en Centos 7"
echo -en "Opcion: ";read opcion
echo ""

if [ $opcion -eq 1 ]; then
    echo "Ejecutando Ansible en Debian omni-voip"
    ansible-playbook -s /etc/ansible/omnivoip/omni-voip.yml -u root
    ResultadoAnsible=`echo $?`

    echo "Finalizó la instalación omni-voip"
    echo ""

elif [ $opcion -eq 2 ]; then
    echo "Ejecutando Ansible en SangomaOS"
    #ansible-playbook -s /etc/ansible/omnivoip/omni-freepbx.yml -u root
    ResultadoAnsible=`echo $?`

    echo "Finalizó la instalación omni-voip"
    echo ""

elif [ $opcion -eq 3 ]; then
    echo "Ejecutando Ansible en Centos"
    #ansible-playbook -s /etc/ansible/omnivoip/centos.yml -u root
    ResultadoAnsible=`echo $?`

    echo "Finalizó la instalación omni-voip"
    echo ""

else
    echo "Parámetro inválido ingrese de nuevo"
    echo  ""
fi


if [ ${ResultadoAnsible} -ne 0 ];then
    echo "Falló la ejecucion de Ansible, favor volver a correr el script"
    exit 0
else
    echo "Pasando al deploy de OmniAPP"

    if [ -z "$VIRTUAL_ENV" ] ; then
        . ~/ominicontacto/virtualenv/bin/activate
    fi

    if [ -z "$1" ] ; then
        echo "ERROR: debe especificar la version (branch, tag o commit)"
        exit 1
    fi

    VERSION=$1
    shift

    ##### No es necesario pasar archivo de inventario pues lo lee del ansible.cfg #####
    #if [ -z "$1" ] ; then
    #	echo "ERROR: debe especificar el archivo de inventario"
    #	exit 1
    #fi
    #
    #if [ ! -e "$1" ] ; then
    #	echo "ERROR: el archivo de inventario no existe"
    #	exit 1
    #fi
    #INVENTORY=$1
    #shift

    set -e

    echo ""
    echo "Se iniciará deploy:"
    echo ""
    echo "      Version: $VERSION"
    #echo "   Inventario: $INVENTORY"
    echo ""

    cd ~/ominicontacto
    #git clean -fdx
    #git fetch --prune --tags --force --all -v
    #git checkout master
    #git pull origin +master:master

    git checkout $VERSION
    git pull origin +$VERSION:$VERSION

    # git reset --hard origin/$VERSION

    ################### Build.sh #####################

    if [ "$VIRTUAL_ENV" = "" ] ; then
            echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
            exit 1
    fi

    set -e

    cd $(dirname $0)

    TMP=/dev/shm/ominicontacto-build

    if [ -e $TMP ] ; then
        rm -rf $TMP
    fi

    mkdir -p $TMP/ominicontacto
    echo "Usando directorio temporal: $TMP/ominicontacto..."

    echo "Creando bundle usando git-archive..."
    git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP/ominicontacto

    echo "Eliminando archivos innecesarios..."
    rm -rf $TMP/ominicontacto/docs
    rm -rf $TMP/ominicontacto/ansible
    rm -rf $TMP/ominicontacto/run_coverage_tests.sh
    rm -rf $TMP/ominicontacto/run_uwsgi.sh

    echo "Obteniendo datos de version..."
    branch_name=$(git symbolic-ref -q HEAD)
    branch_name=${branch_name##refs/heads/}
    branch_name=${branch_name:-HEAD}

    commit="$(git rev-parse HEAD)"
    author="$(id -un)@$(hostname -f)"

    echo "Creando archivo de version | Branch: $branch_name | Commit: $commit | Autor: $author"
    cat > $TMP/ominicontacto/ominicontacto_app/version.py <<EOF

    #
    # Archivo autogenerado
    #

OML_BRANCH="${branch_name}"
OML_COMMIT="${commit}"
OML_BUILD_DATE="$(env LC_ALL=C LC_TIME=C date)"
OML_AUTHOR="${author}"

if __name__ == '__main__':
    print OML_COMMIT


EOF

    echo "Validando version.py - Commit:"
    python $TMP/ominicontacto/ominicontacto_app/version.py

    # ----------
    export DO_CHECKS="${DO_CHECKS:-no}"
fi

if [ $opcion -eq 1 ]; then
    echo "Ejecutando Ansible en Debian omni-app"
    ansible-playbook -s /etc/ansible/deploy/omni-app.yml -u freetech --extra-vars "BUILD_DIR=$TMP/ominicontacto" -K
    echo "Ejecutando Ansible para copia de archivos entre servers"
    ansible-playbook -s /etc/ansible/deploy/omniapp_second/transfer.yml -u root -K
    echo "Finalizó la instalación de Omnileads"

elif [ $opcion -eq 2 ]; then
    echo "Ejecutando Ansible en SangomaOS para deploy de OmniAPP"
    ansible-playbook -s /etc/ansible/deploy/omni-freepbx.yml -u root --extra-vars "BUILD_DIR=$TMP/ominicontacto"
    echo "Finalizó la instalación de Omnileads"

elif [ $opcion -eq 3 ]; then
    echo "Ejecutando Ansible en Centos para deploy de OmniAPP"
    ansible-playbook -s /etc/ansible/deploy/centos.yml -u root --extra-vars "BUILD_DIR=$TMP/ominicontacto"
    echo "Finalizó la instalación Omnileads"
    echo ""

else
    echo "Parámetro inválido ingrese de nuevo"
    echo  ""
fi
