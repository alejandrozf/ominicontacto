************************
INTRODUCCION A OMNILEADS
************************

OMniLeads es una solución de software para Contact Centers, basada en *Software Libre - GPL V3*.

A partir de una sencilla instalación, OMniLeads le permite montar toda una operación de
Contact Center tanto Inbound como Outbound, ya sea dentro del marco de una compañia u organización que necesita su propio Contact Center integrado al PBX operativo dentro de su sistema de telefonía, así como
también cumpliendo el rol sistema "núcleo" de comunicaciones en una compañía que brinda servicios de Customer Contact (Business Outsourcing Process - BPO).

Dentro de un universo 100% Web, los agentes disponen de una interfaz basada en `WebRTC <https://www.webrtc.org/>`_ para la gestión de comunicaciones mientras que los supervisores
aprovechan las bondades de la tecnología WebRTC para realizar acciones de channel spy, coaching de agentes, gestión de QA o three way conferences, sin la necesidad de instalar ninguna aplicación "softphone".
La interfaz para administradores permite gestionar usuarios, campañas, bases de datos, a su vez extraer métricas y estadísticas, gestionar las grabaciones
de las comunicaciones entre tantas otras funcionalidades.

OMniLeads cuenta una interfaz de configuración de parámetros de telefonía, que permite adminsitrar múltiples troncales SIP y su enrutamiento de llamadas salientes de acuerdo
a reglas/patrones de marcado así como también el enrutamiento de llamadas entrantes con la posibilidad de utilizar IVRs y/o Condicionales de tiempo a la hora de encaminar una numeración *DID* hacia una campaña entrante.

Por si quedan dudas: **OMniLeads NO es un módulo de "call center" que añade reportería y  supervisión a un sistema PBX.
OMniLeads fue concebido como una plataforma Standalone orientada y optimizada para el manejo de campañas telefónicas en el marco del Contact Center**


.. image:: images/what_is.png
        :align: center


Cómo lo obtengo ?
*****************
`Nuestro repositorio  <https://gitlab.com/omnileads/ominicontacto>`_ se encuentra disponible en GitLab, para libre descarga, instalación y uso del Software.


Donde se puede instalar ?
*************************
OMniLeads puede correr sobre las distribuciones de GNU/Linux; CentOS7, Debian-9 y Ubuntu Server 18.04.


Cómo lo instalo ?
*****************
Dentro del código del proyecto, se dispone de un script de instalación basado en `Ansible <https://www.ansible.com/>`_ que permite instalar el producto sobre cualquier SO de los
mencionados anteriormente. En la sección Instalación de ésta pagin se detalla el proceso, en sus diferentes tipos de instalación.


Características y funcionalidades de OMniLeads
**********************************************
.. toctree::
  :maxdepth: 2

  what_is_extra.rst

Dónde y cómo lo puedo usar ?
****************************
.. toctree::
  :maxdepth: 2

  what_is_use_cases.rst

Cómo me capacito ?
******************

Esta documentación cubre todos los aspectos del producto. Desde cuestiones técnicas inherentes al administrador IT hasta aspectos funcionales orientados a los supervisores
o líderes del contact center.

Además ponemos a disposición un **Curso online gratuito**, en el cual se exponen videos que ejemplifican los tópicos planteados en esta documentación. Es un material complementario
y a su vez basado en todos los temas aquí postulados.

Para registrarse **sin cargo** acceder a `este enlace <http://www.techxpert.guru/omnileads-takeoff/>`_

***********
INSTALACIÓN
***********

Existen tres formas en la que OMniLeads puede ser instalado. En el presente capítulo se detalla cada uno de los procesos.

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
Todo procesamiento de comunicaciones entre "el exterior" y un agente de OMniLeads es encapsulado dentro de una campaña. En este capítulo se aborda todo lo inherente a la gestión
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
