#Script para generar el certificado final combinando el certificado de la CA con el certificado del nodo

cat {{ kamailio_location }}/etc/certs/demoCA/cert.pem > {{ install_prefix }}static/ominicontacto/voip.cert
cat {{ kamailio_location }}/etc/certs/cert.pem >> {{ install_prefix }}static/ominicontacto/voip.cert
