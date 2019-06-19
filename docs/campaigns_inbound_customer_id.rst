.. _about_customer_id:


****************************************************
Enrutamiento por identificación de llamada entrante
****************************************************

**INTRODUCCIÓN**

Esta funcionalidad es un posible nodo dentro del "flow" de la llamada entrante, que permite lanzar una "solicitud de identificación" sobre cada
llamada entrante derivada implementando a su vez la posibilidad de que el sistema de gestión CRM tome la decisión de encaminamiento de las
llamadas entrantes provenientes del exterior a través de una interacción entre OMniLeads y dicho sistema de gestión.

En su funcionalidad más básica el módulo implementa la posibilidad de solicitar la identificación de un cliente que se ha comunicado a
la compañía a través de los tonos del teléfono (DTMF) y si la misma es válida entonces encaminar la llamada hacia un destino concreto, mientras que sino lo es, rumbo hacia otro destino indicado.

En ambos escenarios (el más básico y el interactivo con CRM), se consigue que la llamada ingrese al Agente con el "ID del cliente" como
índice para obtener toda la información del cliente sobre el Formulario o CRM implicado en la campaña.


Modos de configuración
************************

El módulo viene disponible para ser configurado en distintos modos de funcionamiento;

* **Solamente solicitar identificación**

Bajo esta configuración cuando una llamada entrante es enviada hacia este módulo, se ejecuta una solicitud de identificación a través de un
audio reproducido sobre el canal telefónico del cliente que originó la llamada para luego validar la credencial ingresada y tomar una decisión
de encaminamiento hacia las dos alternativas posibles; "destino  A", si se ha ingresado una identificación y "destino B" si el llamante no lo hizo
o lo hizo de manera errática.

.. image:: images/customer_id_mode_1.png

*Figure 1: Customer id without CRM interaction*


* **Solicitar identificación, notificar al CRM y aguardar respuesta "true / false"**

Bajo esta configuración cuando una llamada entrante es enviada hacia este módulo, se ejecuta una solicitud de identificación a través de un
audio reproducido sobre el canal telefónico del cliente que originó la llamada para luego ejecutar una consulta hacia un servicio web
previamente configurado.

.. image:: images/customer_id_mode_2.png

*Figure 2: Customer id with CRM interaction true/false*

El sistema de gestión CRM toma partido respecto al encaminamiento de un cliente que se comunica a la compañía, ya que a partir de recibir
desde OMniLeads la clave de identificación del llamante, se pueden encaminar las llamadas hacia cada uno de los dos posibles destinos posibles
de acuerdo a lo que se responda (true/false) a dicha credencial recibida.

Un ejemplo podría ser el de una compañía que comprueba si el "número de cliente" se encuentra al día con los pagos del servicio y en base a ello
encaminar la llamada hacia una campaña con mayor o menor prioridad en términos de tiempo en cola de espera.


* **Solicitar identificación, notificar al CRM y aguardar respuesta "destino de la llamada"**

Bajo este modo, cuando una llamada entrante invoca la ejecución del módulo, éste último procede con la solicitud de identificación para luego
validar si el cliente ingresó o no un valor, en caso de haber ingresado se ejecuta una consulta hacia un servicio web previamente configurado.

.. image:: images/customer_id_mode_3.png

*Figure 3: Customer id with interaction and destination chosen by CRM*

El sistema de gestión CRM toma partido respecto al encaminamiento de un cliente que se comunica a la compañía, ya que a partir de recibir
de OMniLeads en tiempo real la clave de identificación del llamante, puede encaminar las llamadas hacia cualquier destino (o nodo) de OMniLeads
siendo posibles una campaña entrante, un IVR, una validación de tiempo, etc.

Un ejemplo aplicación podría ser comprobar en base al "número de cliente" que plan de suscripción tiene contratado, que plan de salud, etc. y en base a
ello encaminar la llamada hacia la campaña en OMniLeads que mejor se ajuste.


.. _about_customer_id_form:

Crear un nuevo punto de solicitud de identificación de clientes
*****************************************************************

Para generar un nuevo nodo, se debe acceder al punto de menú: "Telefonía - Identificación de clientes"

.. image:: images/customer_id_mode_form.png

*Figure 4: New customer id node*

A continuación se detallan los campos del formulario:

+----------------------+------------------------------------------------------------------------------------------------+
| Campo                | Descripción                                                                                    |
+======================+================================================================================================+
|Nombre                | Nombre de referencia del nodo                                                                  |
+----------------------+------------------------------------------------------------------------------------------------+
|Tipo de interacción   | * Sin Interacción: solo se comprueba si hubo o no un ingreso y su logitud                      |
|                      | * Interacción externa tipo 1: se envía id de cliente y se espera "true/false" como respuesta   |
|                      | * Interacción externa tipo 2:se envía id de cliente y se espera un destino como respuesta      |
+----------------------+------------------------------------------------------------------------------------------------+
|URL servicio ident    | Aquí se indica la dirección del servicio web hacia donde enviar el número de identificación    |
+----------------------+------------------------------------------------------------------------------------------------+
|Audio                 | Se trata del audio que se reproduce sobre la llamada entrantes, para solicitar                 |
|                      | la identificación                                                                              |
+----------------------+------------------------------------------------------------------------------------------------+
|Logitud id esperado   | Se puede indicar el largo esperado de código de identificación                                 |
+----------------------+------------------------------------------------------------------------------------------------+
|Timeout               | El tiempo en segudos que el sistema espera a que se ingrese la identificación, en caso de      |
|                      | exirar este tiempo, se comprueba si ya se han sobrepasados los re-intentos para en base a ello |
|                      | ejecutar una nueva petición o derivar la llamada hacia el destino no exitoso                   |
+----------------------+------------------------------------------------------------------------------------------------+
|Intentos              | Cantidad de intentos no efectivos de autenticación                                             |
+----------------------+------------------------------------------------------------------------------------------------+
|Destino Identificación| Tipo de destino y destino puntual para dicho tipo al que se derivan las llamadas "positivas"   |
|exitosa               | en los tipo de interacción "sin interacción" e "interacción tipo 1"                            |
+----------------------+------------------------------------------------------------------------------------------------+
|Destino Identificación| Tipo de destino y destino puntual para dicho tipo al que se derivan las llamadas "negativas"   |
|no exitosa            | en los tipo de interacción "sin interacción" e "interacción tipo 1"                            |
|                      |                                                                                                |
+----------------------+------------------------------------------------------------------------------------------------+

.. important::

  Para poder implementar los modos que implican enviar la identificación hacia un servicio web externo, aguardando una respuesta
  del mismo para luego ejecutar el encaminamiento de la llamada, depende de que el sistema de gestión implemente un servicio web
  para recibir las peticiones de este tipo.


  Para los desarrolladores que deseen habilitar en el sistema de gestión este tipo de interacción, pueden encontrar formato en que OMniLeads
  envía la identificación hacia el servicio web se encuentra dentro de la sección  :ref:`about_customer_id_request`.
