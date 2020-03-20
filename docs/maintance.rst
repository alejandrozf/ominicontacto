******************************
Gestiones del administrador IT
******************************

.. _about_maintance_envvars:

Variables de entorno
*********************

A lo largo de esta sección vamos a estar comentando procedimientos que implican volver a las contraseñas utilizadas en el deploy a través del archivo *inventory*.
Como es sabido, dicho archivo es editado a la hora de realizar la instalación, pero posteriormente vuelve a su estado original quedando todas las variables y sus valores
disponibles como *variables de entorno* del sistema operativo.

Para consultar dichas variables podemos ejecutar un *cat* sobre el archivo */etc/profile.d/omnileads_envars.sh*.

.. code-block:: bash

 cat /etc/profile.d/omnileads_envars.sh

 AMI_USER=omnileadsami
 AMI_PASSWORD=5_MeO_DMT
 ASTERISK_IP=192.168.95.163
 ASTERISK_HOSTNAME=localhost.localdomain
 ASTERISK_LOCATION=/opt/omnileads/asterisk
 CALIFICACION_REAGENDA=Agenda
 DJANGO_PASS=098098ZZZ
 DJANGO_SETTINGS_MODULE=ominicontacto.settings.production
 EPHEMERAL_USER_TTL=28800
 EXTERNAL_PORT=443
 INSTALL_PREFIX=/opt/omnileads/
 KAMAILIO_IP=192.168.95.163
 KAMAILIO_HOSTNAME=localhost.localdomain
 KAMAILIO_LOCATION=/opt/omnileads/kamailio
 MONITORFORMAT=mp3
 MYSQL_PWD=098098ZZZ
 NGINX_HOSTNAME=localhost.localdomain
 OMNILEADS_HOSTNAME=localhost.localdomain
 PGHOST=localhost.localdomain
 PGDATABASE=omnileads
 PGUSER=omnileads
 PGPASSWORD=my_very_strong_pass
 PYTHONPATH=$INSTALL_PREFIX
 REDIS_HOSTNAME=localhost
 SESSION_COOKIE_AGE=3600
 TZ=America/Argentina/Cordoba
 WOMBAT_HOSTNAME=localhost.localdomain
 WOMBAT_USER=demoadmin
 WOMBAT_PASSWORD=demo

 export AMI_USER AMI_PASSWORD ASTERISK_IP ASTERISK_HOSTNAME ASTERISK_LOCATION CALIFICACION_REAGENDA DJANGO_SETTINGS_MODULE DJANGO_PASS EPHEMERAL_USER_TTL EXTERNAL_PORT INSTALL_PREFIX KAMAILIO_IP KAMAILIO_HOSTNAME KAMAILIO_LOCATION MONITORFORMAT MYSQL_PWD NGINX_HOSTNAME OMNILEADS_HOSTNAME PGHOST PGDATABASE PGUSER PGPASSWORD PYTHONPATH REDIS_HOSTNAME SESSION_COOKIE_AGE TZ WOMBAT_HOSTNAME WOMBAT_USER WOMBAT_PASSWORD

De esta manera el administrador podrá disponer de todos estos parámeros operativos cuando desee.

.. Important::

  No editar este archivo bajo ninguna condición

Configuración del módulo de *Discador predictivo*
*************************************************
Antes que nada se notifica que si la instancia de OML desplegada en los pasos anteriores, NO contemplan el uso de campañas con discado saliente predictivo, este paso puede ser omitido.
OMniLeads necesita de una herramienta de terceros para implementar las campañas con discador predictivo. Esta herramienta se basa en licencias de software comerciales que deben
ser gestionadas con el fabricante.

De todas maneras el sistema puede ser utilizado con un canal de pruebas que otorga como demo. Por lo tanto podemos configurar el componente y correr pruebas de concepto
antes de adquirir licencias para una operación real.

Si se desean correr campañas predictivas, se debe generar la siguiente configuración básica de Wombat Dialer .
Para generar esta configuración debemos seguir una serie de pasos que comienzan con el acceso a la URL correspondiente.

http://omnileads.yourdomain:8080/wombat ó http://XXX.XXX.XXX.OML:8080/wombat

.. Note::

  En caso de estar corriendo OMniLeads en **Docker** la URL es:
  http://XXX.XXX.XXX.OML:442/wombat

  Donde XXX.XXX.XXX.OML es la dirección IP del docker engine host

