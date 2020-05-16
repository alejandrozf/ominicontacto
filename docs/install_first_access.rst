.. _about_first_access:

Primer acceso a OMniLeads
^^^^^^^^^^^^^^^^^^^^^^^^^^

Para acceder al sistema OMniLeads debe ingresar a:

https://omnileads-hostname

Nota: El acceso web a OMniLeads debe ser a través del hostname.domain del host. Por lo tanto existen dos posibilidades a la hora de resolver el
hostname:

1 - Que los DNS de la red lo hagan.
2 - Añadir el hostname.domain del host, dentro del archivo de *hosts* (Windows, Linux o Mac de cada PC que tenga que acceder a OMniLeads.

.. image:: images/install_dns_hosts.png

*Figure 1: hosts file*

Al encontrarnos con la pantalla de login, simplemente se debe ingresar el usuario admin y la clave generada durante la instalación, como se expone en la figura 2.

.. image:: images/install_1st_login.png

*Figure 2: First login*

.. note::

  Si no recuerda la contraseña de admin web, podemos consultar su valor :ref:`about_maintance_envvars`.

.. important::

    Si realizó **instalación con Docker** se usa el puerto 444 para el acceso web, ejemplo:
    
    * https://omnileads-hostname:444

    Esto es con el fin de que no conflictue con el clásico 443 que ya lo usan la web de FreePBX o Issabel