Qué es OMniLeads (OML)?

OMniLeads (OML) es una solución de Software Open Source basada en tecnología WebRTC(link) destinada a soportar la gestión, operación y administración de un Contact Center a través de múltiples canales de comunicación. Actualmente permite la gestión y despliegue de atención telefónica a través de: Campañas Entrantes, Campañas Preview y Campañas Salientes Manuales de manera nativa. También cuenta con la posibilidad de administrar Campañas con Discador Predictivo/Progresivo por medio de APIs de Integración.

Es parte del roadmap del software la inclusión de Envío/Recepción de SMS, Integración con Redes Sociales, Campañas de Chat desde la página web, Campañas de IVR (press one), entre otras funcionalidad posibles.

El software soporta únicamente Sistemas Operativos GNU/Linux, cuyas distribuciones se especifican en las secciones de instalación.

Características
    •    Consola de Agente y Supervisor basada en WebRTC
    •    Diferentes perfiles de usuario: administrador, supervisor admin, supervisor cliente, agente
    •    Gestión de múltiples campañas
    •    Detección de Contestadores
    •    Full Recording
    •    Reportería de Productividad
    •    Supervisión en Tiempo Real
    •    Diseño Simple de Formularios Web
    •    API de Integración con CRM/ERP
    •    Modalidad de Agentes Remotos
    •    Integración con PBXs Open Source
    •    Clusterización de componentes

Componentes
Las tecnologías involucradas en OMniLeads (OML) también forman parte de proyectos Open Source, entre ellos:
    ⁃    Asterisk
    ⁃    Kamailio
    ⁃    RtpEngine
    ⁃    Django
    ⁃    Nginx
    ⁃    Postgres
    ⁃    Python
    ⁃    Javascript

Licencia
GPLv3. Cada archivo de código fuente refiere en su cabecera a la licencia y detalles de copyright correspondiente.

Versión Actual
1.0.X.

Documentación
La documentación oficial del proyecto puede encontrarse en la página oficial: https://omnileads.net/.


Instalación
Al momento de la redacción de este README, el software OMniLeads (OML) soporta las siguientes distribuciones:
- GNU/Linux CentOS 7 en su versión minimal
- GNU/Linux Debian 9 en su versión netinstall

Un Tutorial “paso-a-paso” se pone a disposición en la sección de “Docs & Recursos” de su página oficial: https://omnileads.net/

El procedimiento actual de instalación comprende una arquitectura “All In One” (AIO), es decir con todos los componentes de OMniLeads (OML) desplegados sobre un sólo Host Servidor. Existe también la posibilidad de correr ciertos componentes o servicios en Hosts diferentes (escalabilidad horizontal), aunque su implementación no se cubre en esta descripción.

La herramienta seleccionada tanto para instalar OMniLeads (OML) como para correr las actualizaciones es: Ansible(link). La instalación puede llevarse a cabo bajo dos escenarios: 
1- Ansible In One: esto es, ejecutar la instalación corriendo Ansible en el mismo Host Servidor donde se quiere instalar OMniLeads (OML). 
2- Ansible In Two: esto es, ejecutar la instalación corriendo Ansible desde un entorno de trabajo (Host Deployer) e indicando en el instalador la Dirección IP (Internet Protocol) del Host Servidor donde se desea instalar el software.

El script de instalación se encuentra dentro del repositorio del software. Mayor información puede desplegarse utilizando el flag de ayuda “-h”:
./deploy.sh -h

Un ejemplo de instalación del último release estable se describe a continuación:
/deploy.sh -r master -i -t all

Por favor, LEA ATENTAMENTE el Tutorial de Instalación disponible en la página oficial del Proyecto OMniLeads (OML).


Repositorio de OMniLeads (OML):
El repositorio oficial del proyecto de software se encuentra en Gitlab: https://gitlab.com/omnileads/ominicontacto


Reporte de Issues y Bugs:

Para el reporte de Bugs o Request de nuevas features: https://gitlab.com/omnileads/ominicontacto/issues


Soporte a la Comunidad:

Por consultas relacionadas al roadmap del software:  community@omnileads.net
Por consultas relacionadas al soporte del software: support@omnileads.net
Por consultas comerciales del software: business@omnileads.net

Recursos Útiles:
Video-tutoriales pueden hallarse en el siguiente recurso: https://vimeo.com/user87733702
News: https://omnileads.net/news/
Twitter: @OMniLeads_net

Disclaimer:
Los componentes de software de terceros son marcas registradas de sus correspondientes propietarios o poseedores de marca. Su uso no implica ninguna afiliación ni colaboración a ellos por parte del Proyecto OMniLeads (OML).

--
