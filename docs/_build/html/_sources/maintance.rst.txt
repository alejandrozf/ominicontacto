******************************
Gestiones del administrador IT
******************************

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

Al ingresar por primera vez, se debe proceder con la creación de la base de datos MariaDB que utiliza Wombat Dialer.
Hacer click en botón remarcado en la figura 2.

.. image:: images/maintance_wd_2.png

*Figure 1: DB create*

Luego es el momento de ingresar la clave del usuario root de MySQL y hacer click en botón remarcado en la figura 3.
Nota: el password del motor MariaDB fue configurado dentro del archivo "inventory" antes de activar la instalación del sistema. (En el mismo directorio en el que clonó el repositorio de OML).


.. image:: images/install_my_inventory.png


.. image:: images/maintance_wd_mariadb_pass.png

*Figure 2: MariaDB root password*


Procedemos entonces con la creación de la base de datos MariaDB que utilizará de ahora en más el componente Wombat Dialer.

.. image:: images/maintance_wd_mariadb_create.png

*Figure 3: MariaDB root password*


Una vez creada la base de datos MariaDB que utiliza Wombat Dialer, se procede con el primer login.

.. image:: images/maintance_wd_mariadb_post_create.png

*Figure 4: Login post db create*


A continuación se debe realizar un login en la interfaz de administración de Wombat Dialer para avanzar con la configuración
de parámetros necesarios para la interacción con OML.

Al ingresar se despliega una pantalla como la siguiente, donde debemos acceder con el usuario y passwords que se generaron en la instalación.
Recordar que éstas variables se encuentran en la copia del archivo inventory (my_inventory).

.. image:: images/maintance_wd_1.png

*Figure 5: Access to WD*

Una vez adentro del sistema, se procede con la configuración de dos parámetros básicos necesarios para dejar lista la integración con OMniLeads.
Para ello debemos acceder al menú de "Configuración básica" como se indica en la figura 6.

.. image:: images/maintance_wd_config1.png

*Figure 6: WD basic config*

En este menú se debe generar en primer lugar se debe generar una nueva instancia de conexión dentro de la sección "Asterisk Servers"
como se expone en la figura 7.

.. image:: images/maintance_wd_config2.png

*Figure 7: WD basic config - AMI Asterisk*

En este paso debeŕa ingresar el usuario y contraseña AMI disponible en el archivo *inventory* utilizado en la instalación.

.. image:: images/maintance_wd_config_inventory.png

*Figure 9: WD basic config - AMI Asterisk user & pass*

En el siguiente punto, se configura un Troncal utilizando un "Nombre del troncal" arbitrario, pero con la cadena de llamado marcada
en la figura 9. Local/${num}@from-oml/n

.. image:: images/maintance_wd_config3.png

*Figure 9: WD basic config - Asterisk Trunk*

Por último, recuerde dar "play" al servicio de dialer, tal como lo indica la siguiente figura 10.

.. image:: images/maintance_wd_config4.png

*Figure 10: WD activate*

Finalmente la plataforma se encuentra habilitada para gestionar llamadas predictivas. La instalación por defecto cuenta con una licencia de Wombat Dialer demo de un canal.


Back & Restore
**************
OMniLeads dispone de un script para llevar a cabo las tareas de backup/restore.

Para realizar un backup:

Debemos acceder por ssh al host donde tenemos corriendo OMniLeads.
Una vez dentro del host se ejecutan los siguiente comandos.

::

  su omnileads -
  cd /opt/omnileads/bin
  ./backup-restore.sh -b

La ejecución del script arroja una salida similar a la de la figura 11.

.. image:: images/maintance_backup_1.png

*Figure 11: backup*


Como se puede observar, nos indica cómo realizar el restore de dicho backup.

Dentro del path **/opt/omnileads/backup**, se generan los archivos ".tgz" que contienen los backups ejecutados.

Si el restore se realiza en nuevo host, entonces se debe dejar disponible el archivo generado en el backup dentro del path **/opt/omnileads/backup**.

Para llevar a cabo un restore, se debe ejecutar:

