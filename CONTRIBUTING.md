Política de contribuciones externas
===================================

Si desea contribuir al desarrollo de OMniLeads puede crear una incidencia en https://gitlab.com/omnileads/ominicontacto/issues (1) y ,opcionalmente, un merge-request con el código que propone una solución al respecto a través de los siguientes pasos:

  * Garantizar tener un entorno de desarrollo a partir de una instalación del sistema (leer las instrucciones de instalación)
  * Clonar localmente el repositorio
  * Crear una incidencia en (1) y tomar el número de esta (en lo adelante _numero-incidencia_)
  * Crear una rama tomando como base la última versión de la rama 'develop' en el repositorio
      * Escribir código claro, conciso y bien comentado
      * Deberá nombrarse siguiendo el esquema _oml-ext-numero-incidencia-descripcion-precisa_
      * Seguirá el estándar PEP8 teniendo en cuenta la configuración especificada en el archivo .flake8 en la raíz del repositorio
      * Debe garantizar que el sistema de tests unitarios del proyecto se mantenga sin errores o fallas en su ejecución
      * Si se agrega una nueva funcionalidad al sistema deberá escribir tests-unitarios que la documenten correctamente
      * Actualizar la rama con respecto a la rama 'develop' previo a realizar el merge-request usando 'rebase', esto es:
          * $ git rebase develop
      * Subir la rama creada al repositorio:
          * $ git push origin _oml-ext-numero-incidencia-descripcion-precisa_
      * Crear el merge-request desde la interfaz del repositorio
