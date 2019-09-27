.. _about_install_selfhosted:

***************************
Ansible Self-Hosted Install
***************************

Cuando decimos "Ansible Self-Hosted" nos referimos a instalar OMniLeads sobre un OS de forma monolítica (todos los servicios corriendo en dicho host) y
descargando el proyecto en el OS destino de la instalación, para posteriormente ejecutar el script de instalación desde el propio host.

.. image:: images/install_gitlab_repo.png

*Figure 1: self-hosted install*

Pre-requisitos:
^^^^^^^^^^^^^^^

- Una instancia de GNU/Linux CentOS 7 (minimal), Debian 9 (netinstall) ó Ubuntu Server 18.04
- 20 GB de espacio en disco
- 4 GB de memoria RAM

- Es muy importante dejar la hora correctamente configurada en el host.
- Configurar una *dirección IP* y un *hostname* fijo, antes de ejecutar la instalación.

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

- Instalar paquete kernel-devel, realizar el update del sistema operativo y rebotear la máquina.

  .. code-block:: bash

    yum install kernel-devel -y
    yum update -y
    reboot

.. important::

  Luego del reboot es importante revisar que el paquete kernel-devel coincida con el kernel que se muestre con el comando *uname -a*

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

- En este paso, se debe editar el archivo *inventory* (PATH/ominicontacto/deploy/ansible).

.. note::

   OMniLeads utiliza ansible para realizar la instalación, por lo tanto existe un "archivo de inventario" que debe ser modificado de acuerdo a los parámetros del host sobre el que estamos trabajando.

Modificar y descomentar la cadena 'hostname' por el que hemos configurado a nuestro servidor. También en esta línea, se debe editar el parámetro 'X.X.X.X' con la dirección IP del host sobre el que estamos trabajando.


.. image:: images/install_inventory_file_net.png

*Figure 4: inventory file network params section*

Además dentro del mismo archivo, unas líneas debajo encontraremos la sección *[everyyone:vars]*, en la cual se pueden alterar variables y contraseñas que vienen por defecto en el sistema. Introducir el parámetro "time zone" adecuado para su instanacia. Es **Importante** que realice este paso o la instalación no se va a poder realizar.

.. image:: images/install_inventory_passwords.png

*Figure 5: Passwords and parameters of services*

En caso de haber olvidado ingresar la instancia a instalar el script mostrará este mensaje

.. image:: images/install_inventory_nohosts.png

*Figure 6: deploy - No hosts in inventory*

Es importante aclarar que cada vez que se corre el script *./deploy.sh* ya sea para instalar, re-instalar, actualizar, modificar la dirección IP de OML, etc., el archivo de inventory se vuelve a "cero". No obstante se genera una copia del archivo **(my_inventory)**, de manera tal que se cuente con los parámetros del sistema utilizados en la última ejecución del script. La copia en cuestión se ubica en el path donde ha sido clonado el repositorio de OML y bajo el nombre de "my_inventory" como lo expone la figura 6.

.. image:: images/install_my_inventory.png

*Figure 7: inventory copy, my_inventory file*


Ejecución del script de instalación:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La instalación de OMniLeads se realiza mediante el script *deploy.sh*, ubicado dentro de la carpeta deploy/ansible con respecto a la carpeta
raíz del proyecto (ominicontacto).

Una vez configuradas las variables citadas, se procede con la ejecución del script de instalación (como usuario root o con privilegios sudo):

.. code-block:: bash

  sudo ./deploy.sh -i

El tiempo de instalación dependerá mayormente de la velocidad de conexión a internet del host OML, ya que se deben descargar, instalar y configurar varios paquetes correspondientes a los diferentes componentes de software que conforman el sistema.

.. image:: images/install_deploysh.png

*Figure 8: install running*

Si la ejecución de la instalación finaliza exitosamente, se despliega una vista como la de la figura 8.

.. image:: images/install_ok.png

*Figure 9: OMniLeads installation ended succesfuly*

.. important::

  **Para Debian:** En caso de que ocurra este error durante la ejecución del script:

  *"ERROR! Unexpected Exception, this is probably a bug: (cryptography 1.7.1 (/usr/lib/python2.7/
  dist-packages), Requirement.parse('cryptography>=2.5'), set(['paramiko']))"*

  Verificar que no exista el paquete python-cryptography, en caso de existir, desinstalarlo. Esto es debido a un bug conocido durante la instalación de Ansible: https://github.com/ansible/ansible/issues/29084


Primer acceso a OMniLeads:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Si la ejecución de la instalación fue exitosa, entonces podemos realizar un :ref:`about_first_access`.


Errores comunes:
^^^^^^^^^^^^^^^^

- El server no tiene internet o no resuelve dominios (configuración de DNS). **Compruebe el acceso a internet del host (por ej: actualizando paquetes - apt-get update | yum update).**

- Timeout de algún paquete que se intenta bajar. Puede volver a intentar ejecutar el deploy y si vuelve a fallar, la opción puede serinstalar el paquete desde la terminal.

- Falla por mala sintaxis o falta de definición de *hostname* y *dirección IP* en el archivo *inventory*.

- No ejecutó el script de deploy con *sudo*, en el host deployer.

- En caso de contar con algún host Ubuntu-Debian, recordar que se deben instalar paquetes como *sudo, openssh-server o python-minimal* antes de correr el script de *deploy.sh*
