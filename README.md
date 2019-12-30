What is OMniLeads (OML)?

OMniLeads (OML) is an Open Source software solution based on WebRTC technology(https://webrtc.org/) designed to support the management, operation and administration of a Contact Center using multiple comunication channels. At present it allows the management and phone attention deployment using: Inbound Campaigns, Preview Campaigns and Manual Outbound Campaigns natively. Also it have with the option to administrate Predictive/Progressive Dialer Campaigns using integrations APIs.

As part of the roadmap of the develop we are planning to include SMS Send/Reception, Social Networks integration and Chat Campaigns from the web page, IVR Campaigns (press one) and many other features

El system requires only the GNU/Linux OS distributions described in the installation manuals.

Features
    •    Agente & Supervisor console based on WebRTC
    •    Differents user profiles: administrator, supervisor admin, supervisor client, agent
    •    Multiple campaigns management
    •    Answering machine detection
    •    Full Recording
    •    Productivity reports
    •    Real time supervision
    •    Simple creation of Web forms
    •    CRM/ERP integration APIs
    •    Remotes Agents mode
    •    Open Source PBX integration
    •    Components clusterization

Components
The main technologies involved in OMniLeads (OML) are also part of Open Source projects, such as:
    ⁃    Asterisk
    ⁃    Kamailio
    ⁃    RtpEngine
    ⁃    Django
    ⁃    Nginx
    ⁃    Postgres
    ⁃    Python
    ⁃    Javascript

License
GPLv3. Every source code file contains the license preamble and copyright details.

Actual version
1.3.X.

Documentation
Official documentation for the proyect can be found at: https://omnileads.net/.


Installation
At the moment of the creation of this README, OMniLeads (OML) supports the following distributions:
- GNU/Linux CentOS 7 minimal version
- GNU/Linux Debian 9 netinstall version
- GNU/Linux Ubuntu 18.04 version

An "step to step" tutorial is located on the section of “Docs & Recursos” at: https://omnileads.net/

The actual installation procedure describe how to deploy an “All In One” (AIO) architecture, it means all the components of OMniLeads (OML) deployed inside one Host Server. There is also the option of run some components or services on differents hosts (for horizontal scalability), go to the docs to see more information about this.

The selected tool for install & update OMniLeads (OML) is: Ansible(https://www.ansible.com/). The installation have four differents posibilities:
1- Ansible Self-Hosted mode (see https://documentacion-omnileads.readthedocs.io/en/stable/install.html)
2- Ansible Host-Node mode (see https://documentacion-omnileads.readthedocs.io/en/stable/install_remote.html#about-install-remote)
3- Horizontal Cluster Installation(see https://documentacion-omnileads.readthedocs.io/en/stable/install_cluster.html#about-install-cluster)
4- Deploy using Docker(see https://documentacion-omnileads.readthedocs.io/en/stable/install_docker.html#about-install-docker)


The installation script is found inside the software repository. More information can be shown using the help flag “-h”:
./deploy.sh -h

For example, this command makes a fresh install of Omnileads
/deploy.sh -i --iface=<your_iface>

Please, READ CAREFULLY the Installation Tutorial available in the official page for OMniLeads Project (OML).


OMniLeads (OML) repository:
El official project repository is in Gitlab: https://gitlab.com/omnileads/ominicontacto


Issues & Bugs reporting:

For Issues & Bugs reporting: https://gitlab.com/omnileads/ominicontacto/issues


Community support:

For details related to OML roadmap:  community@omnileads.net
For details related to OML support: support@omnileads.net
For comercial services: business@omnileads.net

Useful resources:
Video-tutorials can be found at: https://vimeo.com/user87733702
News: https://omnileads.net/news/
Twitter: @OMniLeads_net

Disclaimer:
The third-party software components are registered marks from its corresponding owners or mark owners. Its use non imply any liability,affiliation or collaboration with those owners from OMniLeads project (OML).

--
