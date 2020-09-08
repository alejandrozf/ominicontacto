Release Notes
*************

*Septiembre 8, 2020*

Detalles de Release 1.10.0
==========================

Nuevas funcionalidades
--------------------------
- La página de supervisión de campañas entrantes fue optimizada para ser más performantes
- Asterisk puede ser ahora opcionalmente separado para que se ejecute en otro host
- Asterisk fue actualizado a la version 16.12.0
- Se adicionó un endpoint para la API para crear bases de contactos
- Las páginas de reportes de una campaña fueron optimizadas para ser más performantes
- La UI de la página de asignación de supervisores a una campaña creada fue mejorada


Fixes y mejoras
--------------------------
- Solucionado error al conectar con Kamailio cuando este se encontraba separado en otro host
- Solucionado error de inconsitencia en permisos que no permitía a supervisores editar perfiles de agentes
- Solucionado error que impedía editar campañas preview cuando se escogía el parámetro de sitio externo para editar
- Solucionado error al intentar linkear los archivos de dialplan de Asterisk al container de Asterisk correspondiente
- Solucionado error de encoding al aplicar migración de trigger de la BD
- Solucionado error que impedía usar el nombre de usuario de un usuario eliminado
