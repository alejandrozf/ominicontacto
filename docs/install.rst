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
GNU/Linux: `CentOS minimal 7.7 <http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1908.iso>`_. A este tipo de instalación lo llamamos **OMniLeads AIO (All In One)**.


Tipos de instalación AIO
########################

A partir de lo que se configure en el archivo de inventario podemos tener dos tipos de instalación AIO:

.. toctree::
  :maxdepth: 3

  install_self_hosted.rst
  install_remote.rst

.. note::

  **Recomendaciones:**

  * Tanto el host como el nodo a instalar tienen que tener conexión buena y estable a internet
  * Que no haya ningún elemento de red para salir a internet (firewall bloqueando puerto 443, proxy)
  * Usar la ISO de CentOS recomendada
  * En caso de fallo de alguna task de ansible volver a correr el script de instalación
  * En caso de que vuelva a fallar levantar un issue a https://gitlab.com/omnileads/ominicontacto/issues especificando distro en la que sucedió y la versión que se intentó instalar


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