.. _about_usecase_pbx:

OML como Contact Center integrado a un PBX basado en SIP
*********************************************************


OMniLeads resulta ideal para las compañías que demandan funcionalidades típicas de Contact Center como extras a lo que brinda la central PBX.  OMniLeads surge como una alternativa para complementar dicha central PBX, desde una instancia independiente (bare-metal host, virtual machine o infraestructura en cloud) integrada al PBX, permitiendo el fluir de las comunicaciones entre ambos componentes y de manera transparente.

Se plantea romper con el paradigma tradicional de adquisición de un stack de software para instalar sobre el PBX, evitando dos tipos de costos:

El coste económico que involucran las licencias de software de las herramientas complementarias para que el PBX obtenga algunas funcionalidaes de Contact Center.

El coste en términos de performance del core de telefonía “PBX” sacrificada para correr complejos reportes y herramientas de monitoreo, que implica ejecutar un «módulo de call center» sobre el sistema PBX.

.. image:: images/oml_and_pbx.png
        :align: center


.. _about_usecase_bpo:

OML en una Compañia de servicios de Customer Contact
*****************************************************

Bajo este escenario, OMniLeads puede trabajar como núcleo de comunicaciones de un Contact Center con agentes que van entre las decenas y centenas.
En este escenario OMniLeads puede manejar múltiples troncales SIP a la vez, con su pertinente enrutamientos entrante y saliente de comunicaciones.

En estos contextos la escalabilidad es un requisito básico, ya que las operaciones son muy dinámicas y pueden demandar picos de usuarios conectados
trabajando en simultánea. La escalabilidad se garantiza a partir de concebir nuestra solución de manera tal que pueda ser facilmente desplegada
en modalidad de cluster.

.. image:: images/oml_bpo.png
        :align: center


.. _about_usecase_cloud:

OML para Carriers ó Proveedores de Cloud PBX
********************************************

Si la necesidad es implementar un servicio de CCaaS (Contact Center as a Service) OMniLeads resulta ideal a partir de la ventaja otorgada por WebRTC como
tecnología base.

Podemos citar como ventajas:

* **WebRTC** elimina la necesidad de instalar aplicaciones softphone para escritorio, ya que la voz y el video fluye a través del browser de los agentes y supervisores. Esto elimina un punto de falla y mantenimiento sobre las estaciones de trabajo.

* Los **Codecs** implementados para audio y video son Opus y VP8, ambos diseñados para funcionar en internet y se adaptan dinámicamente al ancho de banda disponible, lo que evita los incómodos entrecortes de llamadas de la VoIP convencional.

* **Seguridad**: el intercambio de información entre las estaciones de trabajo y la instancia de OML en Cloud, se encuentra encriptado bajo los estándares HTTPS, sRTP y dTLS.

* `Kamailio <https://www.kamailio.org/>`_ es parte del core de comunicaciones de OMniLeads. Se trata de un Proxy-SIP de avanzadas prestaciones y crucial para brindar seguridad a servidores de VoIP y Video de acceso público en internet.


.. image:: images/what_is_webrtc_oml.png
        :align: center
