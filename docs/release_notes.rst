Release Notes
*************

*August 13, 2020*

Detalles de Release 1.9.0
=========================


Nuevas funcionalidades
--------------------------
- La supervisión fue refactorizada para almacenar su informacion en tiempo real en Redis desde AstDB para mejorar la performance
- La IU para escoger una opción de calificación en los wizards de creación de campañas fue mejorada
- Se implementó un filtro por id de contacto externo en la vista de grabaciones
- Se adicionó la estadística de cantidad de reintentos abiertos en la vista de detalle de campañas dialer
- En la instalación del sistema ahora se utiliza un único certficado SSL para todos los componentes
- Se adicionó soporte para bases de contactos de mayor tamaño en campañas dialer


Fixes y mejoras
--------------------------
- Solucionado error cuando un supervisor asignado a un campaña intentaba bloquear campos para agente lanzaba un error
- Solucionar error de dialplan que se generaba al intentar guardar información de la grabación de una llamada en medio de una transferencia consultativa
- Solucionado error de instalación de upgrade al actualizar el paquete virtualenv
- Solucionada inconsistencia cuando un agente pasa de un pausa ACW (con el timeout) a otra pausa
