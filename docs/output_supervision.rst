Supervision
***********

Este módulo permite visualizar el estado de las campañas entrantes, campañas salientes (Manual, Dialer y Preview) y agentes.

.. image:: images/output_supervision_options.png

*Figure 1: Choices for supervision*

* **Agentes:**

En la sección de agentes se observan todos los agentes logueados en el sistema y el estado en el que se encuentran (READY, OnCall, Paused, Dialing, Offline) .

.. important::

  * Un agente debe estar asignado al menos a una campaña para que aparezca en este módulo
  * Luego de unos segundos un agente en estad Offline desaparece de la vista de agentes y vuelve a aparecer al reloguearse

.. image:: images/output_supervision_agentes.png

*Figure2: View of realtime supervision*

Un supervisor puede tomar acciones sobre cada agente. Para ello son los cuatro botones que aparecen al lado del estado. A continuación se describe la función de cada uno (de izquierda a derecha):

  - **Espiar:** el supervisor escucha la **llamada activa** entre agente y cliente. Hacer click en el botón *Finalizar* para terminar de escuchar, en cualquier momento
  - **Espiar y susurrar:** el supervisor puede hablar al agente sin que el cliente lo perciba, durante una **llamada activa**. Hacer click en el botón *Finalizar* para terminar de escuchar, en cualquier momento
  - **Pausar agente:** suponiendo que el agente se fue a break y se le olvidó ponerse en pausa, el supervisor puede con este botón inducir una pausa para que no reciba llamadas. Puede despausar oprimiendo nuevamente este botón.
  - **Desloguear agente:** suponiendo que el agente terminó su sesión y no se deslogueó correctamente del sistema (no presionó su nombre y dió click en salir, extremo derecho superior de la consola de agente), el supervisor puede desloguear al agente con este botón. Es importante hacer este proceso para no tener tiempos de sesión incoherentes en el reporte de agentes.

.. note::

   El supervisor cuenta con un pequeño webphone. Para poder hacer estas acciones es necesario que aparezca el mensaje de **Supervisor Registrado**.

* **Campañas entrantes:**

Esta vista muestra como van la campañas entrantes en cuanto número de llamadas recibidas, atendidas, abandonadas, expiradas y cuantas gestiones se han hecho en el día:

.. image:: images/output_supervision_camp_entrantes.png

*Figure3: view of realtime inbound campaigns*

* **Campañas salientes:**

Esta vista muestra el total de atendidas, no atendidas y cuantas gestiones se han hecho de las campañas salientes, en el día.

.. image:: images/output_supervision_camp_salientes.png

*Figure4: view of realtime outbound campaigns*

.. note::

   Se entiende por día el día a dia de operación desde las 00:00 hasta las 23:59. En el siguiente día las estadísticas de campañas entrantes y salientes se resetean.
