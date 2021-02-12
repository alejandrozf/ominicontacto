Release Notes
*************

*Febrero 12, 2021*

Detalles de Release 1.13.0
=============================

Nuevas funcionalidades
--------------------------
- Una nueva interfaz para configurar el formato del nombre de los archivos de grabaciones fue implementada
- Se realizaron mejoras de performance para las vistas de supervision
- Se adicionaron alertas en tiempo real para agendas de agentes
- Se implementó una nueva interfaz para configurar el comportamiento de agentes por campaña
- Se actualizó el componente Asterisk a la versión 16.16
- Una nueva interfaz para configurar el modulo AMD fue adicionada
- La posibilidad de configurar un audio personalizado para que se reproducido en llamadas entrantes fue adicionada
- La funcionalidad de seleccionar contacto en la consola de agente para una campaña preview fue mejorada
- El reporte general de agentes fue optimizado para mejor performance
- Ahora se muestra información de los ids de campañas y formularios en sus respectivas vistas de listado
- La vista de 'Ver contactos asignados' para campañas preview fue mejorada
- En el paso de asignar supervisores a campañas preview ahora se muestra información sobre el nombre y apellido del supervisor
- Ahora es posible filtrar archivos de grabación de campañas eliminadas en la vista de búsqueda de grabaciones
- El sistema ahora permite pasar variables de canal de Asterisk como parámetros en la interacción con un sitio externo




Fixes y mejoras
--------------------------
- Solucionado error en dialplan relacionado con AMD en llamadas dialer
- Solucionado error en dialplan al transferir una llamada a un agente
- Solucionadas inconsistencias en el reporte de contactados de una campaña
- Las campañas dialer son recargadas en Wombat luego de su creación/modificación.
- Solucionada condición de carrera cuando un agente recibía una llamada entrante/dialer en medio de una transition de cierre a pausa
- Solucionado problema de compatibilidad con Excel al importar archivos .csv en la funcionalidad de reordenar contactos en campañas preview
- El componente Ansible fue dockerizado para permitir realizar instalaciones remotes desde SO diferentes a Ubuntu-18.04
- Ahora se muestran caracteres Unicode en la lista de calificaciones de la consola de agente y en la creación de formularios
- Se mejoró el diseño del reporte general de llamadas
- Se solucionó error al mostrar node de destino personalizado
- Se mejoró el script de coverage para hacerlo mas sencillo
