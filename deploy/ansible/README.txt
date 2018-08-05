"Soundtracks OML"
https://www.youtube.com/watch?v=x2HZQ70hpbU - John Coltrane
https://www.youtube.com/watch?v=ts3YWVFUnvU&t=339s - Om

Seteo de entorno de instalación de Omnileads Ansible-In-One.

1 - Sistema Operativo
----------------------

    Probado con Centos7 minimal instalattion y SangomaOS

    - Tener creado el usuario omnileads con contraseña
    - Tener seteado IP del server, DNS y nombre de dominio
    - Realizar un update al server: yum update -y

    Si está instalando en Issabel
    ----------------------------------------
    (comming soon)
    - Tener instalada la ultima versión del kernel del SO. Para Centos7, el ultimo kernel estable es 3.10.0-693.21.1.el7.x86_64
            yum install kernel-devel kernel-headers -y
    - Instalar el repositorio epel-release
            yum install epel-release
    - Instalar git y pip para poder clonar el repo e instalar ansible, para Centos7
            yum install python2-pip git -y
    - Editar el sudoers para que el usuario omnileads tenga privilegios root
            visudo
            Agregar la linea:  omnileads     ALL=(ALL)       ALL
    - Reboot al server

2 - Clonacion del repositorio usando bitbucket
-----------------------------------------------

    - Una vez el server arriba, loguearse con el usuario omnileads  y realizar los siguientes pasos:
            ssh-keygen
            git config --global user.name "freetech"
            git config --global user.email "desarrollo@freetechsolutions.com.ar"
            cat ~/.ssh/id_rsa.pub
    - Clonar el repositorio en la ubicación que pueda acceder el usuario omnileads. El repositorio está alojado en https://bitbucket.org/product .
      Para loguearse y poder agregar la key ssh deben utilizarse las siguientes credenciales:

            Usuario: desarrollo@freetechsolutions.com.ar
            Contraseña: Freetech123
    - En la siguiente URL clickear en “Add Key” https://bitbucket.org/account/user/freetechdesarrollo/ssh-keys/
    - Elegir un nombre para la nueva llave y copiar la salida del comando: cat .ssh/id_rsa.pub,
      que representa la llave pública que nos permitirá clonar el repositorio desde la terminal.
    - Ejecutar los siguientes comandos:
            git clone git@bitbucket.org:freetechdesarrollo/ominicontacto.git
            cd ominicontacto
            git fetch
            git checkout develop

3 - Ejecución y explicación del script deploy.sh
-----------------------------------------------

    ./deploy.sh -r develop -i -t all
        Opciones a ingresar:
            -h: ayuda
            -r: rama a deployar (ej: -r develop)
            -i: instala ansible, ingresar formato de grabaciones, pass de OML
            -t: ingresar ip, opcion de SO, tags de ansible (TAREAS A EJECUTAR: all o postinstall)


Seteo de entorno de instalación de Omnileads Ansible-In-Two.
------------------------------------------------------------
(ver manual de instalacion)

Ejecucion del script ansibleintwo.sh

./ansibleintwo.sh
