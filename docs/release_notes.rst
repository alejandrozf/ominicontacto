Release Notes
*************

*Octubre 3, 2019*

Release 1.3.2 detalles
=========================

Nuevas funcionalidades
=========================

- Puedes adicionar tu código Asterisk personalizado para OMniLeads!
- OML puede ser accedido detrás de un NAT
- La vista de registro de instancia de OML ahora envía un email al administrador cuando el registro es exitoso
- La documentación ha sido traducida al inglés
- El CI/CD ha sido mejorado con jobs que testean todos los tipos de instalaciones que soportamos
- Los audios de Asterisk pueden ser adicionados al sistema dinámicamente desde la UI


Tareas de instalación
---------------------------------------------------------------
- Solucionado error en las rutas de los audios de identificación
- Ahora la actualización del sistema no necesita modificar el archivo de inventory
- No es necesario especificar el hostname para las instalaciones de tipo hostnode
- El usuario puede adicionar su propio certificado en el inventory
- Se adicionaron reintentos para las tareas de larga duración de descarga para evitar fallos
- Fue mejorada la persistencia del contenedor de redis (para los entornos de prod-env y dev-env)
- El Dev-env fue mejorado para poder leer las variables de entorno desde un archivo .env al igual que el prod-env.
- Ahora un cambio en la variable PGPASSWORD en su archivo .env, realiza ese cambio también en el container de postgres
- Se adicionó un script de desinstalación


OML admin
-------------------------
- Se adicionaron los reportes de promedio de tiempo de abandono, promedio de tiempo de espera y llamadas en espera para campañas entrntes
- Se solucionó error que impedía reciclar más de una vez a partir de una misma campaña dialer
- Se solucionó error que impedía acceder a los reporte diarios de agentes
- Se solucionó error en formularios de IVR al cargar archivos de audio externos
- Se solucionó error en la edición de campañas que no permitía modificar sus formularios asociadas a las opciones de calificación de gestión
- Se solucionó error que impedía editar campañas creadas con el campo interacción de sitio externo definido
- Se solucionó error que lanzaba excepción al intentar acceder al reporte de una campaña
- Los nombres de las bases de datos de contactos deben ser distintas desde ahora
- Los nombres de los grupos de agentes deben ser diferentes a partir de ahora


OML vista de agente
------------------------
- Solucionado error generado al visualizar la lista de llamadas realizadas, se adiciona mas información en esa vista
- Se adicionó una opción de rellamada desde la lista de llamadas realizadas


Asterisk dialplan
------------------------
- Se adicionaron logs más descriptivos
- Se solucionó error en la inserción hacia BD de los eventos de tipo Blacklist
- Se solucionó error que introducía demoras en procesar una opción de IVR
- Se solucionó error al manejar una opción de IVR incorrecta

Misc
------------------------
- Los primeros tests de integración fueron creados y sincronizados con el CI/CD
- Se introdujo una tarea de cron que limpia diariamente la tabla 'queue_log'
- El código JavaScript fue separado de los templates de Django
- Los archivos estáticos fueron organizados hacia sus apps más relacionadas
- Fue adicionada la redirección hacia una url interna al loguearse el usuario
