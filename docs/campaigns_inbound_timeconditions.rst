.. _about_timeconditions:

**********************************************
Enrutamiento condicionado por rango de tiempo
**********************************************

En esta sección se trabaja con el concepto de *Enrutamiento de llamadas entrantes condicionado por rango de tiempo*, para configurar el flujo de llamadas
entrantes hacia diferentes destinos internos a partir de comparar la fecha/hora en que llega una llamada y un patrón (de fechas y horas) relacionado,
de manera tal que se pueda planificar de antemano si una llamada debe ir hacia un destino u otro de acuerdo al resultado de dicha comparación.

Por ejemplo una llamada podria ir hacia una campaña entrante *dentro del rango de fecha y horario de atención al cliente* y hacia un IVR que reproduzca
un anuncio acerca de los horarios de atención, cuando la llamada ingrese fuera de ese rango definido.

.. image:: images/campaigns_in_tc_diagrama.png

*Figure 1: Time conditions*

Existen dos módulos que trabajan en conjunto y que permiten implementar este tipo de configuraciones.

Grupos horarios
****************

Este módulo permite agrupar patrones de fechas y horas como un objeto, para luego puede ser invocados por los objetos del tipo condicionales de tiempo.

Para definir o editar grupos de horarios, se debe acceder al punto de menú **Telefonía -> Grupos horarios**. Para añadir un nuevo grupo se debe presionar
el botón "Agregar nuevo grupo".

La pantalla de grupos horarios se expone en la figura 2.

.. image:: images/campaigns_in_tc1.png

*Figure 2: Time groups*

Una vez generados los *Grupos de tiempos* podemos invocarlos desde el módulo complementario *Condicionales de tiempos*

Validación de tiempo
**********************

Este módulo permite comparar la fecha y hora en el momento de procesar una llamada, con un grupo horario asignado como patrón de comparación.
Luego en base a la coincidencia o no con alguna franja de fecha/hora del grupo, la llamada se envía hacia el destino positivo o negativo de la comparación.

Un *nodo* condicional de esta clase puede ser invocado por otros nodos:

- rutas entrantes
- opción de IVR
- failover de una campaña entrante
- otro condicional de tiempo

Para generar un elemento Condicional de tiempo, se debe acceder a **Telephony -> Time conditions**

La pantalla de configuración es similar a la figura 3.

.. image:: images/campaigns_in_tc2.png

*Figure 3: Time conditions*

Finalmente tenemos disponible este elemento de enrutamiento para ser utilizado por ejemple como destino de una ruta entrante.
