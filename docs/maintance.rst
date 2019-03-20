*********************
OMniLeads Maintenance
*********************

Configuración del módulo de *Discador predictivo*
*************************************************
Antes que nada se notifica que si la instancia de OML desplegada en los pasos anteriores, NO contemplan el uso de campañas con discado saliente predictivo, este paso puede ser omitido.

El core-dialer de OML es un una herramienta basada en licencias e incorporada de manera opcional. Este dialer se llama Wombat Dialer (propiedad de Loway - loway.com) y como se mencionó, es el componente encargado de discar registros de manera progresiva/predictiva.

Si se desean correr campañas predictivas, se debe generar la siguiente configuración básica de Wombat Dialer . Esto se consigue ingresando a la dirección IP del host OML.

http://omnileads.yourdomain:8080/wombat

Al ingresar se despliega una pantalla como la siguiente, donde deberá presionar los botones indicado en la imagen.

Se debe proceder con la creación de la base de datos para Wombat Dialer. Hacer click en botón remarcado en la figura 4.



Figura 14: Crear base de datos Wombat Dialer

Luego es el momento de ingresar la clave del usuario root de MySQL y hacer click en botón remarcado en la figura 6. Nota; el password fue configurado dentro del archivo “inventory” antes de activar la instalación del sistema. (En el mismo directorio en el que clonó el repositorio de OML).



Figura 15: copia del archivo “invenory” de la última ejecución del script

Figura 16: passwords del componente Wombat Dialer

Procedemos entonces con la creación de la base de datos MySQL que utilizará de ahora en más el componente de tercero Wombat Dialer.


Figura 17: Crear base de datos Wombat Dialer



Una vez creada la base de datos MySQL que utiliza Wombat Dialer, se procede con el primer login.



Figura 18: Crear base de datos Wombat Dialer

A continuación se debe realizar un login en la interfaz de administración de Wombat Dialer para avanzar con la configuración de parámetros necesarios para la interacción con OML.


Datos disponibles también en el archivo “inventory”, generado en el deploy.

Usuario: demoadmin
Pass: demo



Figura 19: Login en Wombat Dialer


Para ello simplemente se debe seguir paso a paso, la configuración expuesta en las siguientes figuras: 8, 9, 10 y 11.



Figura 20: Configuración de base WD


En este paso debeŕa ingresar la contraseña AMI ingresada en la instalación. El usuario es: omnileadsami y en caso de de haber dejada la contraseña por defecto (5_MeO_DMT) en el archivo inventory.


Figura 21: Configuración de base WD - Asterisk server



En el siguiente punto, se configura una Troncal utilizando un “Nombre de la troncal” arbitrario, pero con la cadena de llamado marcada en la figura. Local/${num}@from-oml/n



Figura 22: Configuración de base WD - Troncal




Finalmente debemos observar que nuestra configuración luzca como la figura 12.


Figura 23: Configuración de base WD - Resultado final

Por último, recuerde dar “play” al servicio de dialer, tal como lo indica la siguiente figura:



Figura 24: Iniciar el Marcador.



