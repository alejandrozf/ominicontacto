# -*- coding: utf-8 -*-

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
    model = UserApiCrm
    template_name = 'base_create_update_form.html'
    form_class = UserApiCrmForm

    def get_success_url(self):
        return reverse('view_blanco')


class UserApiCrmUpdateView(UpdateView):
    model = UserApiCrm
    template_name = 'base_create_update_form.html'
    form_class = UserApiCrmForm

    def get_success_url(self):
        return reverse('view_blanco')


class UserApiCrmListView(ListView):
    model = UserApiCrm
    template_name = 'user_api_crm_list.html'
