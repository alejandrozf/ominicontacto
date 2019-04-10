************************
INTRODUCCION A OMNILEADS
************************

OMniLeads es una solución *Standalone* para Contact Centers basada en *Software Libre GPL V3*, destinada a soportar la gestión, operación
y administración de un Contact Center.

OMniLeads ofrece funcionalidades que permiten desarrollar operaciones de Call Center tanto Inbound como Outbound
(campañas preview, manuales y predictivas). A partir de una instalación sencilla, se puede montar toda una operación de
Contact Center ya sea dentro del marco de una compañia u organización que necesita su propio Contact Center integrado al PBX operativo dentro de su sistema de telefonía, así como
también funcionando como Núcleo de Comunicaciones de una compañía que brinda servicios de Customer Contact (Business Outsourcing Process - BPO).

De gestión y operación 100% Web, los agentes disponen de una interfaz basada en `WebRTC <https://www.webrtc.org/>`_ para la gestión de comunicaciones mientras que los supervisores
utilizan WebRTC para realizar acciones de channel spy, coaching de agentes, gestión de QA o three way conferences. Por otro lado, los administradores
cuentan con una interfaz que permite mantener usuarios, campañas, bases de datos, a su vez extraer métricas y estadísticas, gestionar las grabaciones
de las comunicaciones entre otras funcionalidades.

OMniLeads cuenta con su propio engine e interfaz de configuración de funciones de telefonía, permitiendo adminsitrar múltiples troncales SIP y su enrutamiento de llamadas salientes de acuerdo
a reglas/patrones de marcado así como también enrutamiento de llamadas entrantes con la posibilidad de utilizar IVRs y/o Condicionales de tiempo a la hora de encaminar una numeración *DID* hacia una campaña entrante.

Por si quedan dudas: **OMniLeads NO es un módulo de "call center" que añade reportería y  supervisión a un sistema PBX.
OMniLeads fue concebido desde cero, como una plataforma Standalone orientada y optimizada para el manejo de campañas telefónicas en el marco del Contact Center**


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



***********
INSTALACIÓN
***********

En el siguiente video se expone paso a paso el proceso de instalación más básico (self-hosted script)

.. raw:: html

        <iframe src="https://player.vimeo.com/video/317503659" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


En las próximas páginas del presente capítulo, detallaremos la ejecución de cada tipo de instalación.

Tipos de instalación
********************

Existen tres formas en la que OMniLeads puede ser instalador. En la presente sección se detalla cada proceso.

.. toctree::
   :maxdepth: 2

   install.rst


*****************
SETTING INICIALES
*****************
En esta sección se plantean las configuraciones escenciales a realizar una vez que dejamos instalada una instancia de OMniLeads.

En el vídeo; una típica configuración posterior a la instalación de OMniLeads.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/319574451" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Dentro de la sección se profundiza al respecto.

  .. toctree::
   :maxdepth: 2

   initial_settings.rst



*********************************
CONFIGURACIÓN DE ACCESO A LA PSTN
*********************************
OMniLeads facilita mediante configuración web, la posibilidad de mantener troncales SIP de acceso a la PSTN. Éstos troncales
son invocados por reglas de enrutamiento de llamadas salientes, en las cuales se puede especificar qué tipo de llamadas son procesadas
por cada troncal SIP. Además los troncales pueden ser configurados en modo *failover*

En el video se expone una configuración típica y escencial que permite dejar activo un troncal SIP y una ruta de acceso a la PSTN desde OMniLeads a un sistema PBX basado SIP.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/320936127" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Para profundizar al respecto se recomienda leer el resto del capítulo.

  .. toctree::
   :maxdepth: 2

   telephony.rst


********
CAMPAÑAS
********
Todo procesamiento de comunicaciones entre "el exterior" y un agente de OMniLeads es encapsulado sobre una campaña. En este capítulo se aborda todo lo inherente a la gestión de campañas Entrantes y Salientes (manuales, preview y dialer)

En el video se expone una introducción conceptual a las campañas en OMniLeads, ejemplificando además paso a paso la creación de:

- Base de contactos
- Calificaciones de campañas
- Formulario de campaña
- Agentes


.. raw:: html

        <iframe src="https://player.vimeo.com/video/320946591" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>



En el resto del capítulo formulamos campañas a partir de contar con los cuatro elementos constituidos en el video anterior, así nos adentramos
en los detalles de cada uno de los tipos de campañas disponibles en OMniLeads.

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
