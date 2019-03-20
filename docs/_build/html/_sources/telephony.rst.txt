*********************************
Configuración de acceso a la PSTN
*********************************

En este capítulo vamos a explicar cómo dejar la capa de *troncalización PSTN* de OMniLeads lista para operar de acuerdo a los contextos planteados.
OMniLeads admite solamente SIP como tecnología de interconexión con otros conmutadores de telefonía.

Explicación del ABM de troncales
********************************

Para acceder a la configuración de los troncales debemos ingresar en el punto de menú *(Telephony -> SIP Trunks)* y allí añadir un nuevo
troncal SIP. Se va a desplegar un formulario similar al de la figura 1.

.. image:: images/telephony_siptrunk_view.png
       :align: center

*Figure 1: New SIP Trunk*

Los campos del formulario son:

- **Name**: el nombre del troncal. Debe ser alfanumperico sin espacios ni caracteres especiales (Ej: Trunk_provider_a).
- **Number of channels**: es la cantidad de canales que permite el vínculo.
- **Caller id**: el número con el que saldrán las llamadas por el troncal.
- **Register string**: se trata de la cadena de registro. En el caso de que el otro extremo del troncal solicite una registración, aquí es donde se debe configurar. (Ej: *username:password@address-domain:port*)
- **Text config**: en este campo de texto se proporciona los parámetros SIP en sintaxis de chan_sip.so de Asterisk.

A continuación se presentan los tipos de escenarios planteados como caso de uso de OMniLeads.


Troncal SIP entre OMniLeads y un sistema PBX
********************************************

Esta sección apunta al caso de uso "OMniLeads como Plataforma de Contact Center integrado a un PBX basado en SIP".
Por lo tanto se plantea una configuración en la cual OMniLeads interactúa con la PSTN a través de un troncal SIP establecido con un
sistema PBX siendo éste último quien está vinculado directamente con el acceso a la PSTN. Además el vínculo SIP mencionado es funcional al flujo de llamadas entre los agentes de OMniLeads y los recursos internos
del PBX (extensiones, colas, salas de conferencias, ertc.), así como también desde los recursos del PBX hacia los de OMniLeads.


  .. toctree::
   :maxdepth: 2

   telephony_settings_pbx.rst


Troncal SIP entre OMniLeads y un proveedor de acceso a la PSTN
***************************************************************

Dentro de ésta sección se expone la configuración de un proveedor que nos brinda acceso a la PSTN a través de un troncal SIP. De esta manera nuestra instancia de OMniLeads podrá interactuar con abonados de la PSTN ya sea enviando llamadas o recibiendo llamadas.

     .. toctree::
      :maxdepth: 2

      telephony_settings_bpo.rst



Configuración de enrutamiento de llamadas salientes
***************************************************

OMniLeads permite gestionar el enrutamiento de llamadas salientes sobre múltiples troncales SIP (previamente creados), de manera tal que
utilizando criterios como el *largo o prefijo del número* para determinar por qué vínculo SIP encaminar la llamada. Además es posible mantener una lógica de *failover*
en término de troncales SIP.

Para acceder al ABM de rutas salientes ingresar al punto de menú (*Telephony -> Outbound routes*)

.. image:: images/telephony_outr.png

*Figure 2: Outbound route*

- Nombre: es el nombre de la ruta (alfanumérico sin espacios)
- Ring time: es el tiempo (en segundos) que las llamadas cursadas por esta ruta, intentarán establecer una conexión con el destino, antes de seguir intentando por el próximo troncal o bien descartar la llamada.
- Dial options: son las opciones de la aplicación "Dial" utilizadas por Asterisk(r) en bajo nivel.
- Patrones de discado: mediante patrones, se puede representar los “tipos de llamadas” que serán aceptados por la ruta para enviarlos al destino por el Trunk SIP.

Para comprender cómo se representan los dígitos con patrones, se recomienda leer éste link: https://www.voip-info.org/asterisk-extension-matching/.

Dentro de cada patrón ingresado hay tres campos:


  * Prepend: son los dígitos que se mandan por el trunk SIP como adicionales al número discado. Es decir llegan al Trunk posicionados delante del número marcado.
  * Prefijo: son los dígitos que pueden venir como “prefijo” de una llamada marcada y éstos serán quitados en el momento de enviarlos por el SIP Trunk.
  * Patrón de discado: se busca representar en este campo el patrón de dígitos autorizados que la ruta va a procesar para y enviar a un SIP Trunk para sacar la llamada hacia el exterior.

- Secuencia de troncales: son los troncales SIP sobre los cuales la ruta saliente va a intentar establecer la llamada discada por OML. Si la llamada falla en un troncal, se sigue intentando en el siguiente.
