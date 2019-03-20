#########################################################
### DevEnv. Omnileads Docker container for developers ###
#########################################################

You can have the software running in your system with this simple steps:
  1. Install Docker CE for Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/
  2. Install docker-compose
      As docker CE follow the installation steps: https://docs.docker.com/compose/install/
  3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/

NOTE: never raise up containers with root user or root privileges

  4. Change the TZ environment file in the docker-compose.yml to raise up containers with the timezone you want
  5. Go to deploy/Docker and run:
      - docker-compose -f stack.yml up -d

The docker-compose file links the OML repository into the container so any change you make in the repository will be reflected in the devenv inmediately

Once the container is running follow this steps to raise up the DevEnv server:

  1. To start your django-server:
      - docker exec -it -u omnileads omnileads /bin/bash -c "django-server"
  2. To kill the django-server:
     - docker exec -it -u omnileads omnileads /bin/bash -c "kill-django-server"
  3. If you see any service is down you can use this command to raise up everything:
     - docker exec -it omnileads /bin/bash -c "restart-services"

To access omnileads via web browser:
  1. Edit you /etc/hosts file with:
      172.16.0.2 omnileads.example.com
  2. Acces with your favorite browser:
      https://omnileads.example.com

#########################################################
###                   PBX-emulator                    ###
#########################################################

Adittionally with omnileads container is the pbx-emulator, this an emulation of a PSTN provider, so you can make calls via Omnileads and have different results of the call based on what you dialed.

Dialplan configuration:
  - Any number dialed finished with 0: PSTN is going to send you a BUSY signal
  - Any number dialed finished with 1: PSTN is going to answer your call and playback audios
  - Any number dialed finished with 2: PSTN will anwer your call, play short audio then hangup. This will emulate a calle hangup
  -  Any number dialed finished with 3: PSTN will answer your call after 35 seconds
  - Any number dialed finished with 5: PSTN will make you wait 120 seconds and then hangup. This will emulate a NO_ANSWER
  - Any number dialed finished with 9: PSTN will simulate a congestion

Inbound calls

You can simulate inbound calls registering an extension from the pbx-emulator. You can use the softphone you want. This are the extensions credentials:

  username: 01155001122
  secret: OMLtraining72
  domanin: 172.16.0.3

After registering the extension you can call this numbers for receiving the call to a Omnileads inbound campaign (check manuals to configure inbound campaign and inbound routing)

  0117766001X => you will receive the call with a random numeric CID
  0117766002X => you will receive the call with the word “unknown” as CID

Also you will have these two numbers to call from Omnileads to your softphone: 01155001122, 01155001133

Note: if you have any suggestions to power up this pbx-emulator you can open an issue in Omnileads gitub repository https://gitlab.com/omnileads/ominicontacto or send us a mail to support@omnileads.net

Thank you for using this!
