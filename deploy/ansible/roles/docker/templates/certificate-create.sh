#!/bin/bash

CA_SUBJECT_CA="/C=AR/ST=CBA/L=CBA/O=FTS/OU=Desarrollo/CN={{ omnicentos_fqdn }}"
CA_SUBJECT_NODE="/C=AR/ST=CBA/L=CBA/O=FTS/OU=Desarrollo/CN={{ omni_ip }}"

sed -i "s/\(^DNS.1 =\).*/DNS.1 = {{ omnicentos_fqdn }}/" /etc/pki/tls/openssl.cnf
sed -i "s/\(^IP.1 =\).*/IP.1 = {{ omni_ip }}/" /etc/pki/tls/openssl.cnf

if [ ! -d {{ kamailio_location }}/etc/certs ]; then
  mkdir {{ kamailio_location }}/etc/certs && chmod 0700 {{ kamailio_location }}/etc/certs
  mkdir {{ kamailio_location }}/etc/certs/demoCA && chmod 0700 {{ kamailio_location }}/etc/certs
  mkdir {{ kamailio_location }}/etc/certs/demoCA/newcerts && chmod 0700 {{ kamailio_location }}/etc/certs
  touch {{ kamailio_location }}/etc/certs/demoCA/index.txt && chmod 0755 {{ kamailio_location }}/etc/certs/demoCA/index.txt
  touch {{ kamailio_location }}/etc/certs/demoCA/serial && echo "01" > {{ kamailio_location }}/etc/certs/demoCA/serial
  cd {{ kamailio_location }}/etc/certs/demoCA/ && \
  openssl req -new -x509 -extensions v3_ca -keyout key.pem -out cert.pem -days 3650 -passout pass:toor123 -subj "$CA_SUBJECT_CA"
  cd {{ kamailio_location }}/etc/certs/ && \
  openssl req -new -nodes -keyout key.pem -out req.pem -subj "$CA_SUBJECT_NODE"
  cd {{ kamailio_location }}/etc/certs && \
  openssl ca -extensions v3_req  -batch -days 1460 -out cert.pem -keyfile demoCA/key.pem -cert demoCA/cert.pem -passin pass:toor123 -infiles req.pem
  chown {{ usuario }}:{{ usuario }} -R {{ kamailio_location }}/etc/certs
  cat {{ kamailio_location }}/etc/certs/demoCA/cert.pem > /tmp/voip.cert
  cat {{ kamailio_location }}/etc/certs/cert.pem >> /tmp/voip.cert

fi
cat > /etc/sysconfig/rtpengine <<EOF

#
# Archivo autogenerado
#

OPTIONS="-i {{ omni_ip }} -n 127.0.0.1:22222 -m 20000 -M 30000 -L 7 --log-facility=local1"
EOF

touch {{ kamailio_location }}/etc/kamailio/kamailio-local.cfg
cat > {{ kamailio_location }}/etc/kamailio/kamailio-local.cfg <<EOF

#!substdef "!MY_IP_ADDR!{{ omni_ip }}!g"
#!substdef "!MY_DOMAIN!{{ omnicentos_fqdn }}!g"
#!substdef "!MY_UDP_PORT!5060!g"
#!substdef "!MY_TCP_PORT!5060!g"
#!substdef "!MY_TLS_PORT!5061!g"
#!substdef "!MY_WS_PORT!1080!g"
#!substdef "!MY_WSS_PORT!14443!g"
#!substdef "!MY_MSRP_PORT!6060!g"
#!substdef "!MY_MSRPTCP_PORT!6061!g"
#!substdef "!MY_ASTERISK!{{ omni_ip }}!g"
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
#!substdef "!MODULES_LOCATION!{{ kamailio_location }}/lib64/kamailio/modules/!g"
#!substdef "!PKEY_LOCATION!{{ kamailio_location }}/etc/certs/key.pem!g"
#!substdef "!CERT_LOCATION!{{ kamailio_location }}/etc/certs/cert.pem!g"
#!substdef "!CA_LOCATION!{{ kamailio_location }}/etc/certs/demoCA/cert.pem!g"
EOF
