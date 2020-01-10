.. _about_webrtc:

WebRTC - Tecnología subyacente de OMniLeads
*********************************************
Antes de de citar los casos de uso, ponemos énfasis en repasar los beneficios de la tecnología WebRTC; núcleo de OMniLeads.

WebRTC dota a un navegador web de la posibilidad de mantener comunicaciones real time de voz, video, chat y compartición de pantalla.
OMniLeads se nutre de esta tecnología para nuclear las comunicaciones y la interfaz de gestión web, evitando el uso de aplicaciones de escritorio
"softphones", lo cual otorga una inmediatez en términos de "click and work" en el alta usuarios ya que a partir de un login web, están en línea
procesando comunicaciones.


.. image:: images/what_is_webrtc.png
        :align: center

**Otras ventajas de WebRTC**

- Se minimizan los puntos de fallo en las estaciones de trabajo.
- Se minimizan las tareas del helpdesk y por ende la demamda del personal de soporte/sistemas.
- Se trabaja con los codecs de audio Opus y video VP8, ambos concebidos para una máxima performance en entornos de internet (codecs internet nativos).
- A nivel seguridad todas las comunicaciones viajan cifradas de manera obligatoria, en términos de señalización y media.


.. _about_omlfeatures:

Características y funcionalidades de OMniLeads
***********************************************
- Gestión de campañas Entrantes y Salientes.
- Consola de agente WebRTC (no se requiere instalar ninguna aplicación ni plugin, 100% Web Browser).
- Opus ® como codec por defecto para todas las comunicaciones de Agente.
- Consola de supervisión WebRTC; detalle de estados de agentes y campañas.
- Reportes de productividad de agentes y campañas.
- Búsqueda de grabaciones con filtros de fecha, campaña, agente, calificaciones, llamadas "observadas", etc.
- Reciclado de campañas por calificación de agente y/o status telefónico.
- Cambio de base de contactos sobre la misma campaña.
- Detección de contestadores con reproducción de mensaje de audio.
- Integración con CRM / ERP a través de la API RestFull.
- Listo para virtualizar ! OML fue concebido como una tecnología orientada a los entornos de virtualización.
- Listo para Dockerizar ! OML está disponible en términos de imágenes Docker, lo cual permite ser ejecutado en cualquier OS así como también orquestando clusters Docker HA y/o despliegues en proveedores de Nube (AWS, GCloud, etc.).
- Listo para escalar ! La escalabilidad es posible debido al hecho utilizar tecnologías subyacentes muy potentes como Postgres, Nginx, Rtpengine, que a su vez pueden correr en hosts independientes (escalabilidad horizontal) con una mínima configuración.
- Addons complementarios que dotan a la plataforma de funcionalidades extras y/o para segmentos verticales.
- 100% orientado a Contact Center. No se trata de un software de PBX con agregados de reportería y/o supervisión. La App fue concebida desde cero y como una plataforma orientada y optimizada para funcionalidades de Contact Center.
