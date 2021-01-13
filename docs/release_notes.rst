Release Notes
*************

*Enero 13, 2021*

Detalles de Release 1.11.8
=============================

Nuevas funcionalidades
--------------------------
- Toda la comunicación AMI con Asterisk usa TCP AMI ahora en vez de HTTP AMI
- Los supervisores pueden asignar y liberar contactos de/a agentes en campañas preview
- Es posible ahora, opcionalmente, ocultar opciones de calificaciones en campañas
- El sistema ahora logue en la base de datos las llamadas fuera de campaña
- Fue implementado un dashboard para agentes
- Las reglas de incidencia en campañas dialer pueden ser relacionadas con las opciones de calificación en la campaña de manera permitiendo un funcionamiento más flexible en campañas dialer
- Se adicionó una página con información de los addons comerciales disponibles
- Ahora es posible realizar el reciclado de una campaña dialer cuando aún se encuentra activa
- El sistema ahora reproduce un audio cuando se intenta llamar a un número que se encuentra en una lista negra
- Se mejoró la seguridad del componente Redis
- Un nuevo parámetro de instalación para el componente RTPEngine fue adicionado
- El códec g729 es instalado ahora por defecto para el componente Asterisk
- Un botón para reenviar la clave del registro de la instancia de OMniLeads ya registrada fue implementado.
- Los grupos de agentes pueden ser configurados para controlar si los agentes pueden ir al estado Ready si no han completadp una calificación pendiente
- Es posible realizar videollamadas entrantes usando el addon CLICK2CALL



Fixes y mejoras
--------------------------
- Solucionado error de dialplan que permitía derivar un número en una lista negra a ser llamado por un agente en una campaña dialer
- Solucionado error al transferir una llamada fuera de campaña hacia un agente
- Solucionado error al liberar un contacto en una campaña preview
- Solucionado error en condición de carrera en la consola de agente cuando se solapaban el momento de login y una llamada en cola que entra
- Solucionado error al reciclar una campaña preview sobre sí misma
- Solucionado error en consola de agente cuando un agente recibía una llamada entrante justo después de cortar una llamada saliente, lo cual no permitía calificar la llamada saliente
- Solucionado error de dialplan que generaba entradas corruptas en Redis
- Solucionada issue #70
- Solucionado error de diaplan que logueaba evento incorrecto para llamadas en BUSY
- Solucionado error al cambiar la contraseña de un usuario y establecer una mayor o igual a 22 caracteres
- Solucionada inconsistencia al comparar estadísticas de actividad de agente entre diferentes reportes
- Los tests de integración fueron refactorizados para una mejor organización
- El código de los reportes de campaña fue refactorizado para mejorar su performance
- El sistema de permisos fue mejorado para garantizar que solo los roles "Administrador" puedan crear o editar otros roles "Administrador"
- Solucionada inconsistencia en reporte de calificaciones dentro de la vista del reporte de la campaña, para mostrar exactamente el status del registro contactado
- Solucionado error aleatorio de desplazamiento UTC
- El script de backup/restore fue mejorado
