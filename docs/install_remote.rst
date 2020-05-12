.. _about_install_remote:

********************************
Instalación desde ansible remoto
********************************

Este tipo de instalación implica que la descarga del proyecto desde el repositorio y la ejecución del script de instalación se realiza desde
la estación de trabajo del sysadmin, ya que precisamente al estar basada en Ansible la instalación se hace viable éste método.

La ventaja principal de esta opción es que el sysadmin puede instalar y mantener varias instancias de OMniLeads desde un único nodo "deployer".

.. image:: images/install_ansible_remote.png

*Figure 1: remote ansible install*


.. _about_install_remote_deployer:

Preparación del deployer
^^^^^^^^^^^^^^^^^^^^^^^^^

- La máquina deployer puede ser un Linux de las siguientes distros: Centos 7, Ubuntu 18.04 o Debian (9 en adelante)
- Debemos contar con el paquete git para luego clonar el repositorio del proyecto y seleccionar el release a instalar.

.. code-block:: bash

  yum install git (para centos)
  apt-get install git (para debian o ubuntu)
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git checkout master

- Debemos asegurarnos de contar con una clave pública generada en la carpeta /root/.ssh/

.. code-block:: bash

   code content
   sudo ls -l /root/.ssh/

Es probable que ya contemos con una clave pública (id_rsa.pub), como se aprecia en la *figura 1*.

.. image:: images/install_id_rsa.png

*Figure 1: ls -a /root/.ssh command output*

En caso de NO disponer de una, se puede generar rápidamente con el siguiente comando:

::

 sudo ssh-keygen

.. image:: images/install_sshkeygen_remote.png

*Figure 2: ssh-keygen command output*

Este comando genera nuestra clave *id_rsa.pub* que mencionamos anteriormente.

- Se comprueba la *dirección IP* y *hostname* que posee de la máquina donde se instalará OMniLeads, para luego ajustar el archivo de inventario.

::

 hostname
 ip a

.. image:: images/install_hostname_command.png

*Figure 3: hostname command output*

.. image:: images/install_ip_a_command.png

*Figure 4: ip a command output*


- En este paso debemos trabajar sobre el archivo de inventario disponible dentro del directorio "PATH/ominicontacto/deploy/ansible". Remitirse a esta sección: :ref:`about_install_inventory_docker`. No olvidar que estamos instalando **Ansible remoto**.

- Luego en el inventory mismo debemos ajustar las :ref:`about_install_inventory_vars` de la instancia.

Una vez ajustados todos los parámetros del archivo de inventario, procedemos con la ejecución de la instalación.

Ejecución del script de instalación
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La instalación de OMniLeads se realiza mediante el script *deploy.sh*, ubicado dentro de la carpeta deploy/ansible con respecto a la carpeta
raíz del proyecto (ominicontacto).

Una vez configuradas las variables citadas, se procede con la ejecución del script de instalación (uitilizando sudo).

.. code-block:: bash

  sudo ./deploy.sh -i

.. image:: images/install_deploysh_remote.png

*Figure 5: remote root password*

La diferencia respecto de la instalación 'Self-Hosted', es que el script nos pide la contraseña del usuario *root* del host destino de la instalación.

El tiempo de instalación dependerá mayormente de la velocidad de conexión a internet del host sobre ek que se está corriendo el deplot de  OML, ya que se deben descargar, instalar y configurar varios paquetes correspondientes a los diferentes componentes de software que conforman el sistema.

Si la ejecución de la instalación finaliza exitosamente, se despliega una vista como la de la figura 6.

.. image:: images/install_ok.png

*Figure 6: OMniLeads installation ended succesfuly*
