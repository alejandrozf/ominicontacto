#Script para generar el certificado final combinando el certificado de la CA con el certificado del nodo

cat {{ install_prefix }}kamailio/etc/certs/demoCA/cert.pem > {{ install_prefix }}static/ominicontacto/voip.cert
cat {{ install_prefix }}kamailio/etc/certs/cert.pem >> {{ install_prefix }}static/ominicontacto/voip.cert