::

 ./backup-restore.sh -r nombre_del_archivo_de_backup


Por ejemplo:

::

 ./backup-restore.sh -r 20190211_database.tgz


Un restore exitoso arroja una salida similar a la figura 12.

 .. image:: images/maintance_backup_2.png

 *Figure 12: restore*


Actualizaciones
***************

OMniLeads es forjado bajo un paradigma de releases continuos, lo cual implica un flujo de actualizaciones constantes.
Por ello es muy importante llevar a cabo de manera limpia las actualizaciones.

A continuación se exponen los pasos a seguir para llevar a cabo una nueva actualización de la plataforma. Esta tarea también se realiza
con el script "deploy.sh".

Las actualizaciones se anuncian por los canales de comunicaciones oficiales del proyecto.
Dependiendo el método de instalación que se haya seleccionado:


**Instalación Self-Hosted**

Acceder como root al host omnileads
Posicionarse sobre el directorio donde reside el script “deploy.sh”

::

 cd ominicontacto/deploy/ansible

Asumiendo que estamos trabajando sobre los release estables (master)
Se debe ejecutar un "git pull origin master" para traernos las actualizaciones del repositorio.

::

 git pull origin master

A continuación se ejecuta el script con el parámetro -u (update). Esta ejecución tomará unos minutos e implica ejecutar todas las actualizaciones
descargadas sobre nuestra instancia de OMniLeads.

::

 ./deploy.sh -u -a

Si todo fluye correctamente, al finalizar la ejecución de la tarea veremos una pantalla como muestra la figura 13.

.. image:: images/maintance_updates_ok.png

*Figure 14: updates OK*


**Instalación desde workstation Linux remoto**

Se debe acceder al repositorio clonado en nuestra maquina workstation, para desde allí correr la actualización sobre el host Linux OMniLeads.

::

 cd PATH_repo_OML
 git pull origin master
 cd ominicontacto/deploy/ansible

A continuación y como en cada ejecución del script "deploy.sh", se debe repasar el archivo de inventory, velando por la coincidencia del
parámetro hostname y dirección IP respecto al host donde corre OMniLeads y vamos a actualizar.

::

 [omnileads-aio]
 hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X #(this line is for node-host installation)


Nota: se debe tener en cuenta que para instalación remota, se debe utilizar la línea con el parámetro "ansible_ssh_port=22" dentro de la
sección [omnileads-aio]

::

	./deploy.sh -u -a


Finalmente, la plataforma queda actualizada a la última versión estable "master"

.. image:: images/maintance_updates_ok.png

*Figure 15: updates from ansible remote OK*

Cambio de dirección IP de la plataforma
***************************************

OMniLeads es un sistema complejo, con varios servicios orientados a las comunicaciones real-time corriendo en el Linux Host.
Esto implica que un cambio de dirección IP del host conlleva cierta complejidad.

Para llevar a cabo esta tarea, debemos ejecutar nuevamente el script “deploy.sh”, el mismo que fue utilizado para llevar a cabo la
instalación de la plataforma.

Debemos ingresar con el usuario root al sistema, cambiar la dirección IP a nivel **sistema operativo** y asegurarnos de que el host tomó la nueva IP.

Luego continuamos con el cambio de IP sobre OML, para ellos debemos pararnos sobre el directorio donde se clonó el repositorio de OML,
para luego acceder al directorio donde se ubica dicho script.

Allí debemos editar nuevamente el archivo *inventory* y repasar el hostname para que coincida con el hostname del host y allí también debemos configurar la nueva dirección IP.

::

 [omnileads-aio]
 hostname ansible_connection=local ansible_user=root ansible_host=X.X.X.X #(this line is for self-hosted installation)

Se guardan los cambios sobre el archivo y finalmente se ejecuta el script *deploy.sh*.

::

 cd ominicontacto/deploy/ansible
 ./deploy.sh --changeip -a

Por último se ejecuta un reinicio de la plataforma. Luego podemos comenzar a utilizar OML en la nueva dirección IP.

::

 reboot