Al ingresar por primera vez, se debe proceder con la creación de la base de datos MariaDB que utiliza Wombat Dialer.
Hacer click en botón remarcado en la figura 1.

.. image:: images/maintance_wd_2.png

*Figure 1: DB create*

Luego es el momento de ingresar la clave del usuario root de MySQL y hacer click en botón remarcado en la figura 2.


.. Note::

  El password del usuario root de MySQL fue configurado en el archivo *inventory* al momento de la instalación y quedó disonible como variable de entorno que puede ser consultada
  según el procedimiento expuesto al comienzo de esta sección.


Procedemos entonces con la creación de la base de datos MySQL que utilizará de ahora en más el componente Wombat Dialer.

.. image:: images/maintance_wd_mariadb_create.png

*Figure 2: MySQL root password*


Una vez creada la base de datos MariaDB que utiliza Wombat Dialer, se procede con el primer login.

.. image:: images/maintance_wd_mariadb_post_create.png

*Figure 3: Login post db create*


A continuación se debe realizar un login en la interfaz de administración de Wombat Dialer para avanzar con la configuración
de parámetros necesarios para la interacción con OML.

Al ingresar se despliega una pantalla como la siguiente, donde debemos acceder con el usuario y passwords que se generaron en la instalación.

.. image:: images/maintance_wd_1.png

*Figure 4: Access to WD*

Una vez adentro del sistema, se procede con la configuración de dos parámetros básicos necesarios para dejar lista la integración con OMniLeads.
Para ello debemos acceder al menú de "Configuración básica" como se indica en la figura 5.

.. image:: images/maintance_wd_config1.png

*Figure 5: WD basic config*

En este menú se debe generar en primer lugar se debe generar una nueva instancia de conexión dentro de la sección "Asterisk Servers"
como se expone en la figura 6.

.. image:: images/maintance_wd_config2.png

*Figure 6: WD basic config - AMI Asterisk*

En el siguiente punto, se configura un Troncal utilizando un "Nombre del troncal" arbitrario, pero con la cadena de llamado marcada
en la figura 7. **Local/${num}@from-oml/n**

.. image:: images/maintance_wd_config3.png

*Figure 7: WD basic config - Asterisk Trunk*

Por último, recuerde dar "play" al servicio de dialer, tal como lo indica la siguiente figura 8.

.. image:: images/maintance_wd_config4.png

*Figure 8: WD activate*

Finalmente la plataforma se encuentra habilitada para gestionar llamadas predictivas. La instalación por defecto cuenta con una licencia de Wombat Dialer demo de un canal.


Backup & Restore
****************
OMniLeads dispone de un script para llevar a cabo las tareas de backup/restore.

.. important::

  En caso de hacer el restore en una nueva máquina, es necesario que dicha máquina:

  * Tenga OMniLeads instalado en la misma version que la maquina productiva
  * Tenga misma IP, mismo hostname y misma credenciales de la maquina productiva

Para realizar un backup:

Debemos acceder por ssh al host donde tenemos corriendo OMniLeads. Una vez dentro del host se ejecutan los siguiente comandos.

::

  su omnileads -
  cd /opt/omnileads/bin
  ./backup-restore.sh -b

La ejecución del script arroja una salida similar a la de la figura 9.

.. image:: images/maintance_backup_1.png

*Figure 9: backup*

Como se puede observar, nos indica cómo realizar el restore de dicho backup.

Dentro del path **/opt/omnileads/backup**, se generan los archivos ".tgz" que contienen los backups ejecutados.

Si el restore se realiza en nuevo host, entonces se debe dejar disponible el archivo generado en el backup dentro del path **/opt/omnileads/backup**.

Para llevar a cabo un restore, se debe ejecutar:

::

  su omnileads
  cd /opt/omnileads/bin/
 ./backup-restore.sh -r nombre_del_archivo_de_backup


Por ejemplo:

::

  su omnileads
  cd /opt/omnileads/bin/
 ./backup-restore.sh -r 20190211_database.tgz

No hace falta agregar el path completo de ubicación del backup.

Un restore exitoso arroja una salida similar a la figura 10.

 .. image:: images/maintance_backup_2.png

 *Figure 10: restore*

Una vez finalizado el restore, ejecutar el siguiente comando para regenerar los archivos de configuración y valores de AstDB de la instancia que se restoreó:

::

 /opt/omnileads/bin/manage.sh regenerar_asterisk

Actualizaciones
***************

OMniLeads genera releases continuos, lo cual implica tener que actualizar el sistema periodicamente.

