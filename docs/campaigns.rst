
********************
Campañas Telefónicas
********************

Una campaña representa una manera de encapsular (dentro de la plataforma) a una operación de Contact Center conformada por:


- Un grupo de agentes procesando llamadas en alguna dirección (outbound o inbound).
- Una base de contactos asociada a la campaña.
- Un listado de calificaciones disponibles a la hora de clasificar la llamada gestionada por el agente.
- Uno o varios formularios de campaña, a ser lanzados en caso de que el agente asigne una calificación de "gestión" sobre la llamada en curso. El formulario es desplegado por dicha calificación y el agente puede completar el mismo según los datos del contacto de la llamada en curso.

En la figura 1 se representa una campaña y sus componentes.

.. image:: images/campaigns_elements.png

*Figure 1: the campaigns elements*

El hecho de trabajar bajo campañas, permite a los perfiles de usuarios Supervisor/Administrador acotar métricas e informes,
así como también realizar monitoreo en tiempo real o buscar grabaciones, entre otras acciones, utilizando campañas como criterio de filtrado.
Podemos contar con diferentes campañas de diferente naturaleza (predictivas, preview, entrantes o manuales), conviviendo de manera simultánea en OMniLeads y dejando
registros sobre las llamadas transaccionadas por los agentes.


.. image:: images/oml_bpo.png

*Figure 2: Campaigns, agents, supervisors and backoffice*


Calificaciones
**************

Las calificaciones constituyen un listado de "etiquetas" disponibles para ser asignadas a cualquier campaña, de manera tal que los agentes puedan clasificar cada llamada
dentro de una campaña, con cualquiera de éstas calificaciones.

Las calificaciones son generadas por el supervisor o administrador y se pueden relacionar con varios aspectos, por ejemplo:

- El resultado de la llamada hacia un contacto de la campaña (ocupado, no atendió, numero equivocado, buzón de mensajes, etc.)
- El resultado asociado a una llamada atendida (interesado, no interesado, venta, encuesta realizada, etc.)

Las calificaciones pueden ser totalmente arbitrarias y para generarlas se debe ingresar al punto de menú; *Campaigns → Call Dispositions → New Call Dispositions*.

Podemos listar las calificaciones generadas dentro de *Campaigns → Call Dispositions → Call Dispositions*

.. image:: images/campaigns_calldispositions.png

*Figure 3: Call dispositions*

Base de contactos
*****************
Las bases de contactos son utilizadas en las campañas salientes aunque también pueden ser utilizadas por campañas entrantes. En el marco de las campañas salientes,
los datos que requiere el discador predictivo o preview son proporcionados por la base de contactos afectada a la campaña, mientras que en las campañas entrantes
aportan los datos complementarios al número telefónico que son desplegados en la pantalla del agente cada vez que ingresa una llamada por una campaña entrante.

Éstas bases son proporcionadas en archivos con formato CSV con los campos separados con coma y además generadas en la codificacipón UTF-8 (requisito excluyente).
Debe existir al menos una columna que contenga un teléfono por cada contacto (registro) del archivo, el resto de las columnas puede contener cualquier contenido,
generalmente cada registro cuenta con datos complementarios al teléfono principal. Éstos datos son expuestos en la pantalla de agente a la hora de establecer
una comunicación entre ambos (agente y contacto de la base).

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
Los formularios de campaña constituyen el método por defecto para recolectar información (relevante para la campaña) en la interacción con la persona detrás
de una comunicación establecida.
Son diseñados por el usuario combinando en una vista estática diferentes tipos campos (texto, fecha, de multiple selección y área de texto), pudiendo ordenar
los mismos de acuerdo a la necesidad de la campaña.

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


Campañas, Calificaciones & Formularios
*****************************************

