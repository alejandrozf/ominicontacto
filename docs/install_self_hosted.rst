.. _about_install_selfhosted:

***************************
Ansible Self-Hosted Install
***************************

Al mencionar "Ansible Self-Hosted" nos referimos a instalar OMniLeads sobre un sistema operativo (GNU/linux kernel) en un despliegue monolítico
(todos los servicios corriendo sobre dicho host). Se descarga el proyecto (repositorio) sobre el host destino de la instalación, para posteriormente ejecutar el
script de instalación allí en dicho host.

.. image:: images/install_gitlab_repo.png

*Figure 1: self-hosted install*

Ajustes necesarios antes  de la ejecución de script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Instalar git para luego clonar el repositorio del proyecto y seleccionar el release a instalar

.. code-block:: bash

  yum install git
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git checkout master

- La instalación se trabaja en el directorio "deploy/ansible", disponible desde la raíz del proyecto (PATH/ominicontacto/deploy/ansible):

.. code-block:: bash

 cd deploy/ansible

- En este paso debemos trabajar sobre el archivo de inventario disponible dentro del directorio "PATH/ominicontacto/deploy/ansible". Remitirse a esta sección: :ref:`about_install_inventory_aio`. No olvidar que estamos instalando **Self Hosted**

- Luego, allí en el inventory mismo debemos ajustar las :ref:`about_install_inventory_vars` de la instanacia.

Una vez ajustados todos los parámetros del archivo de inventario, procedemos con la ejecución de la instalación.

Ejecución del script de instalación
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

La instalación de OMniLeads se realiza mediante el script *deploy.sh*, ubicado dentro de la carpeta deploy/ansible con respecto a la carpeta
raíz del proyecto (ominicontacto).

Una vez configuradas las variables citadas, se procede con la ejecución del script de instalación (como usuario root o con privilegios sudo):

.. code-block:: bash

  sudo ./deploy.sh -i --iface=<your_iface>

Donde **<your_iface>** es la interfaz con la IP que se quiere usar para levantar los servicios que componen OMniLeads (suele ser la IP de la interfaz LAN del servidor).

El tiempo de instalación dependerá mayormente de la velocidad de conexión a internet del host OML, ya que se deben descargar, instalar y configurar varios paquetes correspondientes a los diferentes componentes de software que conforman el sistema. Aproximadamente, este tiempo es de 20 a 30 minutos.

.. image:: images/install_deploysh.png

*Figure 4: install running*

Si la ejecución de la instalación finaliza exitosamente, se despliega una vista como la de la figura 8.

.. image:: images/install_ok.png

*Figure 5: OMniLeads installation ended succesfuly*
