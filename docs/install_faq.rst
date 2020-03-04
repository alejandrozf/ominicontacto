.. _about_install_faq:


Errores comunes
^^^^^^^^^^^^^^^^

Self Hosted
************

- El server no tiene internet o no resuelve dominios (configuración de DNS). **Compruebe el acceso a internet del host (por ej: actualizando paquetes - apt-get update | yum update).**
- Timeout de algún paquete que se intenta bajar. Puede volver a intentar ejecutar el deploy y si vuelve a fallar, la opción puede ser instalar el paquete desde la terminal.
- No ejecutó el script de deploy con *sudo*, en el host deployer.

Ansible Remoto
***************
- En caso de que el deployer sea Ubuntu-Debian, recordar que se deben instalar paquetes como *sudo, openssh-server o python-minimal* antes de correr el script de *deploy.sh*
- Timeout de algún paquete que se intenta bajar. Puede volver a intentar ejecutar el deploy y si vuelve a fallar, la opción puede ser. *Instalar el paquete desde la terminal.*
- Falla por mala sintaxis o falta de definición de *hostname* y *dirección IP* en el archivo *inventory*. *Revisar archivo inventory*
- No se configuró correctamente el acceso ssh del host destino de la instalación. *Revisar estado del firewall. Comprobar acceso remoto por ssh con el usuario root*
- En caso de contar con algún host Ubuntu-Debian, recordar que se deben instalar paquetes como *sudo, openssh-server o python-minimal* antes de correr el script de *deploy.sh*

Para instalación docker
*************************

1. **Como cambiar las contraseñas de los containers docker?**

Hay tres contraseñas importantes: 
  - **OMniLeads Web GUI:** cambiar la variable $DJANGO_PASS en el archivo .env y reiniciar el container de omniapp: **docker restart oml-omniapp-prodenv**
  - **Postgresql y MySQL:** observar la sección de :ref:`about_maintance_change_ip_passwords`

2. **Mi segmento de red LAN es 192.168.15.0/24 o está dentro de este segmento**

Por defecto el entorno docker se levanta con esta subred interna. Cambiar la variable **SUBNET** en el archivo .env y reiniciar el servicio **omnileads-prodenv**.

3. **El entorno no inicia debido a que docker-compose dice que hay un puerto en uso, que hago?**

Hay tres puertos del Docker Host que se usan para mapear puertos internos de los containers, estos son:

*  WD_EXT_PORT=442  --> mapea con el puerto 8080/tcp en Wombat Dialer, para acceder a la GUI
*  NGINX_EXT_PORT=444 --> mapea con el puerto 443/tcp en Omniapp para acceder a OMniLeads GUI
*  PG_EXT_PORT=445  --> mapea con el puerto 5038/tcp en Postgresql para acceder a la base de datos de OMniLeads
