.. _about_api_agent_session:

***********************************
API de sesión de Agente en Asterisk
***********************************

Endpoints para controlar la sesion del agente en Asterisk para el uso del Webphone


Inicio de sesión de agente en Asterisk
**************************************

Establece el estado de sesión del Agente (:ref:`about_agent_user`) en Asterisk como iniciada. Las credenciales deberán pertenecer al Agente, y no hace falta enviar ningún parámetro extra.

**URL**: POST https://<omnileads_addr>/api/v1/asterisk_login/

Cierre de sesión de agente en Asterisk
**************************************

Establece el estado de sesión del Agente (:ref:`about_agent_user`) en Asterisk como finalizada. Las credenciales deberán pertenecer al Agente, y no hace falta enviar ningún parámetro extra.

**URL**: POST https://<omnileads_addr>/api/v1/asterisk_logout/

Ingreso en pausa de agente
**************************

Establece el estado de sesión del Agente (:ref:`about_agent_user`) en Asterisk como en Pausa (:ref:`about_agent_session_pause`). Las credenciales deberán pertenecer al Agente.

**URL**: POST https://<omnileads_addr>/api/v1/asterisk_pause/

+---------------------+---------+---------------------------------------------------------------------------+
| field name          | type    | description                                                               |
+=====================+=========+===========================================================================+
| pause_id            | string  | Id de la pausa en la que entra el Agente.                                 |
+---------------------+---------+---------------------------------------------------------------------------+

Salida de pausa de agente
*************************


Establece el estado de sesión del Agente (:ref:`about_agent_user`) en Asterisk como "Disponible" e indica ela finalizacion de una Pausa (:ref:`about_agent_session_pause`). Las credenciales deberán pertenecer al Agente.

**URL**: POST https://<omnileads_addr>/api/v1/asterisk_unpause/

+---------------------+---------+---------------------------------------------------------------------------+
| field name          | type    | description                                                               |
+=====================+=========+===========================================================================+
| pause_id            | string  | Id de la pausa de la que sale el Agente.                                  |
+---------------------+---------+---------------------------------------------------------------------------+
