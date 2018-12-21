#Script para generar el certificado final combinando el certificado de la CA con el certificado del nodo
{% if cluster == 0 %}
cat {{ install_prefix}}nginx_certs/demoCA/cert.pem > {{ install_prefix }}static/ominicontacto/voip.cert
{% else %}
cat {{ install_prefix}}nginx_certs/ca_cert.pem > {{ install_prefix }}static/ominicontacto/voip.cert
{% endif %}
cat {{ install_prefix }}nginx_certs/cert.pem >> {{ install_prefix }}static/ominicontacto/voip.cert
