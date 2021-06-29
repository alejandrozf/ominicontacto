FROM tomcat:8.5-alpine

ENV WD_VERSION 20.02.1-272
ENV JAVA_CONNECTOR_VERSION 2.3.0
WORKDIR /usr/local/tomcat/webapps/
ADD http://downloads.loway.ch/wd/WombatDialer-$WD_VERSION.tar.gz /usr/local/tomcat/webapps/
RUN apk update \
    && apk add wget unzip \
    && tar xzvf WombatDialer-${WD_VERSION}.tar.gz \
    && mv wombatdialer-20.02.1 wombat \
    && rm -rf  WombatDialer-${WD_VERSION}.tar.gz \
    && wget https://downloads.mariadb.com/Connectors/java/connector-java-2.3.0/mariadb-java-client-${JAVA_CONNECTOR_VERSION}.jar \
    && cp mariadb-java-client-${JAVA_CONNECTOR_VERSION}.jar wombat/WEB-INF/lib/ \
    && rm -rf mariadb-java-client-${JAVA_CONNECTOR_VERSION}.jar
