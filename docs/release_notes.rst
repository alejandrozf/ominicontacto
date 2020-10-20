Release Notes
*************

*Octubre 20, 2020*

Detalles de Release 1.11.0
=============================


Nuevas funcionalidades
--------------------------
- Fue realizado un refactor para usar Redis en vez de AstBD para la mayor parte de los datos que se usan en tiempo real en el proyecto
- Fue adicionada información del teléfono contactado y la campaña en la página de supervision de agentes
- A los usuarios no agentes se les requiere cambiar su contraseña en su primer login
- El sistema genera una contraseña por defecto para el usuario admin por defecto
- Es posible separar el componente Redis para usarlo en otro host
- Se creó un simulador de tráfico de llamadas entrantes para el entorno de desarrollo
- Se mejoró la interfaz de usuario del diálogo de llamadas entrantes


Fixes y mejoras
--------------------------
- Se solucionó inconsistencia en Reportes de Agentes para casos que no tenían eventos de cierre de sesión en logs
- Se solucionó inconsistencia en headers enviados desde dialplan
- Se limitó la longitud del nombre de las bases de contactos hasta 45 caracteres
- Se cambió la nomenclatura en la creación de bases de contactos recicladas
- Se solucionó el error generado cuando una base de contactos contenía algún id externo duplicado
