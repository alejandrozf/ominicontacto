***********************************
Interacciones con Sistemas Externos
***********************************

Interacción con un Sitio externo
********************************
La configuración de un Sitio Externo permite interactuar con un Sistema Externo en el momento en que se establece una llamada con un agente.
Para crear una nueva configuración debe dirigirse a Campañas -> Sitios Externos -> Nuevo Sitio.
Las posibles formas de interactuar son o lanzando una petición desde el servidor OML, o bien desde la ventana del agente automáticamente o mediante un botón que deberá presionar el mismo Agente. Estas tres formas se configuran con la opción "Disparador", que puede ser "Servidor", "Automático" o "Agente" respectivamente.
El método de la petición podrá ser "POST" o "GET", y se disponen de varios formatos para enviar los parámetros.
La opción "Objetivo" estará disponible al seleccionar como disparador al "Agente" o "Automático", y permite elegir si se abrirá una nueva ventana o si se realizará en la misma ventana del agente. Esta forma de interacción permitiría por ejemplo que cada agente del call center disponga automáticamente de una vista del contacto de la comunicación actual, sobre el CRM Web externo.

En cada llamada al CRM se pueden enviar datos de la llamada, del contacto o valores fijos como por ejemplo:

- El "path" de la grabación de la llamada.
- El "id" del agente.
- El "id" de la campaña.
- Cualquiera de las columnas de la base de datos de contactos asociada a la campaña.
- Un valor fijo que identifique a que cliente corresponde la campaña en el CRM.

Entre otros parámetros.


Identificación de entidades del Sistema Externo
***********************************************

Para utilizar las API de generación y de calificación de  de llamadas se debe poder identificar a las entidades pertinentes, por ejemplo la campaña, el contacto y el agente. Esto puede hacerse usando los identificadores automáticos que genera el mismo sistema Omnileads, pero probablemente el Sistema Externo mantenga identificadores distintos, por lo que puede ser necesario sincronizar estos identificadores. Omnileads permite esta sincronización mediante la configuracion de los campos "identificadores externos".

El primer paso es crear un Sistema Externo y asociarle Agentes a los cuales se les asignarán los identificadores que estos tienen para el Sitio Externo. Estos identificadores deberán ser únicos para cada agente del Sistema Externo. Claramente, al utilizar identificadores externos solamente se podrá referenciar a los agentes que los tengan asignados. Cada agente podrá tener un identificador externo para cada Sistema Externo al que este asociado.

Al cargar una Base de datos de Contactos se deberá seleccionar uno de los campos como el poseedor del valor identificador en el sistema externo. Este valor deberá ser único para cada contacto de la base de datos, por lo que no podrán cargarse dos contactos con el mismo valor en una misma base de datos. Cada contacto solo podrá tener un identificador externo.

Para poder identificar a una Campaña con un identificador externo a la hora de su creación deberá indicarse cuál es el Sistema Externo al que pertenece, y además indicarle un valor como su identificador externo. Cada campaña solamente podrá tener un identificador externo.
Con estos valores configurados ya se pueden identificar agentes, campañas y contactos con sus correspondientes en el sistema externo. Para asistir en la configuración de identificadores externos se mostrarán notificaciones en caso de que se detecten situaciones que posiblemente puedan llegar a indicar una configuración errónea.

Cuando se asigna un Sistema Externo a una Campaña estas notificaciones aparecerán en caso de que:

 - A la campaña se le asignen agentes que no tengan identificador externo en el Sistema Externo seleccionado.
 - A la campaña se le asigne una base de datos que ya este asignada a una campaña asociada a OTRO Sistema Externo.
 - A la campaña se le asigne un Sitio Externo que ya esté siendo utilizado en una campaña asociada a OTRO Sistema Externo.
 
 También aparecerán notificaciones en caso de que al editar un Sistema Externo falte asignar identificadores externos a Agentes utilizados en Campañas relacionadas con el Sistema Externo.


Realizar y calificar llamadas a traves de la API
************************************************

Utilizando la API de Omnileads un Sistema Externo puede ordenar la realización de una llamada indicando el Agente, la Campaña, el número de teléfono a llamar y el Contacto al que corresponde la llamada.
Luego también puede realizar la calificación de la llamada indicando también los parámetros correspondientes.
Para realizar y calificar una llamada se debe tener el cuenta el método que se utilizará para identificar las entidades que participan de la operación, ya sea utilizando identificadores de Omnileads o identificadores externos. Para usar este último método se deberá indicar a que Sistema Externo deberań estar relacionadas las entidades.
Para más detalle sobre cómo utilizar estas funcionalidades ir a la sección API

.. toctree::
 :maxdepth: 2

 api.rst
