# ProdEnv. Omnileads Docker environment for production

This environment can be deployed in any linux distro. Linux distro tested by our team is Ubuntu 20.04.

## Prerequisites

1. Install Docker CE for your distro: https://docs.docker.com/install/
2. Install docker-compose
    As docker CE follow the installation steps: https://docs.docker.com/compose/install/
3. Follow docker post-installations steps: https://docs.docker.com/install/linux/linux-postinstall/
4. PostgreSQL, RTPengine, MariaDB and Wombat Dialer installed and configured to be accessed by the containers.

## Deploy of stack

1. Create the .env file, coyping the .env.template. Edit the variables according with your installation
```sh
  $ cp .env.template .env
```
Edit carefully the variables needed. The variables are widely explained in .env file.
---
**Note:** Check the network assigned to devenv in SUBNET variable. By default the subnet 192.168.16.0/24 is assgined to the environment. Change the subnet if it clashes with your WLAN o LAN subnet
---
2. Copy the docker.json file into `/etc/docker/` folder.
3. Copy the `omnileads.service` file in `/etc/systemd/system/`
4. Create the folder `/opt/omnileads`
```sh
  sudo mkdir -p /opt/omnileads
```
5. Make a symbolic link of the prodenv folder in `/opt/omnileads`
```sh
  ln -s $REPO_LOCATION/install/docker/prodenv /opt/omnileads
```
Where $REPO_LOCATION is the path where you cloned the OMniLeads repository
6. Run following commands:
```sh
  systemctl restart docker
  systemctl daemon-reload
  systemctl enable omnileads
  systemctl start omnileads
```
With the last command you raised up the environment. This will take some time while it download the docker images. Once finished you can use **docker ps** to see that you have 10 containers up and running.

## Setting default admin user password
---
**Note:** the next command must be run only once, when environment is raised up at first time
---
```sh
  $ docker-compose exec app bash or docker exec -it omlapp bash
  $ python3 manage.py cambiar_admin_password
```
This will set the admin password to default value: 'admin'. So you can login using that credentials: `admin/admin`

## Services you can access

* First is the web server available. To access omnileads via web browser: **https://YOUR_HOSTNAME:PORT** or **https://YOUR_IP:PORT**. The port is the same of $NGINX_EXT_PORT variable in .env file
* Second, the postgresql database, you can access it with this credentials:
```sh
  PGHOST=host you installed and configured
  PGDATABASE=database you created for omnileads
  PGUSER=user that will own omnileads database
  PGPASSWORD=its password
  PGPORT=port where postgresql is listening
```
* Third, Wombat Dialer web server. To access it: **http://YOUR_HOSTNAME:445**

## Configuring wombat dialer

You only need to do this if you are going to work with Predictive Dialer campaigns

Before accessing the web you need to configure the access of users in your MySQL server:
```sh
  mysql -ne "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION;"
  mysql -ne "GRANT ALL PRIVILEGES ON *.* TO '$WOMBAT_DB_USER'@'%' IDENTIFIED BY '$WOMBAT_DB_PASS' WITH GRANT OPTION;"
```
Where $WOMBAT_DB_USER and $WOMBAT_DB_PASS are the user and password you configured for Wombat Dialer database in .env file

When you enter to **http://YOUR_HOSTNAME:445** you go to Wombat Dialer to begin its configuration. Check our official documentation to check this: https://documentacion-omnileads.readthedocs.io/es/stable/maintance.html#configuracion-del-modulo-de-discador-predictivo
---
**Note:** when configuring AMI connection in Wombat Dialer, the server address is `acd`.
---

## Updating images

The images of the different services can be updated using the script `download_images.sh`. The script will always pull the latest production images of all services from the Freetech Solutions dockerhub.
