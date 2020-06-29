.. _about_install_faq:

***************
Errores comunes
***************

A continuación se listan los problemas típicos que se presentan a la hora de realizar una instalación:

- **La instalación finaliza exitosamente, sin embargo al ingresar a la URL tenemos un error o directamente no aparece la pantalla de login**

Compruebe que ha deshabilitado SELinux y Firewald (:ref:`about_install_prerequisitos`).

- **Al ejecutar el script de deploy falla la lectura de variables del inventory**

Comprobar que las variables (TZ, postgres_user, postgres_password, admin_pass, ami_user, ami_pass y TZ) estén descomentadas y con un valor asignado. Aunque se utilicen los valores
por defecto (no recomendable en producción), se debe descomentar la linea correspondiente a cada variable.

- **Al ejecutar el script de deploy falla en el parámetro iface**

Recordar que *iface* hace referencia a la interfaz de red del host (eth0, eth1, ens18, ens0s3, etc.).

- **El server NO tiene salida a internet / El server no resuelve dominios (no funcionan o no tiene configurados los DNS)**

- **Falla por timeout de algún paquete o repositorio no disponible temporalmente**

En estos casos se debe volver a ejecutar el deploy. Al utilizar paquetes de internet, la no disponibilidad temporal de algún repositorio o conexión a internet puede afectar la isntalación.

- **Equivocarse a la hora de ejecutar un método de instalación y tipo de arquitectura con respecto a la sección del archivo inventory**

A la hora de ejecutar una instalación Self-Hosted o Deployer-Nodes de una arquitectura clasica (AIO) o basada en contenedores, hay que estar muy atentos en trabajar con las secciones
adecuadas para cada combinación: [prodenv-aio], [prodenv-docker] y sus lineas.

- **Falla en la Task asociada a RTPengine**

Esto sucede cuando no se ha instalado el paquete *kernel-devel* o bien el paquete no coincide con la versión del kernel (:ref:`about_install_prerequisitos`).


Errores en método de instalación Deployer-nodes
************************************************

- **El script de deploy nos arroja falta de permisos**

Recordar que en el *deployer* se debe ejecutar el script con *sudo*. Recordar que se deben instalar paquetes como *sudo, openssh-server o python-minimal* antes de correr el script de *deploy.sh*

- **No se configuró correctamente el acceso ssh del host destino de la instalación**.

Revisar estado del firewall. Comprobar acceso remoto por ssh con el usuario *root*


Arquitectura basada en contenedores docker
******************************************

1. **Como cambiar las contraseñas de los containers docker?**

Hay tres contraseñas importantes:
  - **OMniLeads Web GUI:** cambiar la variable $DJANGO_PASS en el archivo .env y reiniciar el container de omniapp: **docker restart oml-omniapp-prodenv**
  - **Postgresql y MySQL:** observar la sección de :ref:`about_maintance_change_ip_passwords`

2. **El segmento de red LAN donde hay que desplegar OML es *192.168.15.0/24* o cae dentro de un segmento que lo abarca**

Por defecto el entorno docker se levanta con esta subred interna dentro del rango mencionado. Cambiar la variable **SUBNET** y utilizar otro segmento de red que no colisione con el de
vuestra LAN, esto se hace en el archivo .env. Luego reiniciar el servicio **omnileads-prodenv**.

3. **El entorno no inicia debido a que docker-compose dice que hay un puerto en uso, que hago?**

Hay tres puertos del Docker Host que se usan para mapear puertos internos de los containers, estos son:

*  WD_EXT_PORT=442  --> mapea con el puerto 8080/tcp del contenedor que aloja el componente Wombat Dialer. Esto permite acceder a la GUI de WD.
*  NGINX_EXT_PORT=444 --> mapea con el puerto 443/tcp en Omniapp para acceder a la GUI de OMniLeads.
