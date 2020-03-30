Release Notes
*************

*Marzo 28, 2020*

Detalles de Release 1.5.2
=========================

Bug fixes
---------
- Solucionado error que regeneraba todos los datos de agentes en AstDB con status vacío después de crear/modificar agente
- Solucionado error que ocultaba los link a calificaciones de llamadas sin identificar en busqueda de grabaciones
- Solucionada condición de carrera en el método close() de pyst2 que afectaba al sistema
- Solucionado error en la configuración de uwsgi que elevaba el uso de CPU
- Solucionado error en el parsing de entradas de agentes en AstDB que contienen la key PAUSE_ID
- Solucionado error en la vista de reporte de supervisión de campañas entrantes
