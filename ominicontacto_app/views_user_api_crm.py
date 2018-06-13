# -*- coding: utf-8 -*-

"""
Esta vista se configua user y password del cual se van conectar a la api de la cuál se
conecta al servicio json configurada calificacion_cliente_externa_view() en el
modulo views_calificacion_cliente
"""

from __future__ import unicode_literals


from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.hashers import make_password
from ominicontacto_app.forms import UserApiCrmForm
from ominicontacto_app.models import UserApiCrm


import logging as logging_

logger = logging_.getLogger(__name__)

class PaswordHasherMixin(object):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.password = make_password(self.object.password,salt='Fuck1ngS4lt',hasher='default')
        #self.object.password = self.object.password.split('$',4)[3]
        self.object.save()
        return super(PaswordHasherMixin, self).form_valid(form)

class UserApiCrmCreateView(PaswordHasherMixin, CreateView):
    """Vista para crear un nuevo userapicrm"""
    model = UserApiCrm
    template_name = 'base_create_update_form.html'
    form_class = UserApiCrmForm

    def get_success_url(self):
        return reverse('user_api_crm_list')


class UserApiCrmUpdateView(PaswordHasherMixin, UpdateView):
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
