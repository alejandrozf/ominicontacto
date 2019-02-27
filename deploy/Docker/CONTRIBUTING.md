

MANTENIMIENTO Y CONSTRUCCION DE IMAGENES DE DOCKER PARA FREETECH SOLUTIONS

En este documento se describe el proceso para la creación de nuevas imágenes de Omnileads, el cual será usado por los devs, testers o cualquiera que quiera tener Omnileads rapido y sin tener que ejecutar el playbook de Ansible en máquinas fisicas.

Pasos previos:

Instalar Docker-CE. Dependiendo del SO los pasos difieren, remitirse a la doc oficial:
  - https://docs.docker.com/install/
Instalar docker-compose:
  - https://docs.docker.com/compose/install/
Ejecutar los pasos de postinstalación de docker para poder usarlo sin necesidad de ser superusuario:
  - https://docs.docker.com/install/linux/linux-postinstall/

Fresh Install de Omnileads:

Como se ejemplo, se hace de cuenta que se va a hacer un fresh install del release-1.2.0

En el repositorio ominicontacto está creada la carpeta deploy/Docker que contiene todos los archivos referentes de Docker. Ir a la carpeta
Ir a la carpeta build/docker-DevEnv-images/
Revisar el Dockerfile-ubuntu para ver lo que hace. Este es el Dockerfile template para levantar “nodos desde ceros”. Ya hay una imagen subida de este Dockerfile al dockerhub llamada freetechsolutions/base-ubuntu
Loguearse al dockerhub usando este comando:
    $ docker login
Se  pedirá usuario y contraseña, estos son:
    usuario: freetechsolutions
    password: S0p0rt3.2019!    
Levantar el container de la imagen freetechsolutions/base-ubuntu para ejecutar ansible dentro de este, para eso usamos el docker-compose file llamado ubuntu-base.yml y levantantamos el container con este comando:
  $ docker-compose -f ubuntu-base.yml up -d
Una vez el container está arriba se ejecuta el siguiente comando para iniciar la instalación dentro del container:
  $ docker exec -it ubuntu-base /bin/bash -c "./deploy.sh -i -a"

NOTA: si se quiere instalar un devenv, cerciorarse que en su repositorio esté en la rama develop, y ejecutar:
  $ docker exec -it ubuntu-base /bin/bash -c "./deploy.sh -i -a -d"

Esperar a que finalice la instalación. Si esta fue exitosa ya se podrá ingresar a omnileads editando el archivo de hosts para que resuelva 172.16.0.2 omnileads.example.com e ingresando por web a https://omnileads.example.com
Luego de finalizadas las revisiones de que el entorno es funcional se está listo para convertir este container en una imagen del release que se haya instalado, para ello se usa este comando:
    $ docker commit ubuntu-base freetechsolutions/release:1.2.0
Finalizado el comando se pushea el commit realizado con:
    $ docker push freetechsolutions/release:1.2.0

De esta manera ya se tiene en el docker hub la imagen buildeada, lista para ser utilizada en el stack.yml.

NOTA: versiones anteriores al release-1.2.0 (sin incluirlo) no podrán ser subidas como imágen de Docker

Upgrade de una imagen

Para el entorno de desarrollo va a suceder que hay hacer upgrade la imágen, debido a que puede cambiar algo de infraestructura.
Para el devenv no es necesario tener que hacer instalaciones de ceros. Se puede hacer upgrade de la imagen inicial que es la 1.0. Así también, si se quiere, se puede sacar un una imagen de un release posterior al 1.2.0 realizando el respectivo upgrade del container, commiteando y pusheando los cambios con el  tag correspondiente. Los pasos para upgradear la  imagen serian:

Tener un container levantado de la imágen que se quiere upgradear.
Realizar el correspondiente postinstall
Commitear y pushear los cambios

Docker, comandos básicos

Loguearse al dockerhub
  $ docker login
Buildear una imagen
  $ docker build -f Dockerfile --tag=TAG .
Listar contenedores activos
  $ docker ps
Listar imagenes
  $ docker image ls
Bajar un contenedor
  $ docker stop container_name
Abrir una shell de un contenedor
  $ docker exec -it container_name /bin/bash
Ejecutar un comando sin abrir una shell con el usuario  omnileads del container
  $ docker exec -i -u omnileads container_name /bin/bash -c “ls .”
Verificar volumenes creados
  $ docker volume ls
Inspeccionar detalles de un volumen en particular
  $ docker volume inspect volume_name
Eliminar todos los containers, imagenes, volumenes y redes de containers stoppeados
  $ docker system-prune -a

Mas info revisar la documentacion oficial:

https://docs.docker.com/get-started/
https://labs.play-with-docker.com
https://www.datadriven-investment.com/dockercon18/#tutorial

Docker- compose, comandos básicos

Levantar un container usando docker-compose (es mucho más práctico que hacer docker run, para empaparse mas leer esto: https://docs.docker.com/compose/ https://docs.docker.com/compose/compose-file/

Levantar la configuración de un docker-compose file
  $ docker-compose -f docker-compose-file up -d
Bajar todos los servicios levantados, removiendo containers, redes, imagenes y volumenes
  $ docker-compose down
Iniciar servicios
  $ docker-compose start
Detener servicios
  $ docker-compose stop
