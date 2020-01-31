.. _about_install_docker_build:

******************************
Creando imágenes de OMniLeads
******************************

OMniLeads cuenta con una imagen para cada servicio que compone el software, dichas imágenes oficiales están disponibles en nuestro `Docker-Hub <https://hub.docker.com/u/freetechsolutions>`_.
Usted podrá crear sus propias imágenes basándose en los Dockerfiles que tenemos predefinidos para cada servicio, debe tener en cuenta lo siguiente:

* Se usa Ansible como herramienta para buildear muchas imagenes al tiempo, por lo que los Dockerfiles son templates de Ansible, ubicados en el `deploy/ansible/roles/docker/files/Dockerfiles`. Esto quiere decir que si quiere hacer algún cambio en los Dockerfiles debe tener conocimiento en Ansible.

***********************
El DevEnv y el ProdEnv
***********************

OMniLeads provee de un entorno de desarrollo (DevEnv) para programadores Django que quieran involucrarse en  el proyecto, nosotros nos encargamos del mantenimiento de estas imágenes y competen los 9 servicios que componen el sistema.
Este entorno es el ideal para desarrollar cambios en el código y tener en tiempo real el cambio, sin necesidad de reiniciar containers.
A su vez, el ProdEnv es el entorno ideal para ambientes productivos, usando imágenes de 5 servicios (todos menos mysql, postgresql y rtpengine). 

Build de imágenes 
******************

Para buildear imágenes seguir los siguientes pasos:

1. Especificar en el archivo de inventario de ansible que entorno se desea. Descomentar la linea que dice #localhost dependiendo del entorno.

  .. code-block:: bash

    # If you are installing a devenv (PE) uncomment
    [prodenv-container]
    #localhost ansible_connection=local
    # If you are installing a devenv (DE) uncomment
    [devenv-container]
    #localhost ansible_connection=local

2. En el mismo archivo observar la seccion [docker:vars], en el verá unas variables sin valor:

  .. code-block:: bash

    [docker:vars]
    registry_username=
    registry_email=
    registry_password=
    oml_release=

Ingresar ahí el nombre de usuario, email y contraseña del *Registry* donde quiere subir sus imágenes.
La variable **oml_release** es usada solo cuando se quiere buildear imagenes para **ProdEnv**. Esta variable va a definir el **Tag** que van a tener las imágenes

3. Por último, ejecutar el script *deploy.sh* de la siguiente forma:

.. code-block:: bash

  ./deploy.sh --docker-build

.. note::

  Durante la ejecución se realiza de una vez el build y push de las imágenes, por lo que si experimenta algun error a la hora del build debido a problemas de conexion a internet, es recomendable volver a correr el script.