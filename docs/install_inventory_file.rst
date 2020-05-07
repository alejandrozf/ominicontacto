.. _about_install_inventory:

**********************
Archivo de inventario
**********************

Al utilizar Ansible como tecnología para realizar los despliegues de OMniLeads, se trabaja con un archivo de "inventario" en el cual se configuran cuestiones como:

* Tipo de instalación a realizar (self-hosted, en remoto, cluster, entorno de desarrollo, etc.)
* Passwords de los diferentes componentes (postgres, asterisk-AMI, acceso de admin, etc.)
* Zona horaria
* Soporte para NAT

Vamos a dividir el archivo en dos fragmentos:

.. _about_install_inventory_aio:

Configuración entorno AIO
**************************

En la primera parte del archivo se encuentra la seccion **[prodenv-aio]**:

.. code-block:: bash

 ##########################################################################################
 # If you are installing a prodenv (PE) AIO y bare-metal, change the IP and hostname here #
 ##########################################################################################
 [prodenv-aio]
 #localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)
 #X.X.X.X ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)

* **Para Self Hosted:** descomentar la primera línea, para que quede así:

.. code:: bash

   localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)

* **Para Ansible Remoto** descomentar la segunda línea, y reemplazar el X.X.X.X por la IP de la máquina a instalar OMniLeads, ejemplo:

.. code:: bash

  192.168.1.206 ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)

.. _about_install_inventory_docker:

Configuración entorno Docker
*****************************

En la segunda parte, se encuentra la sección **[prodenv-container]** para la instalación de OMniLeads en containers:

.. code-block:: bash

  # If you are installing a devenv (PE) uncomment
  [prodenv-container]
  #localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)
  #X.X.X.X ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation, replace X.X.X.X with the IP of Docker Host)

* **Para Self Hosted:** descomentar la primera línea, para que quede así:

.. code:: bash

   localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)

* **Para Ansible Remoto** descomentar la segunda línea, y reemplazar el X.X.X.X por la IP de la máquina a instalar OMniLeads, ejemplo:

.. code:: bash

  192.168.1.206 ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)

.. important::

  Tener mucho cuidado a la hora de descomentar las líneas, no descomentar las de entorno de container si se quiere instalar AIO, por ejemplo.

.. _about_install_inventory_vars:

Parámetros y contraseñas
***************************

En la tercera sección del archivo se ajusta todo lo respectivo a contraseñas de algunos componentes y parámetro para configuración de zona horaria:

* **Postgres SQL**
* **Constraseña del usuario "admin" de OMniLeads**
* **TZ**
* **Usuario de la DB postgresql**
* **Usuario y contraseña para asterisk AMI**
* **Usuario y contraseña para web de Wombat Dialer**

.. code-block:: bash

  [everyone:vars]

  ###############
  # Credentials #
  ###############

  #####################################################################
  #                           Database                                #
  #                    SET POSTGRESQL PASSWORD                        #
  #####################################################################
  postgres_database=omnileads
  #postgres_user=omnileads
  #postgres_password=my_very_strong_pass
  #####################################################################
  #                           Web Admin                               #
  #                     SET WEB ADMIN PASSWORD                        #
  #####################################################################
  #admin_pass=my_very_strong_pass
  #######################################
  # AMI for wombat dialer and OMniLeads #
  #######################################
  #ami_user=omnileadsami
  #ami_password=5_MeO_DMT
  #############################
  # Wombat dialer credentials #
  #############################
  #dialer_user=demoadmin
  #dialer_password=demo
  #################################################################################################
  # Set the timezone where the nodes are. UNCOMMENT and set this if you are doing a fresh install #
  #################################################################################################
  #TZ=America/Argentina/Cordoba

.. _about_install_inventory_docker_vars:

Variables para Docker
**********************

Ademas de las variables vistas anteriormente, si se quiere instalar OMniLeads en su versión dockerizada, será necesario modificar estas variables:

.. code-block:: bash

  [docker:vars]
  registry_username=freetechsolutions
  #registry_email=
  #registry_password=
  subnet=192.168.15.0/24

Las variables necesarias para **deploy** de los containers son:

* **registry_username:** si se va a deployar las imagenes oficiales de Freetech Solutions, dejar esta variable como está
* **subnet:** se refiere a la red LAN con la que se levantarán los containers.

Las variables *registry_email* y *registry_password* son necesarias en caso de querer hacer un **build** de sus propias imágenes.

.. _about_install_inventory_oml_cloud:

Variables OMniLeads Cloud
**************************

Los parámetros  **"external_hostname"**, **"external_port"**, deben configurarse si se quiere instalar un OMniLeads en un servidor en la nube, donde los agentes se conectarán a la URL conformada por **https://external_hostname:external_port**, sin tener una conexion LAN directa o atraves de VPN hacia el OMniLeads.

.. code-block:: bash

  #######################################################################################
  #                                OMniLeads cloud:			 	      #
  # If you are wishing to install OML in a cloud provider you must set these variables: #
  #  - external_port: the outside port where OML web server will listen requests        #
  #  - external_hostname: the dns external users will connect to                        #
  #  - public_ip: where OML is installed                                                #
  #######################################################################################
  #external_port=
  #external_hostname=

.. important::

  Se deben establecer dos reglas de firewall en la GUI del proveedor del servidor cloud, el cual actua como un router de borde, dejando a OML "detrás de un NAT". (si no sabe como hacerlo pongase en contacto con su proveedor)

    * Permit de tráfico saliente desde los puertos 10000 a 30000 UDP
    * Permit de tráfico entrante desde los puertos 10000 a 30000 UDP

.. _about_install_inventory_oml_trusted_certs:
