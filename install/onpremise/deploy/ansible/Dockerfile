FROM lexauw/ansible-alpine:v2.9.2
ENV LANG en_US.utf8
ENV NOTVISIBLE "in users profile"

RUN  apk add bash git net-tools iputils curl rsync openssh-keygen
RUN ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""

EXPOSE 80/tcp
