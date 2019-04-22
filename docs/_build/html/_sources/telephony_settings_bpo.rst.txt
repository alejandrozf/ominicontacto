Troncal SIP con proveedor de acceso PSTN
========================================
El esquema descripto en este insiso se puede representar con la figura 1.

.. image:: images/oml_bpo_simple.png
       :align: center

*Figure 1: SIP trunk provider and OMniLeads*

Vamos a considerar entonces que un proveedor de troncales SIP nos facilita un acceso a la PSTN. En este escenario se plantea una plantilla
de configuración muy similar a la siguiente.

Parámetros para el troncal SIP
******************************

::

  defaultuser=account_user
  secret=account_password
  host=XXX.XXX.XXX.PROVIDER
  context=from-pstn
  qualify=yes
  type=friend
  insecure=invite
  deny=0.0.0.0/0.0.0.0
  permit=XXX.XXX.XXX.PROVIDER/255.255.255.255

NOTA: ponemos énfasis en el parámetro "**context=from-pstn**". Es imprescindible que sea especificado.

Debemos recordar que la sintaxis utilizada para especificar los parámetros del troncal está basada en el módulo chan_sip.so de Asterisk.
Para mayor información sobre los parámetros `<https://www.voip-info.org/asterisk-config-sipconf/>`_

Una configuración ejemplar podría ser la de la figura 2.

.. image:: images/telephony_oml_siptrunk_provider.png
       :align: center

*Figure 2: SIP trunk provider config*

Comprobación del estado del troncal
***********************************

En este punto simplemente se accede por medio de una sesión SSH a OMniLeads y desde dicha conexión se debe ejecutar el comando de Asterisk

::

  asterisk -rx 'sip show peers'

Esto listará todos los *peers SIP* y su estado, como lo expone la figura 3.

.. image:: images/telephony_sipshowpeers.png

*Figure 3: SIP trunk check state*
