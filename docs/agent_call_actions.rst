Llamadas hacia otros agentes
*****************************

Para ejecutar una llamada hacia otro agente de OMniLeads, debemos acudir al botón "Llamar fuera de campaña" disponible en la parte inferior del webphone.
Al hundir dicho botón se despliega una ventana que nos facilita la selección de un agente del listado total para luego ejecutar la llamada (Figura 1).

Llamadas externas sin campaña asociada
***************************************

A veces es necesario ejecutar una llamada hacia el exterior (número de abonado o extensión de la central PBX), sin la necesidad de gestionar el contacto,
sin más bien lanzar la llamada sin más. Esto se permite a partir de hundir el botón "Llamar fuera de campaña" disponible en la parte inferior del webphone.
La ventana desplegada cuenta con un campo para introducir el número a marcar (figura 1).


.. image:: images/about_agent_withoutcamp_calls.png

*Figure 1: without camp calls*

Poner en espera una llamada
***************************

En medio de cualquier tipo de llamada en curso, el agente puede poner en espera al teléfono en el otro extremo
de la comunicación. Esto se logra hundiendo el botón "hold" del webphone de agente.

.. image:: images/about_agent_callactions_hold_1.png

*Figure 2: call on hold*

Al disparar la acción de hold, el otro extremo de la llamada que escuchando la música de espera, mientras que el agente puede volver a retomar la llamada cuando desee
simplemente hundiendo el botón de unhold, tal como se indica en la figura 3.

.. image:: images/about_agent_callactions_hold_2.png

*Figure 3: unhold*

Esta funcionalidad puede ser utilizada en cualquier tipo de llamada.

Transferencias y conferencias
******************************

Dentro del abanico de posibilidades de transferencias de llamadas que se pueden realizar en el sistema, tenemos las siguientes:


**Transferencia directa hacia otro agente**

El "agente A" se encuentra en una llamada activa y desea transferir la llamada hacia el "agente B" de manera directa.
En este caso se hunde el botón de transferencia disponible en el webphone y luego se selecciona "blind transfer" como tipo de transferencia y se puede elegir al agente destino.

.. image:: images/about_agent_callactions_ag2ag_bt.png

*Figure 4: "Agent A" to "Agent B" blind transfer*

En este caso, la llamada automáticamente es despachada hacia el agente B, quedando liberado el webphone del "agente A". Una vez disparada esta transferencia, no se puede volver
a recuperar la llamada original, ni tampoco el "agente A" puede conocer si la llamada fue atendida o no por el "agente B"

**Transferencia directa hacia teléfono externo**

El "agente A" se encuentra en una llamada activa y desea transferir la llamada hacia un "Teléfono" externo a OMniLeads de manera directa. Cuando decimos externo, nos referimos
a una llamada que se genera hacia afuera del sistema, puede ser una extensión del PBX de la compañía o bien un teléfono externo de la PSTN.

En este caso se hunde el botón de transferencia disponible en el webphone y luego se selecciona "blind transfer" como tipo de transferencia y se debe introducir el número destino en recuadro
como lo indica la figura 5.

.. image:: images/about_agent_callactions_ag2out_bt.png

*Figure 5: "Agent A" to "External telephone" blind transfer*

En este caso, la llamada automáticamente es despachada hacia el teléfono destino, quedando liberado el webphone del "agente A". Una vez disparada esta transferencia, no se puede volver
a recuperar la llamada original, ni tampoco el "agente A" puede conocer si la llamada fue atendida o no por el teléfono destino de la transferencia.

**Transferencia con consulta hacia otro agente**

El "agente A" se encuentra en una llamada activa y desea transferir la llamada hacia el "agente B" de manera consultativa, es decir logrando que el teléfono externo quede
en espera mientras el "agente A" abre un nuevo canal hacia el "agente B", si la llamada entre ambos se establece y el "agente B" desea recibir la transferencia, entonces
el "agente A" corta la llamada y automáticamente el teléfono externo queda unido en una llamada con el "agente B".

.. image:: images/about_agent_callactions_ag2ag_ct.png

*Figure 6: "Agent A" to "Agent B" consultative transfer*

En este escenario también puede ocurrir:

-  Que no se logre contactar al "agente B", entonces el "agente A" puede cancelar la transferencia durante el ring hacia el "agente B" con el botón "cancel transfer" del webphone.


- Se logra el contacto con el "agente B" pero éste no pueda/quiera proceder con la transferencia, por lo tanto el "agente B" debe cortar la llamada y atomáticamente vuelve a quedar el "agente A" con el teléfono externo enlazados.


**Conferencia de a tres entre el número externo, agente A y agente B**

Este caso es un escenario posible dentro de una transferencia consultativa, ya que la acción a ejecutar por el agente que impulsa la conferencia "agente A", es en un principio
una transferencia consultativa, solo que al momento de entablar conversación del "agente A" hacia el "agente B" (mientras la persona externa "numero externo" se encuentra en espera)
el "agente A" debe hundir el botón de "Confer" disponible en el Webphone de agente y de esta manera quedan las tres partes en un salón de conferencia.


.. image:: images/about_agent_callactions_3way_confer_internal.png

*Figure 7: "Agent A", "Agent B" and External number three way conference*

**Transferencia con consulta hacia teléfono externo**

