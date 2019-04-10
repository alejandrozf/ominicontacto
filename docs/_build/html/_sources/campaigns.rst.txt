
********************
Campañas Telefónicas
********************

Una campaña representa una manera de clasificar dentro de la plataforma a una operación de Contact Center que integra:


- Un grupo de agentes procesando llamadas en un sentido (outbound o inbound).
- Una base de contactos asociada a la campaña.
- Un listado de calificaciones que se despliegan a la hora de clasificar la llamada gestionada por el agente.
- Uno o varios formularios de campaña, a ser desplegados en caso de que el agente asigne una calificación de "gestión" asociada a alguno de los formularios, sobre la llamada en curso. El formulario es desplegado por dicha calificación y el agente puede completar el mismo según los datos del contacto en curso.

En la figura 1, se ilustra todo lo citado en los ítems.

.. image:: images/campaigns_elements.png

*Figure 1: the campaigns elements*

El hecho de trabajar bajo campañas, permite a los perfiles de usuarios Supervisor/Administrador extraer información y métricas de cada campañas, así como también realizar monitoreo en tiempo real o buscar grabaciones, entre otras acciones, usando como criterio de filtrado a las campañas.
Podemos contar con diferentes campañas de diferente naturaleza (predictivas, preview, entrantes o manuales), conviviendo de manera simultánea en OMniLeads y dejando registros sobre las llamadas transaccionadas por los agentes.


.. image:: images/oml_bpo.png

*Figure 2: Campaigns, agents, supervisors and backoffice*


Calificaciones
**************

Las calificaciones constituyen un listado de etiquetas disponibles para ser vinculadas a cualquier campaña, de manera tal que luego las llamadas procesadas dentro de una campaña pueda ofrecer dichas calificaciones al agente
afectado a una llamada i así éste ultimo pueda cerrar (temporal o definitivamente) la gestión de la llamada utilizando una de las calificaciones disponibles en la campaña como etiqueta para tipiicar la gestión.

Las calificaciones las define el supervisor o administrador y se pueden relacionar a varios aspectos, por ejemplo:

- El estado del contacto (respondió, no atendió, numero equivocado, etc.)
- El resultado de la gestión (interesado, no interesado, se ofreció producto, se vendió, etc.)
- La predisposición del contactado o el resultado de una encuesta de satisfacción (cliente conforme, enojado, etc.)

Las calificaciones pueden ser totalmente arbitrarias y para generarlas se debe ingresar al punto de menú; *Campaigns → Call Dispositions → New Call Dispositions*.

Podemos listar las calificaciones generadas dentro de *Campaigns → Call Dispositions → Call Dispositions*

.. image:: images/campaigns_calldispositions.png

*Figure 3: Call dispositions*

Base de contactos
*****************
Las bases de datos son utilizadas tanto para las campañas entrantes como salientes. En las campañas salientes, los datos que requiere el discador predictivo/preview se extraen de la base de contactos afectada a la campaña, mientras que en las campañas entrantes aportan los datos que se despliegan en la pantalla del agente cada vez que ingresa al sistema alguna comunicación

Deben estar almacenadas en archivos con formato CSV con los campos separados con coma y además generadas en la codificacipón UTF-8 (requisito excluyente). Debe existir al menos una columna
que contenga un teléfono de cada contacto (registro) del archivo, el resto de las columnas puede contener cualquier contenido, generalmente cada registro cuenta con datos complementarios
al teléfono principal. Éstos datos son expuestos en la pantalla de agente a la hora de establecer una comunicación entre ambos (agente y contacto de la base).

.. image:: images/campaigns_contactdb_1.png

*Figure 4: Contacts CSV file - text editor view*

.. image:: images/campaigns_contactdb_2.png

*Figure 5: Contacts CSV file - libreoffice excel view*

Se dispone entonces de una base de contactos (csv) para proceder con la carga del archivo en el sistema accediendo al punto de menú; *Contacts → New contacts database*

.. image:: images/campaigns_upload_contacts.png

*Figure 6: New contact database*

Se debe indicar con un check, cuales columnas son las que almacenan teléfonos, como se indica en la figura 7.

.. image:: images/campaigns_upload_contacts_2.png

*Figure 7: Tel check*

Finalmente se salva el archivo y el mismo queda disponible como una base de contactos del sistema instanciable por cualquier tipo de campaña.

Formularios
***********
Los formularios de campaña constituyen un elemento que permite recolectar información de la interacción con la persona detrás de la comunicación establecida.
Son diseñados dentro de OMniLeads conjugando en una vista estática diferentes tipos campos (texto, fecha, de multiple selección y área de texto).

Para crear formularios se debe acceder al punto de menú; *Campaigns → New form*. Allí

Los formularios pueden contener campos del tipo:

- **Texto**
- **Fecha**
- **Combo de selección múltiple**
- **Campo de complementarios**

En la figura 8 se ejemplifica un campo del tipo "combo" dentro de la creación de un formulario.

.. image:: images/campaigns_newform_1.png

*Figure 8: New campaign form*

Podemos generar un formulario de ejemplo de encuesta de satisfacción con el aspecto de la figura 9.

