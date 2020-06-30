.. _about_install_prerequisitos:

Pre-requisitos
**************

Se asume que contamos con una instancia de CentOS-7 o Amazon Linux, sobre la cual se ejecutará la instalación. Pero antes de ésto debemos realizar
una serie de pasos necesarios, por lo tanto a través de una conexión SSH al host se procede con:

Configuración del hostname
**************************

Antes de avanzar con la instalación no olvidar configurar el hostname del host. OMniLeads utiliza dicho valor como parámetro a la hora de
configurar algunos servicios relacionados a la parte SIP (Telefonía).


Deshabilitar firewalld y SElinux:
*********************************

.. code-block:: bash

  systemctl disable firewalld
  sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
  sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config

Instalación de actualizaciones, kernel-devel
********************************************
.. code-block:: bash

  yum update -y && yum install kernel-devel git -y
  reboot

.. important::

  Revisar que el paquete kernel-devel coincida con el kernel.


Ejecutar los comandos:

.. code-block:: bash

  uname -r
  rpm -qa |grep kernel-devel

.. image:: images/install_kernel_devel.png

Proporcionar Certificados SSL confiables
****************************************

OMniLeads se despliega con certificados SSLv3 para la comunicación segura entre el servicio web Nginx y el servicio de SIP Proxy Kamailio (https y websocket), utilizando un certificado
auto-firmado creado por el propio deploy y cuyo Common-Name es el FQDN (o nombre DNS) del host. El certificado emitido utiliza SHA-512 con encriptación RSA como algoritmo de firma y
un tamaño de clave 4096 bits. Al ser un certificado auto-firmado, produce en el browser un **Warning de Sitio No Seguro** al momento de accesar al sistema por primera vez
(ya que la autoridad certificadora o CA no está dentro del repositorio de CAs Confiables del Browser). Una vez agregada la excepción para confiar en él de manera segura, dicho certificado
ya queda configurado para su aceptación.

Sin embargo, se recomienda cargar sus certificados SSL de confianza durante la instalación de la App. Usted deberá ubicar sus archivos **cert** y **key** en formato **.pem** dentro de
la carpeta **ominicontacto/deploy/certs**. Durante el proceso de deploy se detectan los archivos en dicha ubicación y por lo tanto se proporcionan a nivel web y webtrc, de manera
tal que al finalizar el deploy la plataforma quede disponible y utilizando sus propios certificados de confianza.



Ejecución del deploy
********************

Una vez disponible el host, se procede con la instalación. Aquí es donde debemos elegir el tipo
de instalación y arquitectura de OMniLeads a desplegar.

.. toctree::
  :maxdepth: 3

  install_self_hosted.rst
  install_remote.rst