Para explicar la relación entre éstos componentes, debemos recordar que múltiples formularios pueden ser asignados a una campaña. La idea es que diferentes calificaciones de una campaña
pueden disparar diferentes formularios, permitiendo así a la operación de recolectar mediante formularios previamentes diseñados, información asociada a la interacción entre el
agente de OMniLeads y la persona en el otro extremo de la comunicación dentro de la campaña.

Resulta importante explicar conceptualmente cómo se utilizan los formularios de campaña en OMniLeads. Antes que nada aclarar que en el marco de una campaña a la hora de asignar
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


Campañas Manuales
*****************

Dentro de este inciso se ejemplifica el paso a paso de cómo administrar campañas manuales.

.. toctree::
  :maxdepth: 2

  campaigns_manual.rst


Campañas Preview
****************

Dentro de este inciso se ejemplifica el paso a paso de cómo administrar campañas preview

.. toctree::
  :maxdepth: 2

  campaigns_preview.rst

Campañas con discador predictivo
********************************

Dentro de este inciso se ejemplifica el paso a paso de cómo administrar campañas dialer.

.. toctree::
  :maxdepth: 2

  campaigns_dialer.rst

Campañas Entrantes
******************

Al hablar de llamadas entrantes nos toca desplegar cada funcionalidad aplicable al flujo de llamadas entrantes, como bien sabemos una llamada entrante
puede pasar por una serie "nodos" hasta finalmente conectar con un agente de atención. Por lo tanto vamos a ampliar el concepto de "campañas entrantes"
a los siguientes ítems de configuración.

.. toctree::
  :maxdepth: 1

  campaigns_inbound.rst
  campaigns_inbound_routes.rst
  campaigns_inbound_routes_frompbx.rst
  campaigns_inbound_timeconditions.rst
  campaigns_inbound_ivr.rst
  campaigns_inbound_customer_id.rst
  telephony_cunstom_dst.rst

Plantillas de Campaña
*********************

Suele ser recurrente que los parámetros de una "clase" de campañas (por ejemeplo campañas preview de encuestas) no varíen demasiado salvo quizás por
el grupo de agentes asignados, la base de contactos a utilizar o el supervisor agignado. Por lo tanto en lugar de tener que crear campañas muy similares siempre
desde cero, se pueden generar plantillas para luego crear campañas nuevas rápidamente a partir de clonar dichas plantillas.


Esta funcionalidad la otorgan los *Templates* de campañas de OMniLeads.

A partir de la generación de una plantilla (que se genera de manera similar a una campaña), se pueden crear nuevas campañas simplemente seleccionando el template y
la opción *Create campaign from template*. Cada nueva campaña estará disponible con todos los parámetros especificados en su plantilla matriz.


.. image:: images/campaigns_template.png

*Figure 13: templates*

Interacción con sistemas de gestión externos
***********************************************

OMniLeads está diseñado desde una perspectiva en la que se prioriza una integración con el sistema de gestión predilecto de la compañía. Brindando así la posibilidad
de que una empresa mantenga el uso de su sistema de gestión apropiado a su mercado vertical (salud, ventas, atención al cliente, etc.).

Mediante funcionalidades propias y métodos de la API, OMniLeads permite los siguientes interacciones:


* Abrir una vista concreta del CRM en una comunicación entrante o saliente, utilizando parámetros de la comunicación (id del agente, id del contacto, id de la campaña, etc.) como información dinámica para invocar al CRM.
* Permitir realizar una llamada "click to call" desde una vista de contacto en el CRM y accionar así una llamada a través de una campaña y agente de OMniLeads.
* Permitir calificar la gestión de un contacto del CRM y que la calificación se impacte en OMniLeads, de manera tal que exista una correlación entre el sistema CRM y el sistema de Contact Center dentro de cada campaña.
* OMniLeads en las llamadas entrantes puede solicitar el ID del llamante y notificar al CRM para que éste decida sobre que campaña de OMniLeads encaminar una llamada.

Ampliamos todos estos conceptos y configuraciones en el siguiente link :ref:`about_crm`.
