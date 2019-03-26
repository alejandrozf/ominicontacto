#########################################################
### DevEnv. Omnileads Docker container for developers ###
#########################################################

A partir del esquema propuesto se van a crear 5 containers de Omnileads: asterisk, omniapp, kamailio, dialer y database (postgreSQL).

Adicionalmente se crea el container pbx-emulator.

Pasos previos

  * Instalar Docker-CE. Dependiendo del SO los pasos difieren, remitirse a la doc oficial: https://docs.docker.com/install/
  * Instalar docker-compose: https://docs.docker.com/compose/install/
  * Ejecutar los pasos de postinstalación de docker para poder usarlo sin necesidad de ser   
  superusuario: https://docs.docker.com/install/linux/linux-postinstall

Fresh Install

  * En el repositorio ominicontacto está creada la carpeta deploy/docker que contiene todos los archivos referentes de Docker.
  * Ir a la carpeta build/devenv-images
  * Esta carpeta contiene las bases de distros para comenzar a deployar un entorno. Inicialmente se uso el Dockerfile-ubuntu.
  * Hacer build del Dockerfile-ubuntu
  * Levantar el container de la imagen buildeada para ejecutar ansible dentro de este, para eso usamos el docker-compose file llamado ubuntu-base.yml y levantantamos los containers con este comando:
      $ cd deploy/docker/devenv
      $ docker-compose -f ubuntu-base.yml up -d
  * Una vez el container está arriba básicamente se tiene una instalación modo cluster. Remitirse al manual de instalación para setear el entorno de ansible para este tipo de instalación.
  * Esperar a que finalice la instalación. Si esta fue exitosa ya se podrá ingresar a omnileads editando el archivo de hosts para que resuelva 172.16.0.6 omniapp e ingresando por web a https://omniapp
  * Ya puedes hacer commit/push atu tu docker-hub de los containers creados

De esta manera ya se tienen en el docker hub las imagenes buildeadas, listas para ser utilizada en el devenv-stack.yml.

If you have any suggestions to power up this devenv, if you see any error or if you want to cooperate with us,  you can open an issue in Omnileads github repository https://gitlab.com/omnileads/ominicontacto or send us a mail to support@omnileads.net

Thank you for your cooperation!
