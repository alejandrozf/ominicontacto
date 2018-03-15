#!/bin/bash

#
# Shell script para facilitar el deploy de la aplicación desde un servidor de deploy
#
# Autor: Andres Felipe Macias
# Colaborador:  Federico Peker
#
ANSIBLE=`which ansible`
PIP=`which pip`
current_directory=`pwd`
export ANSIBLE_CONFIG=$current_directory

Help() {
USAGE="
       Opciones a ingresar: \n
            -h: ayuda \n
            -r: rama a deployar (ej: -r develop) \n
            -i: instala ansible, transfiere llaves ssh a maquina a deployar, ingresar fqdn, formato de grabaciones, pass de OML \n
            -t: ingresar ip, opcion de SO, tags de ansible (TAREAS A EJECUTAR y no ejecutar) \n
        \n
       EJEMPLOS: \n
       - ./deploy.sh -r develop -t hosts -> deployará la rama develop, ejecutara todas las tareas \n
       - ./deploy.sh -r release-0.4 -i -t kamailio,nginx,kamailio-cert -> deploya la rama release-0.4, pide datos del server, ejecuta las tareas de instalación de kamailio y de nginx  exceptuando la creacion de certificados (tiene que estar separado por coma) \n
       - ./deploy.sh -r release-0.4 -i -t asterisk,,kamailio-cert -> igual al anterior, solamente ejecutará tareas de instalación de asterisk exceptuando la creacion de certificados \n
       \n
       Tags disponibles: \n
       hosts: ejecuta todos los procesos \n
       asterisk-insthosts: compila e instala asterisk \n
       asterisk-config: realiza tareas de configuracion de asterisk con OML \n
       asternic: instala y configura asternic y scripts de grabaciones \n
       deploy: instala la aplicación, setea el virtualenv y el entorno de OML \n
       django-migrations: realiza todas las migraciones de django (uso de python manage.py) \n
       freepbx: realiza la instalación de freepbx \n
       kamailio: compila e instala kamailio y rtpengine \n
       kamailio-cert: realiza el seteo y creacion de certificados usados por kamailio y nginx \n
       nginx: configuraciones de nginx \n
       omnivoip: ejecuta toda la instalacion de omnivoip \n
       omniapp: ejecuta toda la instalacion de omniapp (abarca deploy de django de OML y nginx) \n
       pre-sangoma: ejecuta los prerequisitos de SangomaOS (instalacion de paquetes tambien) \n
       pre-centos: ejecuta los prerequisitos de Centos (instalacion de paquetes tambien) \n
       postgresusers: crea la base de datos y usuarios postgres \n
       postinsthosts: ejecuta tareas necesarias para un post-deploy \n
       queuelog-trigger: ejecuta el trigger de queuelog \n
       sshkey-transfer: realiza la transferencia de la llave publica ssh entre usuarios freetech y root \n
       supervision: deploya la supervision \n "
       static: crea el archivo voip.cert \n
       wombat: instala y configura wombat \n
       echo -e $USAGE
       exit 1
}

Rama() {
    cd $current_directory
    echo "Creando directorio temporal de ansible"
    mkdir -p /var/tmp/ansible
    TMP_ANSIBLE='/var/tmp/ansible'
    echo "Copiando el contenido de ansible del repositorio al directorio temporal"
    cp -a $current_directory/* $TMP_ANSIBLE
    cd ..
    echo "Pasando al deploy de OmniAPP"
    set -e
    echo ""
    echo "Se iniciará deploy:"
    echo ""
    echo "      Version: $1"
    #echo "   Inventario: $INVENTORY"
    echo ""

    git checkout $1

    ################### Build.sh #####################

    #if [ "$VIRTUAL_ENV" = "" ] ; then
    #        echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
    #        exit 1
    #fi

    #set -e
    #cd $(dirname $0)
    TMP=/var/tmp/ominicontacto-build
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
    author="$(id -un)@$(hostname)"

    echo "Creando archivo de version | Branch: $branch_name | Commit: $commit | Autor: $author"
    cat > $TMP/ominicontacto/ominicontacto_app/version.py <<EOF

#
# Archivo autogenerado
#

OML_BRANCH="${branch_name}"
OML_COMMIT="${commit}"
OML_BUILD_DATE="$(env LC_hosts=C LC_TIME=C date)"
OML_AUTHOR="${author}"

if __name__ == '__main__':
    print OML_COMMIT


EOF

    echo "Validando version.py - Commit:"
    python $TMP/ominicontacto/ominicontacto_app/version.py

    # ----------
    export DO_CHECKS="${DO_CHECKS:-no}"
    rama=$1
}

Preliminar() {

    echo "Bienvenido al asistente de instalación de Omnileads"
    echo ""
    echo "Instalando ansible 2.4.0"

    if [ -z $ANSIBLE ]; then
        $PIP insthosts 'ansible==2.4.0.0'
    else
        echo "Ya tiene instalado ansible"
    fi

    if [ -f ~/.ssh/id_rsa.pub ]; then
        echo "Ya se han generado llaves para este usuario"
    else
        echo "Generando llaves públicas de usuario actual"
        ssh-keygen
    fi

    echo "Parámetros de la aplicación"
    echo -en "Ingrese valor de variable session_cookie_age: "; read session_cookie
    sed -i "s/\(^session_\).*/session_cookie_age=$session_cookie/" $TMP_ANSIBLE/hosts
    echo -en "Ingrese la contraseña de superuser de Omnileads: "; read admin_pass
    sed -i "s/\(^admin_pass\).*/admin_pass=$admin_pass/" $TMP_ANSIBLE/hosts
}

