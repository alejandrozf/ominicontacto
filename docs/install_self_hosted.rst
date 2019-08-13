.. _about_install_selfhosted:

***************************
Ansible Self-Hosted Install
***************************

Al mencionar "Ansible Self-Hosted" nos referimos a instalar OMniLeads sobre un sistema operativo (GNU/linux kernel) en un despliegue monolítico
(todos los servicios corriendo sobre dicho host). Se descarga el proyecto (repositorio) sobre el host destino de la instalación, para posteriormente ejecutar el
script de instalación allí en dicho host.

.. image:: images/install_gitlab_repo.png

*Figure 1: self-hosted install*

Pre-requisitos:
^^^^^^^^^^^^^^^

- Una instancia de GNU/Linux CentOS 7 (minimal), Debian 9 (netinstall) ó Ubuntu Server 18.04
- 20 GB de espacio en disco
- 4 GB de memoria RAM

- Es muy importante dejar la hora correctamente configurada en el host.
- Configurar una *dirección IP* y un *hostname* fijo, antes de ejecutar la instalación.

.. note::

   En versiones menores a CentOS 7.6 es necesario primero hacer un yum update y luego reebotear el server

Ajustes necesarios antes  de la ejecución de script:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Debemos contar con el paquete git para luego clonar el repositorio del protyecto y seleccionar el release a instalar

**Ubuntu - Debian:**

.. code-block:: bash

  apt install git
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git checkout master

**CentOS:**

.. code-block:: bash

  yum install git
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git checkout master

- La instalación se trabaja en el directorio "deploy/ansible", disponible desde la raíz del proyecto (PATH/ominicontacto/deploy/ansible):

.. code-block:: bash

 cd deploy/ansible

- Se comprueba la *dirección IP* y *hostname* que posee el host y que luego se utiliza en el archivo de inventario en el proceso de instalación:

.. code-block:: bash

 hostname
 ip a

.. image:: images/install_hostname_command.png

*Figure 2: hostname command output*


.. image:: images/install_ip_a_command.png

*Figure 3: ip a command output*

- En este paso debemos trabajar sobre el archivo  :ref:`about_install_inventory` disponible dentro del directorio "PATH/ominicontacto/deploy/ansible".

.. note::

   OMniLeads utiliza ansible para realizar la instalación, por lo tanto existe un "archivo de inventario" que debe ser modificado de acuerdo a los parámetros
   del host sobre el que estamos trabajando.

Modificar y descomentar la cadena 'hostname' por el que hemos configurado a nuestro servidor. También en esta línea, se debe editar el parámetro 'X.X.X.X' con la
dirección IP que implementa el host sobre el que estamos trabajando.

.. code-block:: bash

 ##########################################################################################
 # If you are installing a prodenv (PE) AIO y bare-metal, change the IP and hostname here #
 ##########################################################################################
 [prodenv-aio]
 oml-name.example.com ansible_connection=local ansible_user=root ansible_host=10.10.10.100 #(this line is for self-hosted installation)
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X #(this line is for node-host installation)

Luego, allí en el inventory mismo debemos ajustar las :ref:`about_install_inventory_vars` de la instanacia.

Una vez ajustados todos los parámetros del archivo de inventario, procedemos con la ejecución de la instalación.

Ejecución del script de instalación:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La instalación de OMniLeads se realiza mediante el script *deploy.sh*, ubicado dentro de la carpeta deploy/ansible con respecto a la carpeta
raíz del proyecto (ominicontacto).

Una vez configuradas las variables citadas, se procede con la ejecución del script de instalación (como usuario root o con privilegios sudo):

.. code-block:: bash

  sudo ./deploy.sh -i

El tiempo de instalación dependerá mayormente de la velocidad de conexión a internet del host OML, ya que se deben descargar, instalar y configurar varios paquetes correspondientes a los diferentes componentes de software que conforman el sistema.

.. image:: images/install_deploysh.png

*Figure 4: install running*

Si la ejecución de la instalación finaliza exitosamente, se despliega una vista como la de la figura 8.

.. image:: images/install_ok.png

*Figure 5: OMniLeads installation ended succesfuly*

.. important::

  **Para Debian:** En caso de que ocurra este error durante la ejecución del script:

  *"ERROR! Unexpected Exception, this is probably a bug: (cryptography 1.7.1 (/usr/lib/python2.7/
  dist-packages), Requirement.parse('cryptography>=2.5'), set(['paramiko']))"*

  Verificar que no exista el paquete python-cryptography, en caso de existir, desinstalarlo. Esto es debido a un bug conocido durante la instalación de Ansible: https://github.com/ansible/ansible/issues/29084


Primer acceso a OMniLeads:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Si la ejecución de la instalación fue exitosa, entonces podemos realizar un :ref:`about_first_access`.


.. important::

 Cada vez que se ejecuta el script *./deploy.sh* ya sea para instalar, correr una actualización del sistema o modificar algún parñametro de red,
 el archivo de "inventory" se vuelve a cero, es decir se pierde toda la parametrización realizada antes de la ejecución del script. No obstante una vez finalizada la
 ejecución de "deplo.sh", se genera una copia del archivo "inventory" (llamada my_inventory), para no perder todos los parámetros del sistema
 utilizados en la última ejecución del script. La copia en cuestión se ubica en el path donde ha sido clonado el repositorio de OML y bajo el nombre de "my_inventory"
 como lo expone la figura.

.. image:: images/install_my_inventory.png

*Figure 6: inventory copy, my_inventory file*


Errores comunes:
^^^^^^^^^^^^^^^^

- El server no tiene internet o no resuelve dominios (configuración de DNS). **Compruebe el acceso a internet del host (por ej: actualizando paquetes - apt-get update | yum update).**

- Timeout de algún paquete que se intenta bajar. Puede volver a intentar ejecutar el deploy y si vuelve a fallar, la opción puede serinstalar el paquete desde la terminal.

- Falla por mala sintaxis o falta de definición de *hostname* y *dirección IP* en el archivo *inventory*.

- No ejecutó el script de deploy con *sudo*, en el host deployer.

- En caso de contar con algún host Ubuntu-Debian, recordar que se deben instalar paquetes como *sudo, openssh-server o python-minimal* antes de correr el script de *deploy.sh*
