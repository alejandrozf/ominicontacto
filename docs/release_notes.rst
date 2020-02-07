Release Notes
*************

*February 7, 2020*

Detalles de Release 1.4.0
=========================


Nuevas funcionalidades
-------------------------
- OML ahora puede ser deployado e integrado con Issabel PBX & FreePBX usando docker
- Se realizón la migración de endpoints de agentes Asterisk de chan_sip hacia PJSIP
- El sistema soporta troncales SIP basados ahora en el módulo PJSIP de Asterisk
- Las interacciones con Asterisk desde la consola de agentes fueron refactorizadas para usar el protocolo AMI
- Se realizaron mejoras en la instalación del sistema en Docker para ambientes productivos
- PostgreSQL fue actualizado a la versión 11
- Se adicionaron nuevos endpoints para la API pública que enriquecen la interacción con CRM
- El archivo kamailio.cfg fue refactorizado y optimizado
- El trigger usado como logger de eventos fue portado desde plpython a plperl


Bug fixes
-------------------------
- Solucionado bug que contaba como ABANDONWEL los eventos de llamadas entrantes que excedían el límite de llamadas en
  cola configurado that exceeds the queue calls limit, afectando a los reportes
- Solucionado bug en paginación de las vistas de listas de objetos de telefonía
- Solucionado bug que contaba como EXPIRED a los eventos de llamadas entrantes con un destino en
  caso de fallo configurado en la campaña como destino personalizado, afectando a los reportes
- Solucionado error de redirección infinita al eliminar un agente logueado
- Solucionada inconsistencia en AstDB al eliminar agentes
- Solucionado bug que generaba un valor de callid incorrecto al realizar llamadas manuales de click2call
  afectando los reportes
- Solucionado bug que impedía editar el parámetro 'boost factor' en campañas dialer
- Solucionado error generado en la vista de supervisión de llamadas entrantes cuando
  existía alguna llamada dialer en cola
- Solucionado bug que eliminada los datos almacenados usando django-constance en instalaciones
  en docker despues de reiniciar el servicio de kamailio
- Solucionado bug que enviaba un id incorrecto al finalizar una pausa de tipo ACW.
- Solucionado error en la paginación de la vista de supervision de agentes