IngresarIP(){

    echo -en "Ingrese el formato de audio en el que quiere las grabaciones: "; read audio
#    sed -i "s/\(^MONITORFORMAT\).*/MONITORFORMAT = \'$audio\'/" $TMP_ANSIBLE/deploy/roles/oml_server/templates/oml_settings_local.py
    echo -en "Ingrese fqdn  de maquina a deployar: "; read omnicentos_fqdn
    sed -i "s/\(^omnicentos_fqdn=\).*/omnicentos_fqdn=$omnicentos_fqdn/" $TMP_ANSIBLE/hosts
    echo "Transifiendo llave publica a usuario root de Centos"
}

Desarrollo() {
    echo ""
    echo "#############################################################################"
    echo "Escogió la opción -d por lo que el deploy es para una máquina de desarrollo"
    echo "#############################################################################"
    echo ""
    sed -i "s/\(^desarrollo\).*/desarrollo=1/" $TMP_ANSIBLE/hosts
}

Tag() {
    echo -en "Ingrese IP  de maquina a deployar: "; read ip
    ssh-copy-id -i ~/.ssh/id_rsa.pub root@$ip
    echo "Ingrese 1 si va instalar en Debian, 2 si va a instalar en SangomaOS o 3 si va a instalar en Centos 7"
    echo -en "Opcion: ";read opcion

if [ $opcion -eq 1 ]; then
    echo -en "Ingrese IP  de omni-voip: "; read omnivoip_ip
    sed -i "s/\(^omnivoip_ip:\).*/omnivoip_ip: $omnivoip_ip/" /etc/ansible/hosts
    sed -i "s/\(^192.168.70.62\).*/$omnivoip_ip/" /etc/ansible/hosts.yml

    echo -en "Ingrese IP  de omni-app: "; read omniapp_ip
    sed -i "s/\(^omniapp_ip:\).*/omniapp_ip: $omniapp_ip/" /etc/ansible/hosts
    sed -i "s/\(^192.168.70.63\).*/$omniapp_ip/" /etc/ansible/hosts.yml

    echo -en "Ingrese fqdn  de omni-voip: "; read omnivoip_fqdn
    sed -i "s/\(^omnivoip_fqdn:\).*/omnivoip_ip: $omnivoip_fqdn/" /etc/ansible/hosts

    echo -en "Ingrese fqdn  de omni-app: "; read omniapp_fqdn
    sed -i "s/\(^omniapp_fqdn:\).*/omniapp_fqdn: $omniapp_fqdn/" /etc/ansible/hosts

    echo "Ejecutando Ansible en Debian"
    ansible-playbook -s /etc/ansible/omnivoip/omni-voip-debian.yml -u root
    ResultadoAnsible=`echo $?`

    echo "Finalizó la instalación omnileads"
    echo ""

elif [ $opcion -eq 2 ]; then

    sed -i "8s/.*/$ip ansible_ssh_port=22/" $TMP_ANSIBLE/hosts
    echo "Ejecutando Ansible en SangomaOS"
    ansible-playbook -s $TMP_ANSIBLE/deploy/omnileads-freepbx.yml -u root --extra-vars "BUILD_DIR=$TMP/ominicontacto RAMA=$rama" --tags "${array[0]},${array[1]}" --skip-tags "${array[2]}"
    ResultadoAnsible=`echo $?`
    echo "Finalizó la instalación omnileads"
    echo ""

elif [ $opcion -eq 3 ]; then

    sed -i "6s/.*/$ip ansible_ssh_port=22/" $TMP_ANSIBLE/hosts
    echo "Ejecutando Ansible en Centos"
    ansible-playbook -s $TMP_ANSIBLE/deploy/omnileads-centos.yml -u root --extra-vars "BUILD_DIR=$TMP/ominicontacto RAMA=$rama" --tags "${array[0]},${array[1]}" --skip-tags "${array[2]}"
    ResultadoAnsible=`echo $?`
    echo "Finalizó la instalación omnileads"
    echo ""

else
    echo "Parámetro inválido ingrese de nuevo"
    echo  ""
fi

if [ ${ResultadoAnsible} -ne 0 ];then
    echo "Fhostsó la ejecucion de Ansible, favor volver a correr el script"
    exit 0
#else

#if [ $opcion -eq 1 ]; then
#    echo "Ejecutando Ansible en Debian omni-app"
#    ansible-playbook -s /etc/ansible/deploy/omni-app-debian.yml -u freetech --extra-vars "BUILD_DIR=$TMP/ominicontacto" -K
#    echo "Ejecutando Ansible para copia de archivos entre servers"
#    ansible-playbook -s /etc/ansible/deploy/omniapp_second/transfer.yml -u root -K
#    echo "Finalizó la instalación de Omnileads"

fi

}

while getopts "r::t:ihd:" OPTION;do
	case "${OPTION}" in
		r) # Rama a deployar
            Rama $OPTARG
		;;
		i) #Realizar pasos y agregar opciones preliminares
		    Preliminar
		    IngresarIP
		;;
		t) #Tag
		    set -f # disable glob
           IFS=',' # split on space characters
            array=($OPTARG) # use the split+glob operator
   		    Tag $array
		;;
		h) # Print the help option
			Help
		;;
		d) #Cliente de desarrollo?
		    Desarrollo
		 ;;
	esac
done
if [ $# -eq 0  ]; then Help; fi

