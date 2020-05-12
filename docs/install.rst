.. _about_install:

******************************
Instalación de OMniLeads
******************************

La instalación de OMniLeads requiere la configuración completa de un servidor Linux. No queremos depender del viejo formato de ISO para distribuir el software, ya que tenemos como filosofía el despliegue continuo de releases. Por ende, usamos como base esta herramienta de automatización de tareas: `Ansible <https://docs.ansible.com/ansible/latest/index.html>`_.
El código de Ansible ya está versionado, solo hay que tener en cuenta un archivo muy importante, y este es el `Archivo de Inventario <https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html>`_.

.. note::

  No es necesario preocuparse por la instalación de Ansible, el script de instalación que se va a usar ya lo instala.

A continuación presentamos el archivo de inventario construido para OMniLeads:

.. toctree::
  :maxdepth: 3

  install_inventory_file.rst

Con la configuración ya establecida en este archivo, tenemos variedad a la hora de definir que tipo de instalación queremos. Para OMniLeads tenemos dos grandes tipos:

Instalación AIO
*****************

OMniLeads puede correr como una aplicación tradicional desplegando una instalación de todos los componentes sobre un server físico, máquina virtual o VPS. Siempre y cuando se utilice como base
GNU/Linux. A este tipo de instalación lo llamamos **OMniLeads AIO (All In One)**.


* Si se va a instalar en un server físico o máquina virtual utilizar esta versión de CentOS `CentOS minimal 7.7 <http://centos.zero.com.ar/centos/7.8.2003/isos/x86_64/CentOS-7-x86_64-Minimal-2003.iso>`_.

* Si se va a instalar en un VPS o cloud provider (DigitalOcean, Vultr, OVH, etc) escoger un CentOS lo más parecido posible al minimal y tener en cuenta lo siguiente:

  1. Solamente se puede realizar el tipo de instalación :ref:`about_install_selfhosted` para deployar OMniLeads en un servidor Cloud.
  2. En el archivo de inventario revisar las :ref:`about_install_inventory_oml_cloud`.
  3. Se recomienda utilizar certificados digitales confiables.

.. note::

  Desde el equipo de Freetech Solutions hemos probado la instalación en la distro `Amazon Linux 2 <https://aws.amazon.com/es/amazon-linux-2/>`_. Se **recomienda** utilizar esta distro si va a hostear su OMniLeads en Amazon Web Services.

**Añadir par key/cert confiables**

OMniLeads utiliza por defecto un par de key/cert digital autofirmado, lo que hace que siempre salten excepciones en el browser con los conocidos errores **ERR_CERT_AUTORITHY INVALID** (para Google Chrome) y **SEC_ERROR_UNKNOWN_ISSUER** (para Firefox). Si ud posee su propio par key/cert certificados firmados por una CA válida puede añadirlos a su instalación de OMniLeads siguiendo estos pasos:

  1. Ubique sus par de archivos en la carpeta *deploy/certs/* dentro del repositorio
  2. Los archivos tienen que estar en formato *.pem*
  3. Proceda con la instalación

.. important::

  Dejar sus certificados en la carpeta *deploy/certs/*, para que al actualizar el software se mantenga el uso de estos certificados.

Prerequisitos maquina a instalar
#################################

Ya sea que se vaya a instalar en un VPS, server físico o maquina virtual, tener en cuenta lo siguiente:

- Una instancia de GNU/Linux CentOS 7 (minimal)
- 4 GB de memoria RAM
- Dejar la hora correctamente configurada.
- Configurar una *dirección IP* y un *hostname* fijo.
- Revisar si tiene instalado *firewalld*, si está instalado stopear el servicio y deshabilitarlo:

.. code-block:: bash

  systemctl status firewalld
  systemctl stop firewalld
  systemctl disable firewalld

- Revisar si se tiene selinux activado, para ello ver si existe el archivo `/etc/sysconfig/selinux`. En caso de que si, deshabilitarlo:

.. code-block:: bash

  sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
  sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config

- Realizar un update de la máquina y rebootear

.. code-block:: bash

  yum update -y
  reboot

  .. important::

    Luego del reboot es importante revisar que el paquete kernel-devel coincida con el kernel que se muestre con el comando *uname -a*

Con esto, la máquina queda lista para proceder con el tipo de instalación que se quiera realizar.

Tipos de instalación AIO
########################

A partir de lo que se configure en el archivo de inventario podemos tener dos tipos de instalación AIO:

.. toctree::
  :maxdepth: 3

  install_self_hosted.rst
  install_remote.rst

.. note::

  **Recomendaciones:**

  * Tanto el deployer(host-node) como la máquina a instalar deben tener conexión buena y estable a internet
  * Que no haya ningún elemento de red para salir a internet (firewall bloqueando puerto 443, proxy)
  * En caso de fallo de alguna task de ansible volver a correr el script de instalación
  * En caso de que vuelva a fallar levantar un issue a https://gitlab.com/omnileads/ominicontacto/issues especificando distro en la que sucedió y la versión que se intentó instalar

.. _about_install_cloud:


Instalación en contenedores
****************************

OMniLeads puede ser desplegado utilizando contenedores `Docker <https://www.docker.com>`_, esto extiende la posibilidad de ejecución de la aplicación sobre diversas
distrubuciones de GNU/Linux. Se resalta el hecho de que mediante este formato es posible desplegar OMniLeads sobre instancias de Issabel-PBX & FreePBX, de manera tal que dentro del mismo
host conviva el software de PBX y OMniLeads como software de Contact Center.

En esta sección puede ver los pasos para lograr esta instalación:

.. toctree::
  :maxdepth: 3

  install_docker_linux.rst

El siguiente apartado esta dirigido a usuarios avanzados de Docker, los cuales quieran involucrarse mas con la creacion de imagenes para el proyecto:

.. toctree::
  :maxdepth: 3

  install_docker_build.rst

Primer acceso al sistema
*************************

Una vez instalado el software, remitirse a esta sección para el primer acceso:

.. toctree::
  :maxdepth: 3

  install_first_access.rst

FAQ y errores comunes
**********************

.. toctree::
  :maxdepth: 3

  install_faq.rst
