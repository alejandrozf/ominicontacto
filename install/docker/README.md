# Docker Omlapp

## Omlappbuilder

In this folder is the Dockerfile to install the dependencies that will need OMniLeads django code.

To build the image `omlappbuilder` use the script `build_image.sh`:

```sh
  DOCKER_USER=$USER DOCKER_PASSWORD=$PASSWORD ./build_image.sh $TAG
```
Change $USER and $PASSWORD with the credentials of docker hub and change $TAG with the tag of the image you want.

## Omlapp

To build the docker image of Omlapp:
```sh
  docker build -f Dockerfile -t freetechsolutions/omlapp:$TAG ../..
```
Where $TAG with the tag of the image you want.
