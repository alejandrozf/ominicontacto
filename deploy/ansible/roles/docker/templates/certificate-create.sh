#!/bin/bash

echo "Ingrese la IP del servidor"
echo -en "IP: "; read ip

echo "Ingrese el FQDN del servidor"
echo -en "IP: "; read fqdn

CA_SUBJECT_CA="/C=AR/ST=CBA/L=CBA/O=FTS/OU=Desarrollo/CN=$fqdn"
CA_SUBJECT_NODE="/C=AR/ST=CBA/L=CBA/O=FTS/OU=Desarrollo/CN=$ip"

sed -i "s/\(^DNS.1 =\).*/DNS.1 = $fqdn/" /etc/pki/tls/openssl.cnf
sed -i "s/\(^IP.1 =\).*/IP.1 = $ip/" /etc/pki/tls/openssl.cnf

mkdir /opt/kamailio/etc/certs && chmod 0700 /opt/kamailio/etc/certs
mkdir /opt/kamailio/etc/certs/demoCA && chmod 0700 /opt/kamailio/etc/certs
mkdir /opt/kamailio/etc/certs/demoCA/newcerts && chmod 0700 /opt/kamailio/etc/certs
touch /opt/kamailio/etc/certs/demoCA/index.txt && chmod 0755 /opt/kamailio/etc/certs/demoCA/index.txt
touch /opt/kamailio/etc/certs/demoCA/serial && echo "01" > /opt/kamailio/etc/certs/demoCA/serial
cd /opt/kamailio/etc/certs/demoCA/ && \
   openssl req -new -x509 -extensions v3_ca -keyout key.pem -out cert.pem -days 3650 -passout pass:toor123 -subj "$CA_SUBJECT_CA"
cd /opt/kamailio/etc/certs/ && \
   openssl req -new -nodes -keyout key.pem -out req.pem -subj "$CA_SUBJECT_NODE"
cd /opt/kamailio/etc/certs && \
   openssl ca -extensions v3_req  -batch -days 1460 -out cert.pem -keyfile demoCA/key.pem -cert demoCA/cert.pem -passin pass:toor123 -infiles req.pem
chown kamailio:kamailio -R /opt/kamailio/etc/certs

cat > /etc/sysconfig/rtpengine <<EOF

#
# Archivo autogenerado
#

OPTIONS="-i $ip -n 127.0.0.1:22222 -m 20000 -M 30000 -L 7 --log-facility=local1"
EOF

touch /opt/omnileads/kamailio/etc/kamailio/kamailio-local.cfg
cat > /opt/omnileads/kamailio/etc/kamailio/kamailio-local.cfg <<EOF

#!substdef "!MY_IP_ADDR!$ip!g"
#!substdef "!MY_DOMAIN!$fqdn!g"
#!substdef "!MY_UDP_PORT!5060!g"
#!substdef "!MY_TCP_PORT!5060!g"
#!substdef "!MY_TLS_PORT!5061!g"
#!substdef "!MY_WS_PORT!1080!g"
#!substdef "!MY_WSS_PORT!14443!g"
#!substdef "!MY_MSRP_PORT!6060!g"
#!substdef "!MY_MSRPTCP_PORT!6061!g"
#!substdef "!MY_ASTERISK!$ip!g"
#!substdef "!MY_DB!127.0.0.1!g"

#!substdef "!MY_UDP_ADDR!udp:MY_IP_ADDR:MY_UDP_PORT!g"
#!substdef "!MY_TCP_ADDR!tcp:MY_IP_ADDR:MY_TCP_PORT!g"
#!substdef "!MY_TLS_ADDR!tls:MY_IP_ADDR:MY_TLS_PORT!g"
#!substdef "!MY_WS_ADDR!tcp:MY_IP_ADDR:MY_WS_PORT!g"
#!substdef "!MY_WSS_ADDR!tls:MY_IP_ADDR:MY_WSS_PORT!g"
#!substdef "!MY_MSRP_ADDR!tls:MY_IP_ADDR:MY_MSRP_PORT!g"
#!substdef "!MY_MSRPTCP_ADDR!tcp:MY_IP_ADDR:MY_MSRPTCP_PORT!g"
#!substdef "!MSRP_MIN_EXPIRES!1800!g"
#!substdef "!MSRP_MAX_EXPIRES!3600!g"
EOF
