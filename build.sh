#!/bin/bash

#
# Script de build y deploy para Omnileads
#
# Autor: Federico Peker
# Colaborador: Felipe Macias
#

opcion=2

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
#cat > $TMP/ominicontacto/version.py <<EOF


# ----------

export DO_CHECKS="${DO_CHECKS:-no}"

if [ $opcion -eq 1 ]; then
    echo "Ejecutando Ansible en Debian omni-app"
    ansible-playbook -s /etc/ansible/deploy/main.yml -u freetech --extra-vars "BUILD_DIR=$TMP/ominicontacto" -K
    echo "Ejecutando Ansible para copia de archivos entre servers"
    ansible-playbook -s /etc/ansible/deploy/omniapp_second/transfer.yml -u root -K
    echo "Finalizó la instalación de Omnileads"

elif [ $opcion -eq 2 ]; then
    echo "Ejecutando Ansible en SangomaOS Post-Freepbx"
    ansible-playbook -s /etc/ansible/deploy/omni-freepbx.yml -u root
    echo "Finalizó la instalación de Omnileads"

else
    echo "Parámetro inválido ingrese de nuevo"
    echo  ""
fi

echo "Ejecutando Ansible"



