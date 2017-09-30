#!/bin/bash

#
# Shell script para facilitar el deploy de la aplicación desde un servidor de deploy
#
# Autor: Federico Peker
#


if [ -z "$VIRTUAL_ENV" ] ; then
	. ~/proyectos/ominicontacto/virtualenv/bin/activate
fi

if [ -z "$1" ] ; then
	echo "ERROR: debe especificar la version (branch, tag o commit)"
	exit 1
fi

VERSION=$1
shift

if [ -z "$1" ] ; then
	echo "ERROR: debe especificar el archivo de inventario"
	exit 1
fi

if [ ! -e "$1" ] ; then
	echo "ERROR: el archivo de inventario no existe"
	exit 1
fi

INVENTORY=$1
shift

set -e

echo ""
echo "Se iniciará deploy:"
echo ""
echo "      Version: $VERSION"
echo "   Inventario: $INVENTORY"
echo ""
echo "Presione ENTER para iniciar deploy..."
read
echo ""

cd ~/ominicontacto

#git clean -fdx

#git fetch --prune --tags --force --all -v

git checkout master
git pull origin +master:master
git checkout $VERSION
git pull origin +$VERSION:$VERSION

# git reset --hard origin/$VERSION

./build.sh -i $INVENTORY $*