Finalmente la plataforma se encuentra habilitada para gestionar llamadas predictivas. La instalación por defecto cuenta con una licencia de Wombat Dialer demo de un canal Recuerde acceder a la página del fabricante y comprar canales de discador dependiendo de sus necesidades (https://www.wombatdialer.com/purchase.jsp).



Back & Restore
**************
OMniLeads dispone de un script para llevar a cabo las tareas de backup/restore.

Para realizar un backup:

Debemos acceder por ssh al host donde tenemos corriendo OMniLeads.
Una vez dentro del host:


su omnileads -
cd /opt/omnileads/bin
./backup-restore.sh -b

La ejecución del script arroja una salida similar a la de la figura 19.



figura 19: procedimiento de backup

Como se puede observar, nos indica cómo realizar el restore de dicho backup.

Dentro del path /opt/omnileads/backup, se generan los archivos “.tgz” que contienen los backups ejecutados.

Si el restore se realiza en nuevo host, entonces se debe dejar disponible el archivo generado en el backup dentro del path /opt/omnileads/backup.

Para llevar a cabo un restore, se debe ejecutar:


./backup-restore.sh -r nombre_del_archivo_de_backup

Por ejemplo: ./backup-restore.sh -r 20190211_database.tgz


figura 20: restore de un backup


Actualizaciones
***************

OML es forjada bajo el paradigma de lanzamientos de releases continuos, lo cual implica un flujo de actualizaciones constantes. Por ello es muy importante llevar a cabo de manera limpia las actualizaciones.

A continuación se exponen los pasos a seguir para llevar a cabo una nueva actualización de la plataforma. Y como ya se puede sospechar, esta tarea también se realiza con el script “deploy.sh”.

Las actualizaciones se anuncian por los canales de comunicaciones, oficiales del proyecto.

Dependiendo el método de instalación que se haya seleccionado:


Instalación Self-Hosted


Acceder como root al host omnileads
Posicionarse sobre el directorio donde reside el script “deploy.sh”
cd ominicontacto/deploy/ansible

Realizar un “git checkout” sobre la rama a actualizar
git checkout release-X.X.X

Donde X.X.X se corresponde con versión de OML (por ej: 1.1.1).

A continuación se ejecuta el script con el parámetro -u (update). Esta ejecución tomará unos minutos e implica llevar a la plataforma OML a la versión previamente seleccionada en el git checkout.
./deploy.sh -u -a

Si todo fluye correctamente, al finalizar la ejecución de la tarea veremos una pantalla como muestra la figura X.


Figura 18: Actualización exitosa


Instalación desde workstation Linux remoto

Se debe acceder al repositorio clonado en nuestra maquina workstation, para desde allí correr la actualización sobre el host Linux OMniLeads.

cd PATH_repo_OML
cd ominicontacto/deploy/ansible

Para seleccionar el release a utilizar para actualizar, utilizamos git checkout
	git checkout release-X.X.X
Donde X.X.X se corresponde con versión de OML (por ej: 1.1.1).

A continuación y como en cada ejecución del script “deploy.sh”, se debe repasar el archivo de inventory, velando por la coincidencia del parámetro hostname y dirección IP respecto al host donde corre OML.

[omnileads-aio]
hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X #(this line is for node-host installation)

Nota: tener en cuenta que para instalación remota, se debe utilizar la línea con el parámetro “ansible_ssh_port=22” dentro del contexto [omnileads-aio]

Finalmente, la plataforma queda actualizada a la versión “release-X.X.X”.

	./deploy.sh -u -a


Cambio de dirección IP de la plataforma
***************************************


OMniLeads es un sistema complejo, con varios servicios orientados a las comunicaciones real-time corriendo en el Linux Host. Esto implica que un cambio de dirección IP del host conlleva cierta complejidad.

Para llevar a cabo esta tarea, debemos ejecutar nuevamente el script “deploy.sh”, el mismo que fue utilizado para llevar a cabo la instalación de la plataforma.

Debemos ingresar con el usuario root al sistema, cambiar la dirección IP a nivel sistema operativo y asegurarnos de que el host tomó la nueva IP.

Luego continuamos con el cambio de IP sobre OML, para ellos debemos pararnos sobre el directorio donde se clonó el repositorio de OML, para luego acceder al directorio donde se ubica dicho script.

Allí debemos editar nuevamente el archivo “inventory” y repasar el hostname para que coincida con el hostname del host y allí también debemos configurar la nueva dirección IP.

[omnileads-aio]
hostname ansible_connection=local ansible_user=root ansible_host=X.X.X.X #(this line is for self-hosted installation)

Se guardan los cambios sobre el archivo y finalmente se ejecuta el script deploy.sh.

cd ominicontacto/deploy/ansible
./deploy.sh --changeip -a

Por último se ejecuta un reinicio de la plataforma. Luego podemos comenzar a utilizar OML en la nueva dirección IP.

reboot
