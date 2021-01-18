FROM centos:centos7
ENV LANG en_US.utf8
ENV NOTVISIBLE "in users profile"
ENV AWS_CLI_VERSION 1.18.5
ENV ANSIBLE_VERSION 2.9.2
ENV PATH=$PATH:/usr/local/bin:/root/.local/bin

RUN yum update -y && \
    yum -y install epel-release && \
    yum install python python-pip git which -y && \
    pip install "ansible==$ANSIBLE_VERSION" --user \
    pip install "awscli==$AWS_CLI_VERSION"
