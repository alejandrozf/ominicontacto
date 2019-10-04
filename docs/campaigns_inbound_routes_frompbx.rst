.. _about_inboundroutespbx:

***************************************************************
Derivación de llamadas entrantes desde la PBX hacia OMniLeads
***************************************************************

En esta sección se ejemplifica cómo configurar OMniLeads y un PBX basado en Asterisk, para derivar llamadas desde el PBX hacia OMniLeads.

.. image:: images/campaigns_in_route_frompbx_ivr.png

*Figure 1: Inbound route parameters*

Partimos del hecho de considerar que existe un troncal SIP que vincula OMniLeads con la centralita PBX.

Lo primero que se debe definir es la numeración asignada a la ruta entrante que va a procesar la llamada desde el PBX hacia un destino de OMniLeads, ya que este número
(DID de la ruta) debe ser marcado por la PBX para enviar llamadas desde cualquier módulo (extensiones, IVRs, Inbound routes, followme) de dicho PBX, hacia el destino
configurado en la ruta de OMniLeads.

.. image:: images/campaigns_in_route_frompbx.png

*Figure 2: Inbound route parameters*

Tomando como ejemplo la ruta con el DID *123456* utilizado en la figura anterior, la centralita PBX Asteisk deberá generar llamadas por el SIP trunk
hacia el número mencionado, cada vez que algún recurso de la PBX necesite alcanzar el destino *123456* de OMniLeads.

Si nuestro PBX Asterisk dispone de una interfaz web de configuración entonces simplemente puedo generar una *Nueva extensión custom* y hacer que la misma apunte a;
*SIP/trunkomnileads/123456* , donde *trunkomnileads* es el nombre configurado en la PBX, para nombrar el troncal SIP con OMniLeads.

La idea de extensión apuntando hacia OMniLeads se ejemplifica en la figura 3 y 4.

.. image:: images/campaigns_in_route_frompbx2.png


*Figure 3: OMniLeads PBX custom extension*

Si bien la extension en el PBX puede tener cualquier numeración (se ejemplificó con *2222*), lo importante es enviar *123456* (en nuestro ejemplo) hacia OMniLeads
como se resalta en la figura 4.

.. image:: images/campaigns_in_route_frompbx3.png

*Figure 4: OMniLeads PBX custom extension*

Una vez disponible la extension en el PBX, solo es cuestión de invocarla desde cualqueir módulo de la centralita PBX, como por ejemplo un IVR.

.. image:: images/campaigns_in_route_frompbx4.png

*Figure 5: from IVR to OMniLeads*

Si bien en la figura 5 se ejemplifica la derivación de llamadas hacia campañas entrantes de OMniLeads desde un IVR de la centralita PBX.
Podemos concluir en que también las extensiones de la PBX pueden marcar o transferir llamadas hacia OMniLeads, así como también módulos de la PBX como Condiciones horarias,
followme, inbound routes, etc. podrán invocar una *extensión custom* de la PBX que derive llamadas hacia OMniLeads.
