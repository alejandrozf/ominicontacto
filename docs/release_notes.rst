Release Notes
*************

*March 20, 2020*

Detalles de Release 1.5.0
=========================

Nuevas funcionalidades
----------------------
- Django fue actualizadp a la versión 2.2.7 y, por tanto, todo el código python fue migrado a python3
- El parsing de los headers de Asterisk DB fue optimizado
- Ahora es posible distribuir los contactos entre agentes de forma proporcional en la creación de campañas preview
- Se adicionaron nuevos endpoints que permiten la interacción de agentes con Asterisk
- Se adicionaron nuevos parámetros a las campañas entrantes
- Se adicionó información sobre el release actual después de loguearse un administrador
- Se adicionó la posibilidad de realizar grabaciones de llamada bajo demanda
- Se eliminó el soporte para instalaciones AIO de Ubuntu/Debian
- Se refactorizó el deploy del sistema en entornos basados en Docker
- El sistema ahora permite auditar grabaciones y re-calificar llamadas por supervisores
- Los agentes pueden ahora visualizar las grabaciones de sus propias llamadas
- Asterisk fue actualizado a la versión 16.9.0
- Se le realizaron modificaciones estéticas al formulario de calificación
- Se habilitó destino  si NO se identifica correctamente para Tipo de interacción "externa 2" para el objeto de telefonía Identificador de Clientes



Bug fixes
---------
- Solucionado error que oocrría al intentar asignar columnas de la base al URL de sitio externo
- Solucionado error que no renderizaba la URL de sitio externo en la Agent Toolbar
- Solucionado error en script de restore backup
- Se adiciona validación para evitar setear tiempo de anuncio sin haber elegido anuncio perióidico
- Solucionado error que ocurría al cumplirse una regla de incidencia en campañas dialer y trackeaba mal el OUTNUM en queue_log
