#!/bin/bash

source /etc/profile.d/omnileads_envars.sh

python manage.py shell << EOF
from ominicontacto_app.models import User
u = User.objects.get(username='{{ admin_user }}')
u.set_password('$DJANGO_PASS')
u.save()
exit()
EOF
