Release Notes
*************

*Junio 29, 2020*

Detalles de Release 1.7.0
=========================

Nuevas funcionalidades
--------------------------
- Un nuevo sistema de permisos fue implementado, reescribiendo y generalizando el existente, ahora es posible crear roles de usuarios y administrar sus permisos a las funcionalidades del sistema
- Fue implementada una funcionalidad para auditar las calificaciones de llamadas a contactos por agentes. Se permite además filtrar calificaciones y se muestra el valor de dicha auditoría en el formulario de calificaciones para agentes
- La página de supervisión de agentes ahora muestra información de estado de agentes que están no disponibles (UNAVAILABLE)


Bug fixes y mejoras
--------------------------
- Solucionado error que escribía datos inconsistentes en AstDB para llamadas entrantes.
- Solucionado error que escribía datos vacíos para campos ocultos de contactos en una campaña
- Solucionado problema al restringir el campo CID en wizard de creación de campaña saliente
- Solucionado error al eliminar un nodo destino entrante
- Solucionado error en vista de supervisión de agentes
- Solucionado error que no permitía retroceder en los wizards de campañas dialer y entrantes
- Solucionado error que mostraba siempre la primera opción a agentes en el formulario de la campaña
- Solucionado error de instalación que duplicaba algunos archivos de dialplan
- Solucionado error en job de gitlab para crear imágenes de docker para entornos productivos
- Solucionado error en Ubuntu que detenía la instalación si el SO no tenía python-pip instalado
- Solucionados errores de audio en una sola dirección en algunos ambientes de Cloud
- Solucionada incorrecta exportación de reporte de campaña a PDF
