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

Configuración acerca del tipo de instalación
**********************************************

En la primera parte del archivo se especifica el tipo de despliegue a realizar, en donde tenemos para elegir:


* **Entorno de producción AIO (All In One).**

Como podemos observar esta sección involucra dos lineas que vienen comentadas, las cuales están atañadas al formato de instalación de un entorno productivo AIO.
Ambas son mutuamente excluyentes, la primera hace referencia a una instalación :ref:`about_install_selfhosted` y la segunda se utiliza cuando se desea ejecutar una :ref:`about_install_remote`.

.. code-block:: bash

 ##########################################################################################
 # If you are installing a prodenv (PE) AIO y bare-metal, change the IP and hostname here #
 ##########################################################################################
 [prodenv-aio]
 #localhost ansible_connection=local ansible_user=root #(this line is for self-hosted installation)
 #X.X.X.X ansible_ssh_port=22 ansible_user=root #(this line is for node-host installation)


* **Entorno de desarrollo basado en Docker.**

En caso de requerir el despliegue de un entorno de desarrollo, se debe hacer foco en dicha sección. Aquí simplemente se debe desomentar la linea
"#localhost ansible_connection=local".


.. code-block:: bash

 ##############################################################################
 # Docker host is localhost because the application is deployed in localhost. #
 # Uncomment the line if you want to deploy DE or PE                          #
 ##############################################################################
 # If you are installing a devenv (PE) uncomment
 [prodenv-container]
 #localhost ansible_connection=local
 # If you are installing a devenv (DE) uncomment
 [devenv-container]
 #localhost ansible_connection=local



* **Entorno de producción clusterizando componentes (cluster horizontal).**

Bajo este escenario se deben establecer los parámetros inherentes a cada host que conforma el cluster OMniLeads. Como podemos observar la aplicación puede ser desplegada
dividiendo la carga en hasta cinco componentes. Cada linea corresponde a uno de éstos y deben ser configurados indicando su:

* **hostname**
* **ssh port**
* **ssh user**
* **dirección IP**


.. code-block:: bash

 ################################################################
 # If you  are installing a cluster in bare-metal.              #
 # Uncomment this lines and change IP and hostnames of servers  #
 ################################################################
 [omniapp]
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X
 [kamailio]
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X
 [asterisk]
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X
 [database]
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X
 [dialer]
 #hostname ansible_ssh_port=22 ansible_user=root ansible_host=X.X.X.X


.. _about_install_inventory_vars:

Parámetros y contraseñas
***************************

En la tercera sección del archivo se ajusta todo lo respectivo a contraseñas de algunos componentes:

* **Postgres SQL**
* **MySQL**
* **Usuario "admin" de OMniLeads**

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
  postgres_user=omnileads
  #postgres_password=my_very_strong_pass
  #####################################################################
  #                           Web Admin                               #
  #                     SET WEB ADMIN PASSWORD                        #
  #####################################################################
  #admin_pass=my_very_strong_pass
  #######################################
  # AMI for wombat dialer and OMniLeads #
  #######################################
  ami_user=omnileadsami
  ami_password=5_MeO_DMT
  #####################################################
  # Wombat dialer credentials and MYSQL root password #
  #####################################################
  dialer_user=demoadmin
  dialer_password=demo
  #mysql_root_password=my_very_strong_pass
  ################################################################################################
  # Set the timezone where the nodes are UNCOMMENT and set this if you are doing a fresh install #
  ################################################################################################
  #TZ=America/Argentina/Cordoba

Parámetros de zona horaria y configuración de NAT:

Donde **"TZ"** corresponde al Time Zone correspondiente y por otro lado tenemos los parámetros **"external_port"** y **"external_hostname"**, que hacen alusión a la posibilidad de
que OMniLeads se encuentre detrás de un firewall, en este caso se debe indicar sobre que puerto externo (puerto del firewall) se accede a la aplicación, al igual
con el hostname con el que se invoca a la aplicación desde el exterior.

.. code-block:: bash

  ################################################################################################
  # Set the timezone where the nodes are UNCOMMENT and set this if you are doing a fresh install #
  ################################################################################################
  #TZ=America/Argentina/Cordoba
  #################################################################################
  # OMniLeads behind nat:                                                         #
  #  External port is the outside port where OML web server will listen requests  #
  #  External hostname is the dns external users will connect to                  #
  #################################################################################
  #external_port=
  #external_hostname=
