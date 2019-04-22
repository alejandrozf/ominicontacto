Installing OMniLeads
=====================

Install OMniLeads takes approximately 30-60 minutes to install.  The following video shows you the install process:

.. raw:: html

        <iframe src="https://player.vimeo.com/video/317503659" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Prerequisites:
^^^^^^^^^^^^^^

The platform is compatible and can be deployed over the following Operations Systems:

- GNU/Linux CentOS 7 (minimal), Debian 9 (netinstall) & Ubuntu Server 18.04
- The minimum disk space needed to install OML in any host is 20 GB
- Git package needs to be installed
Ubuntu - Debian:
::

  apt install git
|

CentOS:
::

  yum install git
|

- Remember to check and correct (if  necessary) the server’s date and time
- Remember to check and correct (if  necessary) the server’s hostname and ip address


Install Options
^^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 2

   install_self_hosted.rst
   install_remote_ansible.rst
   install_cluster.rst
