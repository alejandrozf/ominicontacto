# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from django.views.generic import ListView, CreateView, UpdateView

from configuracion_telefonia_app.models import TroncalSIP
from configuracion_telefonia_app.forms import TroncalSIPForm


class TroncalSIPMixin(object):

    def form_valid(self, form):
        # self.object = form.save(commit=False)
        # self.object.save()
        # Hacer los cambios en AstDB, oml_sip_trunks.conf y oml_sip_registrations.conf
        return super(TroncalSIPMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_troncal_sip')


class TroncalSIPUpdateView(TroncalSIPMixin, UpdateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'base_create_update_form.html'


class TroncalSIPCreateView(TroncalSIPMixin, CreateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'base_create_update_form.html'


class TroncalSIPListView(ListView):
    """Vista para listar los Sip Trunks"""
    model = TroncalSIP
    paginate_by = 40
    template_name = 'lista_troncal_sip.html'
