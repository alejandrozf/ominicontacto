************************
INTRODUCCION A OMNILEADS
************************


`OMniLeads <https://www.omnileads.net/>`_ es un Software `GPLV3  <https://www.gnu.org/licenses/gpl-3.0.en.html/>`_ para Contact Centers basado en `WebRTC <https://www.webrtc.org/>`_ ,
que permite implementar y gestionar un Contact Center administrando operaciones entrantes y salientes, con acceso a métricas, reportes e indicadores, supervisión real-time de agentes y demás funcionalidades avanzadas
de QA, gestión de contactos y campañas.

A partir de una sencilla instalación junto a unos pocos pasos de Configuración post-instalación, se dispone de una instancia funcional
de OMniLeads lista para traccionar operaciones de Contact Center en términos de campañas entrantes y salientes.

Esta aplicación puede adaptarse a una compañia u organización que necesita
montar su propio Contact Center integrado a su central IP-PBX, así como también asumir la función de "núcleo" de comunicaciones para
una compañía que brinda servicios de Customer Contact (Business Outsourcing Process) o bien ser ejecutada en instancias del tipo VPS o proveedores de nube pública.

Dentro de un universo 100% web, los diferentes perfiles de usuarios; agentes, supervisores, administradores, clientes, acceden a OMniLeads desde
cualquier navegador web moderno con soporte `WebRTC <https://www.webrtc.org/>`_. Al no requerir del uso de aplicaciones de escritorio *Softphones*, OMniLeads
reduce a nada respecto a la configuración de las estaciones de trabajo de los agentes, tan solo con acceder a la dirección web HTTPS, agentes y supervisores pueden estar
online gestionando comunicaciones con los clientes. Esta facilidad hace de OMniLeads una gran opción para implementar CCaaS "Contact Center as a Service" !


.. image:: images/what_is.png
        :align: center


Cómo lo obtengo ?
*****************
`Nuestro repositorio  <https://gitlab.com/omnileads/ominicontacto>`_ se encuentra disponible en GitLab, para libre descarga, instalación, modificación y uso del Software.


Cómo lo instalo ?
*****************

En la sección :ref:`about_install` se aborda este asunto presentando los pasos a seguir para instalar la aplicación bajo cualquiera de los esquemas mencionados con anterioridad.


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


*********************
INTEGRACION CON PBXs
*********************

A partir de unas pocas configuraciones se puede establecer una completa integración entre OMniLeads y cualquier central IP-PBX. En esta sección se ejemplifica
paso a paso la configuración necesaria para dejar integrada una IP-PBX (con sus recursos locales y acceso a la PSTN) y OMniLeads operando como una tecnología
de Contact Center complementaria y extensiva del sistema de telefonía basado en dicha IP-PBX

 .. toctree::
  :maxdepth: 2

  pbx_integration.rst


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
