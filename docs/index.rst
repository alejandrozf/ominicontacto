************************
INTRODUCCION A OMNILEADS
************************


`OMniLeads <https://www.omnileads.net/>`_ es una Aplicación Web para Contact Centers basada en la licencia de software libre `GPLV3  <https://www.gnu.org/licenses/gpl-3.0.en.html/>`_.

Esta App permite implementar y gestionar operaciones de Contact Center tanto entrantes como salientes y en modalidad Blended. La App pone a disposición métricas, reportes e indicadores,
supervisión real-time de agentes, módulos de auditorías para backoffice y demás funcionalidades avanzadas de QA, gestión de contactos y campañas.

El hecho de ser 100% `WebRTC <https://www.webrtc.org/>`_ convierte en ideal para montar operaciones con agentes en modalidad home-office debido a la eficiencia y seguridad criptográfica que
implica la tecnología WebRTC en su operación por defecto al momento de mantener sesiones de voz y/o video a través de Internet.

Los diferentes perfiles de usuarios; agentes, supervisores, administradores o clientes acceden a OMniLeads desde cualquier navegador web moderno. Al no requerir del uso de aplicaciones de escritorio
*Softphones* no es necesario realizar las típicas configuraciones sobre las estaciones de trabajo de los agentes de contact center, tan solo con acceder a la dirección web HTTPS donde reside
la App, agentes y supervisores pueden estar online gestionando comunicaciones con los clientes. Esta facilidad implica una gran ventaja a la hora de brindar servicios de Cloud CCaaS (Contact Center as a Service).

OMniLeads puede adaptarse a una compañia u organización que necesita montar su propio Contact Center integrado a su central PBX, así como también escalar hacia compañías
que brindan servicios de Customer Contact (Business Outsourcing Process) ya sea en entornos on-premise así como también en despliegues en Cloud.

.. image:: images/what_is.png
        :align: center


Cómo la obtengo ?
*****************
`El repositorio  <https://gitlab.com/omnileads/ominicontacto>`_ se encuentra disponible en GitLab, para libre descarga, instalación, modificación y uso del Software.


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

Esta documentación cubre todos los aspectos del producto. Desde cuestiones técnicas inherentes al administrador IT, hasta aspectos funcionales orientados a los agentes, supervisores
o líderes del contact center.

***********
INSTALACIÓN
***********

En este capítulo se cubren todos los tipos de instalación de la App.

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


************************************
AUDITORIA SOBRE GESTIONES DE AGENTES
************************************
Cada vez que un agente genera una *gestión positiva* con un contacto, existe la posibilidad de auditar la misma desde el *módulo de auditorías*.

   .. toctree::
    :maxdepth: 2

    backoffice.rst


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