.. important::

  **Upgrade anterior a release-1.3.1 (incluyendolo)**

  * Es **IMPRESCINDIBLE** contar con las contraseñas de *postgresql*, *mysql* y *django admin* que se usaron durante la instalación. Tendrá que asignarlas nuevamente en el archivo *inventory*. Si no se utilizan las mismas contraseñas que se usaron, el upgrade cambiará las contraseñas por aquellas que se encuentren en el inventory
  * Si no utiliza la misma contraseña de MySQL que se tenia previamente, el upgrade fallará.

  **Upgrade después de release-1.3.1**

  * Si no se quieren cambiar alguna variable basta con definir el tipo de instalación.
  * Si se quieren cambiar alguna variable, ingresarla y la actualización se encargará de ello.

A continuación se exponen los pasos a seguir para llevar a cabo una nueva actualización de la plataforma. Esta tarea también se realiza con el script "deploy.sh".
Las actualizaciones se anuncian por los canales de comunicaciones oficiales del proyecto.
Dependiendo el método de instalación que se haya seleccionado:

**Instalación Self-Hosted**

* Acceder como root a la maquina con OMniLeads instalado
* Posicionarse sobre el directorio donde reside el script “deploy.sh”

::

 cd ominicontacto/deploy/ansible

* Asumiendo que estamos trabajando sobre los release estables (master). Se debe ejecutar un "git pull origin master" para traernos las actualizaciones del repositorio.

.. code-block:: bash

 git pull origin master

* Descomentar en el archivo de inventario la línea para instalación self-hosted

.. code-block:: bash

  ##########################################################################################
  # If you are installing a prodenv (PE) AIO y bare-metal, change the IP and hostname here #
  ##########################################################################################
  [prodenv-aio]
  localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)
  #10.10.10.100 ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)

* A continuación se ejecuta el script con el parámetro -u (update). Esta ejecución tomará unos minutos e implica el aplicar todas las actualizaciones descargadas con el "git pull origin master" sobre nuestra instancia de OMniLeads.

::

 ./deploy.sh -u --iface=**your_NIC_name**

* Si todo fluye correctamente, al finalizar la ejecución de la tarea veremos una pantalla como muestra la figura 11.

.. image:: images/maintance_updates_ok.png

*Figure 11: updates OK*


**Instalación desde workstation Linux remoto**

* Se debe acceder al repositorio clonado en nuestra maquina workstation, para desde allí correr la actualización sobre el host Linux OMniLeads.

::

 cd PATH_repo_OML
 git pull origin master
 cd ominicontacto/deploy/ansible

* A continuación y como en cada ejecución del script "deploy.sh", se debe repasar el archivo de inventory, velando por la coincidencia de la dirección IP de host donde corre OMniLeads y vamos a actualizar.

::

  ##########################################################################################
  # If you are installing a prodenv (PE) AIO y bare-metal, change the IP and hostname here #
  ##########################################################################################
  [prodenv-aio]
  #localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)
  10.10.10.100 ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)

.. note::

  * Se debe tener en cuenta que para instalación remota, se debe utilizar la línea con el parámetro "ansible_ssh_port=22" (donde 22 es el puerto por defecto, pero es normal tambien que se utilice otro puerto) dentro de la sección [prodenv-aio]
  * Se ejecuta el script con el parámetro -u (update). Esta ejecución tomará unos minutos e implica el aplicar todas las actualizaciones descargadas con el "git pull origin master" sobre nuestra instancia de OMniLeads.

::

	./deploy.sh -u

* Finalmente, la plataforma queda actualizada a la última versión estable "master"

.. image:: images/maintance_updates_ok.png

*Figure 12: updates from ansible remote OK*

.. note::

  Las instalaciones AIO dejarán de ser soportadas en un futuro para Debian y Ubuntu, por lo que se recomienda usar CentOS

**Instalación basada en contenedores Docker**

.. important::

  Si ya tiene un entorno instalado con el script *install.sh* y quiere pasar a actualizar con Ansible, tiene que ingresar las variables correspondientes en el archivo de inventario. Es **MUY IMPORTANTE** que ingrese la misma password MYSQL.

Una vez instalado OMniLeads en docker no siempre va a a ser necesario ejecutar el instalador de Ansible para realizar la actualización de la plataforma, salvo en estos casos:

