*****************
Preview Campaigns
*****************

Para crear una nueva campaña preview se debe ingresar al punto de menú *Campaigns -> New  Campaign*. El proceso de creación consta de
un wizard de dos pantallas.

La primera pantalla nos invita a indicar una serie de parámtros de la campaña, como lo indica la figura 1.

.. image:: images/campaigns_prev_wizard_1.png

*Figure 1: Campaigns parameters*


- **Name:** nombre de la campaña
- **Contact database:** la base de contactos que utilzará el discador preview a la hora de entregar llamadas a los agentes
- **Tipo interacción:** aquí se selecciona si la campaña va a operar con un formulario o solamente utilizando un llamo a un CRM externo Web".
- **External URL:** URL a disparar cada vez que el agente lo indique.
- **Enable recordings:** habilitar que todas las llamadas de la campaña sean grabadas.
- **Scope:** se define como la cantidad de gestiones positivas que se esperan para la campaña. En la supervisión de la campaña se muestra en tiempo real el porcentaje de avence de la campaña respecto al objetivo definido.
- **Disconection time:** es el tiempo que el discador preview reserva un contacto a un agente, hasta ser liberado de manera tal que pueda ser demandado por otro agente.

En la segunda pantalla se deben asignar las calificaciones que se requieran como disponibles para los agentes a la hora de clasificar cada llamada de cada contacto.

.. image:: images/campaigns_prev_wizard_2.png

*Figure 2: Call dispositions*

Luego resta asignar a los supervisores y agentes que podrán trabajar en la misma.
En la figura 3 y 4 se ejemplifica una asignación de agentes a una campaña.

.. image:: images/campaigns_prev_wizard_3.png

*Figure 3: supervisor assignment*


.. image:: images/campaigns_prev_wizard_4.png

*Figure 4: agent assignment*

Finalmente nuestra campañas queda disponible para comenzar a operar. Por lo tanto cuando los agentes asignados a la misma realicen un login a la plataforma, deberían
disponer de la campaña preview tal como se expone en la figura 5.


.. image:: images/campaigns_prev_agconsole1.png

*Figure 5: Preview agents view*

Si el agente hace click sobre el teléfono entonces se dispara la llamada, se visualizan los datos (extras al teléfono) del contacto llamado, en la vista de agente
y permitiendo a su vez al agente clasificar la llamada con alguna de las calificaciones asignadas a la campaña.


.. image:: images/campaigns_prev_agconsole2.png

*Figure 6: Contact called*

**Campaña con base de datos Multinum**

Como sabemos, OMniLeads admite que cada contacto de una base posea "n" números de teléfono de contacto, de manera tal que si el contacto no es encontrado en su número principal
(el primero de nuestro archivo CSV de base), pueda ser contactado a los demás números. En este caso, cada número de teléfono (que indicamos en la carga de la base) se genera
como un link dentro de los datos del contacto presentados sobre la pantalla de agente. Al hacer click sobre dicho link, se dispara una llamada hacia ekl número de teléfono extra
del contacto. En la figura 7 se muestra dicho escenario.

.. image:: images/campaigns_prev_agconsole3.png

*Figure 7: Multinum contact database*

Por lo tanto, el agente puede intentar contactar a todos los números disponibles como "link" en la ficha del contacto, hasta finalmente calificar y pasar a uno nuevo.
