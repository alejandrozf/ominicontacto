.. _about_install_docker_linux:

*******************************************
Instalación de OMniLeads utilizando Docker
*******************************************

A partir de la versión 1.4.0, OMniLeads puede ser desplegado en producción utilizando Docker. En esta sección se cubren todos los aspectos necesarios
para correr la aplicación utilizando esta novedosa tecnología de "virtualización" sobre CentOS-7, FreePBX o Issabel como sistema operativo subyacente.

.. note::

  Antes de avanzar aclaramos que todo lo expuesto a continuación, tiene garantías en `Issabel-20200102 <https://razaoinfo.dl.sourceforge.net/project/issabelpbx/Issabel%204/issabel4-USB-DVD-x86_64-20200102.iso>`_. Para
  `FreePBX-15 <https://downloads.freepbxdistro.org/ISO/SNG7-FPBX-64bit-1910-2.iso>`_ existe un workaround que se detalla al final de esta sección.


Al ejecutar el proceso de instalación disponible en el repositorio, se procede con la instalación de:

  * Docker
  * docker-compose
  * PostgreSQL
  * MySQL
  * RTPEngine

Estos componentes serán instalados y se van a ejecutar directamente sobre el sistema operativo de base.
Por otro lado los componentes restantes de la aplicación, serán ejecutadoss como contenedores Docker.
En la siguiente figura se presenta un esquema representativo acerca del cómo se despliega OMniLeads.

  .. image:: images/install_docker_centos.png
        :align: center

Como se puede observar los componentes: Asterisk, Kamailio, Nginx, Wombat Dialer, Redis y OMni-App se ejecutan en contenedores, mientras que RTPengine, PostgreSQL y MySQL sobre el sistema operativo base.
A nivel de red, estos componentes se despliegan en una red LAN la cual es creada por docker, creando interfaces virtuales por cada componente.
Este tipo de configuración de red es llamado `Bridge network <https://docs.docker.com/network/bridge/>`_. La LAN por defecto para los containers es 192.168.15.0/24.

Procedimiento de instalación
****************************

Como primer paso se procede con el ingreso al host Linux para luego descargar el repositorio de OMniLeads y una vez clonado el repositorio
debemos posicionarnos sobre el path *relativo*; ominicontacto/deploy/docker/prodenv.

  .. code-block:: bash

    yum -y install git kernel-devel kernel-headers
    yum update -y
    reboot

Una vez terminado el reboot se procede a usar Ansible para la instalación, pudiendo hacerlo de los dos modos: :ref:`about_install_selfhosted` o :ref:`about_install_remote`.
Hay que tener en cuenta estas cosas:

1. Revisar la sección :ref:`about_install_inventory_docker` del archivo de inventario
2. Revisar la sección :ref:`about_install_inventory_docker_vars` para ver las variables de docker a modificar.
3. Modificar las variables del archivo de inventario :ref:`about_install_inventory_vars`.

.. note::

   * La variable *subnet=192.168.15.0/24*, debe modificarse OBLIGATORIAMENTE en caso de que su dirección IP LAN del Linux host (donde se ejecuta el docker-engine) coincida con este rango aquí citadas.
   * Para una instalación en FreePBX o Issabel la variable *mysql_root_password* no es necesario ingresarla, para Issabel va a tomar el valor que encuentre en /etc/issabel.conf y para FreePBX tomará un valor vacio, ya que FreePBX por default no setea contraseña de mysql.

4. Ejecutar el script deploy.sh de la siguiente forma:

**Para ansible remoto:**

.. code-block:: bash

  ./deploy.sh --docker-deploy

**Para ansible self-hosted:**

.. code-block:: bash

  ./deploy.sh --docker-deploy --iface=<your_iface>

Donde **<your_iface>** es la interfaz con la IP que se quiere usar para levantar los servicios que componen OMniLeads (suele ser la IP de la interfaz LAN del servidor).


Systemd - omnileads-prodenv
****************************

A partir de la instalación se deja disponible el servicio: omnileads-prodenv.service el cual servirá para parar/levantar la aplicación. El sistema se deja configurado para que
inicie automáticamente luego de cada reinicio del sistema operativo de base.

Para verificar el servicio:

.. code-block:: bash

  systemctl status omnileads-prodenv

Si todo es correcto deberíamos obtener la siguiente salida:

.. image:: images/install_docker_systemctl_status.png
      :align: center

Para bajar el servicio:

 .. code-block:: bash

   systemctl stop omnileads-prodenv

Para levantar el servicio:

 .. code-block:: bash

   systemctl start omnileads-prodenv

Workaround para freePBX
***********************

Luego de cada *reboot* del sistema operativo se deberán ejecutar los siguientes comandos para dejar apta la instancia para comenzar a trabajar.

.. code-block:: bash

  systemctl restart docker
  systemctl restart omnileads-prodenv

Estos dos comandos dejaran lista la instancia de OMniLeads sobre FreePBX.


.. Note::

    En próximas versiones se tratará de optimizar la ejecución sobre FreePBX.