.. image:: images/campaigns_newform_2.png

*Figure 9: Survey campaign form*


Campañas VS Calificaciones VS Formularios
*****************************************

Para explicar la relación entre éstos componenetes, debemos recordar que múltiples formularios pueden ser asignados a una campaña. La idea es que diferentes calificaciones de una campaña
pueden disparar diferentes formularios, permitiendo así a la operación de recolectar mediante formularios previamentes diseñados, información asociada a la interacción entre el
agente de OMniLeads y la persona en el otro extremo de la comunicación dentro de la campaña.

Resulta importante explicar conceptualmrnte cómo se utilizan los formularios de campaña en OMniLeads. Antes que nada aclarar que en el marco de una campaña a la hora de asignar
calificaciones, se van a poder definir calificaciones normales y calificaciones "de gestión" o "engaged". Éstas últimas son las que disparan los formularios de campaña.


.. image:: images/campaigns_calldispositions_add.png

*Figure 10: Call dispositions inside campaign*

En el ejemplo de la figura 10, contamos con dos calificaciones del tipo engaged, por un lado la calificación "Survey on demand client"
que tiene asociado el formulario "Survey On Demand" y por el otro la calificación "Survey" que dispara el formulario "Survey Clients".

Siempre que haya una llamada activa entre un agente y un contacto de la base de la campaña, el agente dispone de los datos complementarios al teléfono del contacto en su pantalla
junto al combo de selección de calificación para el contacto actual. Si el agente selecciona y guarda una calificación del tipo "gestión", entonces se dispara en la pantalla de agente
el formulario asociado a la calificación dentro de la campaña.

.. image:: images/campaigns_dispositions_engaged.png

*Figure 11: Engaged dispostions and forms*

En el siguiente video ilustramos a los dos tipos de calificaciones y su comportamiento.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/320941143" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Interacción con un CRM externo
******************************
Esta funcionalidad permite lanzar una petición "HTTP - Get" utilizando datos de la llamada actual, desde OMniLeads hacia un CRM basado en tecnología web (requisito excluyente),
permitiendo así que cada agente del call center disponga automáticamente de una vista del contacto de la comunicación actual, sobre el CRM Web externo.

En cada llamada al CRM se pueden enviar datos de la llamada y el contacto como por ejemplo:

- El "path" de la grabación de la llamada.
- El "id" del agente.
- El "id" de la campaña.
- Cualquiera de las columnas de la base asociada a la campaña.

Entre otros parámetros.

Campañas Manuales
*****************

Dentro de este insiso se ejemplifica el paso a paso de cómo generar una campaña de llamadas manuales.

.. toctree::
 :maxdepth: 2

 campaigns_manual.rst


Campañas Preview
****************

En el siguiente video se expone paso a paso la creación y puesta en marcha de una campaña preview. Además se ejemplifica la operación del agente dentro de la misma.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/320950602" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Para profundizar en el asunto ingresar al link, donde se explica cada pantalla de configuración detalladamente.

.. toctree::
 :maxdepth: 2

 campaigns_preview.rst


Campañas con discador predictivo
********************************

.. toctree::
 :maxdepth: 2


 campaigns_dialer.rst


Campañas Entrantes
******************
En este capítulo se repasan todas las funcionalidades asociadas al tratamiento de llamadas entrantes.

En el siguiente video se expone paso a paso la creación y puesta en marcha de una campaña entrante.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/320941143" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


En este siguiente video se ejemplifica cómo configurar un PBX basado en Asterisk para derivar llamadas hacia campañas entrantes de OMniLeads, desde un IVR del PBX. Aunque la configuración expuesta también permite
derivar llamadas desde cualquier elemento del PBX, incluyendo las llamadas generadas o transferidas desde extensiones del PBX con destino en alguna campaña de OMniLeads.

.. raw:: html

        <iframe src="https://player.vimeo.com/video/320955286" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Para profundizar en cada una de las funcionalidaes pertinentes al mundo de las llamadas entrantes, se recomienda ingresar a cada uno de los links expuestos debajo.

.. toctree::
 :maxdepth: 2


 campaigns_inbound.rst
 campaigns_inbound_routes.rst
 campaigns_inbound_routes_frompbx.rst
 campaigns_inbound_ivr.rst
 campaigns_inbound_timeconditions.rst


Plantillas de Campaña
*********************

En muchas ocasiones los parámetros de una familia de campañas (por ejemeplo campañas preview de encuestas) no varían demasiado salvo por quizás por ejemplo el grupo de agentes asignados, la base de contactos a utilizar
o el supervisor agignado. Entonces en lugar de tener que crear campañas myu similares siempre de cero, se pueden utilizar las plantillas y clonar éstas con los parámetros listos para avanzar más rápidamente en la creación de la nueva campaña.

Esta funcionalidad la otorgan los *Templates* de campañas de OMniLeads.

A partir de generar un template (que se genera como una campaña), se pasa a disponer del mismo, de manera tal que simplemente seleccionando el template y la opción *Create campaign from template* se genera
una nueva campaña con todos los parámetros especificados en el template como configurados en la nueva campaña.


.. image:: images/campaigns_template.png

*Figure 13: templates*
