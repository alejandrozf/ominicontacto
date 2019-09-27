************************
INTRODUCCION A OMNILEADS
************************


`OMniLeads <https://www.omnileads.net/>`_ es un Software `GPLV3  <https://www.gnu.org/licenses/gpl-3.0.en.html/>`_ para Contact Centers basado en `WebRTC <https://www.webrtc.org/>`_ ,
que permite implementar y gestionar un Contact Center administrando operaciones entrantes y salientes, con acceso a métricas, reportes e indicadores, supervisión real-time de agentes y demás funcionalidades avanzadas de QA y gestión de contactos y campañas.

A partir de ejecutar una sencilla :ref:`about_install`, y unos pocos pasos de Configuración posteriores, tenemos funcional una instancia
de OMniLeads con operaciones de Contact Center en términos de campañas entrantes y salientes. Nuestro software puede adaptarse a una compañia u organización que necesita
mantener su propio Contact Center con integración a su central PBX, así como también asumir la función de "núcleo" de comunicaciones para
una compañía que brinda servicios de Customer Contact (Business Outsourcing Process - BPO).

Dentro de un universo 100% web, los diferentes perfiles de usuarios; agentes, supervisores, administradores, clientes, acceden a OMniLeads desde
cualquier navegador moderno con soporte `WebRTC <https://www.webrtc.org/>`_. Al no requerir del uso de aplicaciones de escritorio Softphones, este
software simplifica a nada la configuración a realizar en las estaciones de trabajo de los agentes, tan solo acceder a una dirección HTTPS para estar
online gestionando comunicaciones con los clientes. OMniLeads es una gran opción para implementar CCaaS "Contact Center as a Service" !


.. image:: images/what_is.png
        :align: center


Cómo lo obtengo ?
*****************
`Nuestro repositorio  <https://gitlab.com/omnileads/ominicontacto>`_ se encuentra disponible en GitLab, para libre descarga, instalación y uso del Software.


Donde se puede instalar ?
*************************
OMniLeads ha sido testeado en su totalidad en las siguientes distribuciones de GNU/Linux:

* `CentOS 7.7.1908 minimal ISO <http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1908.iso>`_
* `Debian 9.3 netinstall ISO <https://cdimage.debian.org/mirror/cdimage/archive/9.3.0/amd64/iso-cd/debian-9.3.0-amd64-netinst.iso>`_
* `Ubuntu Server 18.04.2 LTS ISO <https://ubuntu.com/download/server/thank-you?version=18.04.2&architecture=amd64>`_

.. important::

  Remitirse a estas versiones de las distribuciones y sus correspondientes ISO para lograr una instalación exitosa

Por otra parte, si eres usuario de `Docker <https://www.docker.com>`_, puedes ejecutar el sistema a partir de nuestras imágenes oficiales disponibles en el
`Docker-Hub <https://hub.docker.com/u/freetechsolutions>`_ y el correspondiente `docker-compose  <https://docs.docker.com/compose>`_ que viene en el repositorio.

Cómo lo instalo ?
*****************
La instalación de omnileads está basada en el uso de un script de bash que setea un entorno para la ejecución de  `Ansible <https://www.ansible.com/>`_. Dentro del código del proyecto,
se dispone de dicho script que permite instalar el sistema sobre cualquiera de los Sistemas Operativos previamente citados. En la sección :ref:`about_install` de esta
documentación, se detalla dicho proceso.


Características y funcionalidades de OMniLeads
**********************************************

* :ref:`about_webrtc`.
* :ref:`about_omlfeatures`.

Dónde y cómo lo puedo usar ?
****************************

* :ref:`about_usecase_pbx`.
* :ref:`about_usecase_bpo`.
* :ref:`about_usecase_cloud`.


Cómo me capacito ?
******************

Esta documentación cubre todos los aspectos del producto. Desde cuestiones técnicas inherentes al administrador IT hasta aspectos funcionales orientados a los supervisores
o líderes del contact center.

Además ponemos a disposición un **Curso online gratuito**, en el cual se exponen videos que ejemplifican los tópicos planteados en esta documentación. Es un material complementario
y a su vez basado en todos los temas aquí postulados.

Para registrarse **sin cargo** acceder a `ESTE LINK <http://www.techxpert.guru/omnileads-takeoff/>`_

***********
INSTALACIÓN
***********

En este capítulo se cubren todos los tipos de instalación del software.

.. toctree::
  :maxdepth: 2

  install.rst


*****************
SETTING INICIALES
*****************
En esta sección se plantean las configuraciones escenciales a realizar una vez que dejamos instalada una instancia de OMniLeads.

.. toctree::
  :maxdepth: 2

  initial_settings.rst


*********************************
CONFIGURACIÓN DE ACCESO A LA PSTN
*********************************
OMniLeads facilita mediante configuración web, la posibilidad de mantener troncales SIP de acceso a la PSTN. Éstos troncales
son invocados por reglas de enrutamiento de llamadas salientes, en las cuales se puede especificar qué tipo de llamadas son procesadas
por cada troncal SIP. Además los troncales pueden ser configurados en modo *failover*

Para profundizar al respecto se recomienda leer el resto del capítulo.

  .. toctree::
   :maxdepth: 2

   telephony.rst


********
CAMPAÑAS
********
Toda comunicación entre "el exterior" y un agente de OMniLeads es encapsulado dentro de una campaña. En este capítulo se aborda todo lo inherente a la gestión
de campañas Entrantes y Salientes (manuales, preview y dialer)

  .. toctree::
   :maxdepth: 2

   campaigns.rst


*********************************************
METRICAS, REPORTES, GRABACIONES Y SUPERVISION
*********************************************
Dentro de este capítulo se aborda todo lo inherente a la extracción de informarción que arroja el sistema respecto a estadísticas,
métricas, reportes, grabaciones, supervisión en tiempo real, etc.

  .. toctree::
   :maxdepth: 2

   output.rst


****************
MANUAL DE AGENTE
****************
En esta sección se repasan todas las acciones que un agente de OMniLeads pueda realizar dentro de una operación. Cuestiones que van desde la atención/generación de
una llamada, calificaciones, agendamiento, macación de grabaciones, transferencias de llamadas y mucho más, son tratadas en este capítulo de la documentación.

  .. toctree::
   :maxdepth: 2

   agent.rst


*******************************
GESTIONES DEL ADMINISTRADOR IT
*******************************
En esta sección se cubren algunas tareas inherentes al administrador técnico de OMniLeads. Cuestiones como la configuración de bajo nivel
del módulo de discador predictivo, gestión de actualizaciones, backup & restore y cambio de dirección IP de la plataforma.

  .. toctree::
   :maxdepth: 2

   maintance.rst

*********************
INTEGRACION CON CRM
*********************

OMniLeads permite integrarse con sistemas Web CRM, de manera tal que se puede configurar para enviar notificaciones y peticiones desde OMniLeads
hacia el sistema CRM y viceversa a traves de la API del sistema.

.. toctree::
 :maxdepth: 2

 crm_integration.rst


********
OML API
********
En esta sección vamos a encontrar toda la especificación de la API Rest del sistema.

  .. toctree::
   :maxdepth: 2

   api.rst

************
KNOWN ISSUES
************

.. toctree::
 :maxdepth: 2

 known_issues.rst


*************
RELEASE NOTES
*************

.. toctree::
 :maxdepth: 2

 release_notes.rst
