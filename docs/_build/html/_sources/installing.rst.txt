Installing OMniLeads
=====================

Install OMniLeads takes approximately 30-60 minutes to install.  The following video shows you the install process:

.. raw:: html

        <iframe src="https://player.vimeo.com/video/317503659" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>


Prerequisites:
^^^^^^^^^^^^^^

The platform is compatible and can be deployed over the following Operations Systems:

- GNU/Linux CentOS 7 (minimal)
- GNU/Linux Debian 9 (netinstall)
- Ubuntu Server 18.04
- The minimum disk space needed to install OML in any host is 20 GB
- git needs to be installed: yum install git -y (centos) or apt-get install git -y (ubuntu - debian)


Install Options
^^^^^^^^^^^^^^^^

- Proxy SIP Traffic Only (Don't Proxy audio (RTP) traffic)
- Proxy SIP Traffic and Audio when it detects a SIP Agent is behind NAT
- Proxy SIP Traffic, Audio and it configures the system to work properly when the PBX's and dSIPRouter are behind a NAT.

OS Support
^^^^^^^^^^

- **Debian Stretch (tested on 9.6)**
- **CentOS 7**

Kamailio will be automatically installed along with dSIPRouter.  Must be installed on a fresh install of Debian Stretch or CentOS 7.  You will not be prompted for any information.  It will take anywhere from 4-9 minutes to install - depending on the processing power of the machine. You can secure the Kamailio database after the installation.  Links to the installation documentation are below:

- :ref:`debian9-install`
- :ref:`centos7-install`