1. Upgrade de algun componente que se instala en el Docker Host (rtpengine o postgresql).
2. Modificación de algún parámetro del docker-compose file.
3. Adición de una variable de entorno nueva que requiera el sistema.

En cada release nos encargaremos de avisar si es necesario o no ejecutar el instalador.

* **En caso de ser necesario:** basta con seguir los pasos para :ref:`about_install_docker_linux` a excepción de que ya no es necesario ingresar :ref:`about_install_inventory_vars`, a no ser que se quiera modificar alguna variable. En la variable **oml_release**, ingresar el release al que se quiere upgradear.
* **En caso de NO ser necesario:** basta con ingresar al folder `/home/omnileads/prodenv/` y alli modificar la variable **RELEASE** del archivo `.env`.

Luego realizar un `service omnileads-prodenv restart`.

.. code-block:: bash

  systemctl restart omnileads-pbx

En el proceso de reinicio cuando se invoca el *docker-compose* al percatarse del *tag* de versión modificado se procede con la descarga de las nuevas imagenes que implementan el release especificado.

.. note::

  1. Los nuevos releases suelen traer nuevo codigo JavaScript. El browser mantiene el código viejo en su cache por lo que se **recomienda** instalar en el browser un addon para borrar la cache. *Clear cache* para *Google Chrome*, por ejemplo

.. _about_maintance_change_ip_passwords:

Cambios de los parámetros de red (Hostname y/o Dirección IP) y cambios de contraseñas de servicios
***************************************************************************************************

**Para entorno AIO**

* Para llevar a cabo éstas tareas, debemos ejecutar nuevamente el script "deploy.sh".
* **Si se quiere cambiar IP** Se debe ingresar con el usuario root al sistema, cambiar la dirección IP a nivel sistema operativo y/o hostname y asegurarnos de que el host tomó los cambios. Se recomienda un *reboot* del sistema.
* **Si se quieren cambiar constraseñas** cambiar la contraseña que se desee, remitirse a :ref:`about_install_inventory_vars` para revisar las variables de contraseñas.

Llevar a cabo esta tarea conlleva ejecutar el script deploy.sh asi:

.. code:: bash

  ./deploy.sh -u

.. important::

  Asegurarse de correr el script en el mismo release en el cual se encuentra instalado el sistema, de lo contrario realizará actualización del software.

**Para entorno docker**

La única diferencia con el entorno AIO es que debe correr el script deploy.sh así:

.. code-block:: bash

  ./deploy.sh --docker-deploy

Desbloqueo de usuarios
***********************

OMniLeads cuenta con un sistema de bloqueo de usuarios, cuando alguno ingresa la contraseña erronea tres veces. Esta es una medida de seguridad implementada para evitar ataques de fuerza bruta en la consola de Login de la plataforma.
El usuario administrador tiene la posibilidad de desbloquar algún usuario que haya sido bloqueado por ingresar su contraseña errónea sin querer.

Para desbloquearlo se ingresa a la siguiente URL: https://omnileads-hostname/admin, esta URL despliega la llamada **Consola de Administración de Django**.

.. image:: images/django_admin.png

*Figure 13: Django admin console*


Allí, ingresar las credenciales del usuario admin. Luego hacer click en el botón **Defender**

.. image:: images/defender.png

*Figure 14: Defender in django admin*

Esto abre la administración de **Django Defender** (https://github.com/kencochrane/django-defender) que es el plugin de Django usado para manejar esto. Hacer click en **Blocked Users**

.. image:: images/blocked_users.png

*Figure 15: Blocked users view*

Se observará el usuario bloqueado. Basta con hacer click en **Unblock** para desbloquearlo.

.. image:: images/unblock.png

*Figure 16: Unblock user view*

Ya el usuario podrá loguearse sin problema.

Desinstalación de OMniLeads
****************************

Si por alguna razón quiere desinstalar OMniLeads de su máquina o VM se cuenta con un script para ello. Ya viene incorporado en el proceso de instalación, basta con ejecutarlo:

.. code::

  oml-uninstall

Este script:

* Desinstala los servicios esenciales de omnileads: asterisk, kamailio, rtpengine, mariadb, postgresql, wombat dialer, redis, nginx y omniapp.
* Borra la carpeta /opt/omnileads (incluyendo grabaciones)
* Elimina las bases de datos

.. note::

  El script no desinstala la paquetería de dependencias usadas para la instalación de los servicios.

.. important::

  Tener cuidado al ejecutarlo, una vez ejecutado no hay forma de recuperar el sistema.