El "agente A" se encuentra en una llamada activa y desea transferir la llamada hacia un "teléfono" externo de manera consultativa, es decir logrando que "telefono externo A" quede
en espera mientras el "agente A" abre un nuevo canal hacia el "teléfono externo B", si la llamada entre ambos se establece y el "teléfono externo B" desea recibir la transferencia, entonces
el "agente A" corta la llamada y automáticamente el "teléfono externo A" queda unido en una llamada con el "teléfono externo B".


.. image:: images/about_agent_callactions_ag2out_ct.png

*Figure 8: "Agent A" to "External telephone" consultative transfer*

En este escenario también puede ocurrir:

-  Que no se logre contactar al "teléfono externo B", entonces el "agente A" puede cancelar la transferencia durante el ring hacia el "teléfono externo B" con el botón "cancel transfer" del webphone.


- Se logra el contacto con el "telefono externo B" pero éste no pueda/quiera proceder con la transferencia, por lo tanto el "teléfono externo B" debe cortar la llamada y atomáticamente vuelve a quedar el "agente A" con el "teléfono externo A" enlazados.


**Conferencia de a tres entre el número externo A, agente y un número externo B**

Bajo este escenario el "agente A" puede armar una conferencia de a tres entre el "número externo A", es decir la persona que inicialmente se encuentra
en llamada con "agente A" y un "numero externo B", que puede ser la extensión de un PBX o un abonado de la PSTN, de manera tal que queden las tres partes
en una sala de conferencias.

Para llevar a cabo esta acción, el "agente A" debe iniciar una *transferencia consultativa* hacia el "numero externo B" y una vez en llamada con éste último
el agente debe hundir el botón de "Confer" de su webphone (Figura 9).

.. image:: images/about_agent_callactions_3way_confer_out.png

*Figure 9: "Agent A", "Subscriber A" and "Subscriber B" three way conference*

.. image:: images/about_agent_callactions_3way_confer_switch.png

*Figure 10: Webphone confer switch*


**Transferencia a otra campaña**

Bajo este escenario el "agente A" se encuentra en una llamada activa y desea transferir la llamada hacia una campaña entrante. A la hora de seleccionar el tipo de transferencia
se debe marcar "blind transfer" ya que la llamada es lanzada sobre la cola de espera de la campaña destino.

.. image:: images/about_agent_callactions_ag2camp.png

*Figure 11: "Agent A" to "inbound campaign" transfer*

Como se trata de una transferencia directa, la llamada automáticamente es despachada hacia el teléfono destino, quedando liberado el webphone del "agente A". Una vez disparada esta transferencia, no se puede volver
a recuperar la llamada original, ni tampoco el "agente A" puede conocer si la llamada fue atendida o no


Observar grabación de llamada
*****************************

Esta funcionalidad del webphone de agente, permite a éste poder generar una marca sobre la grabación de la llamada. La idea es que luego desde el módulo de busqueda de grabaciones
se pueda recuperar grabaciones "observadas" por los agentes y allí también desplegar la observación que realizó el agente sobre la grabación de la llamada.

.. image:: images/about_agent_callactions_tag_call.png

*Figure 12: call recording tag*

Como se indica en la figura 12, luego de hundir el botón para marcar la llamada, se depliega un campo de texto para que el agente pueda describir la situación.

Finalmente en el módulo de grabación de OMniLeads, se puede recuperar dicha grabación y observar lo que el agente escribió al respecto.


Grabar llamada bajo demanda
***************************
Esta funcionalidad permite grabar una llamada, a partir del momento de hacer click en el botón que se muestra en la siguiente figura, la funcionalidad esta habilitada exclusivamente para llamadas pertecientes a campañas con la opción de realizar grabaciones desactivada.

.. image:: images/about_agent_callactions_record_call.png


Agendamiento de llamadas
************************

La funcionalidad de agendamiento de llamadas permite al sistema volver a procesar un contacto hacia el futuro. La idea es no descartar al mismo, sino seguirlo gestionando.

**Agendamiento personal:**

Cuando el agente requiere volver a llamar a un contacto determinado, puede generar un recordatorio en su agenda personal, para luego al listar dicha agenda contar con
la entrada que le recuerda el horario y contacto que debe llamar.

El agendamiento de llamadas es una calificación que se encuentra por defecto siempre como calificación de contacto.

.. image:: images/about_agent_callactions_agenda_1.png

*Figure 13: agenda personal*

Luego de guardar la calificación, se despliega un formulario para seleccionar la fecha, hora y motivo de la agenda personal del contacto.

.. image:: images/about_agent_callactions_agenda_2.png

*Figure 14: detalles de la agenda personal*

Finalmente, la entrada en la agenda personal del agente quedará disponible ingresando al punto de menú Agendas:

.. image:: images/about_agent_callactions_agenda_3.png

*Figure 15: detalles de la agenda personal*

**Agendamiento global de llamadas predictivas**

Este tipo de agendamiento es solo aplicable a campañas con discador predictivo ya que tiene como finalidad volver a colocar al contacto dentro de la lista de números
a llamar por el discador. En este escenario el discador simplemente vuelve a llamar a dicho número agendado hacia el final de la campaña, es decir no se puede elegir
ni una fecha u horario ni tampoco sobre qué agente va a caer el contacto llamado nuevamente por el discador.

Se trata de una funcionalidad que permite no descartar al contacto, pero sin implicar un seguimiento personal por parte del agente.

Para generar una agenda de este tipo, se debe calificar al contacto con la calificación "agenda" pero luego seleccionar "global" en el menú de selección del tipo de agenda.
