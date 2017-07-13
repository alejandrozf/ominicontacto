# -*- coding: utf-8 -*-

"""
Esta vista se configua user y password del cual se van conectar a la api de la cuál se
conecta al servicio json configurada calificacion_cliente_externa_view() en el
modulo views_calificacion_formulario
"""

from __future__ import unicode_literals


from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, ListView
from ominicontacto_app.forms import UserApiCrmForm
from ominicontacto_app.models import UserApiCrm


import logging as logging_

logger = logging_.getLogger(__name__)


class UserApiCrmCreateView(CreateView):
    """Vista para crear un nuevo userapicrm"""
    model = UserApiCrm
    template_name = 'base_create_update_form.html'
    form_class = UserApiCrmForm

    def get_success_url(self):
        return reverse('user_api_crm_list')


class UserApiCrmUpdateView(UpdateView):
    """Vista para modificar el userapicrm"""
    model = UserApiCrm
    template_name = 'base_create_update_form.html'
    form_class = UserApiCrmForm

    def get_success_url(self):
        return reverse('user_api_crm_list')


class UserApiCrmListView(ListView):
    """Vista para listar los userapicrm"""
    model = UserApiCrm
    template_name = 'user_api_crm_list.html'
