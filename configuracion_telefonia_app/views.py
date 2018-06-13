# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from django.views.generic import ListView, CreateView, UpdateView

from configuracion_telefonia_app.models import RutaSaliente, TroncalSIP
from configuracion_telefonia_app.forms import (RutaSalienteForm, TroncalSIPForm,
                                               PatronDeDiscadoFormset, OrdenTroncalFormset)


class TroncalSIPMixin(object):

    def form_valid(self, form):
        # self.object = form.save(commit=False)
        # self.object.save()
        # Hacer los cambios en AstDB, oml_sip_trunks.conf y oml_sip_registrations.conf
        return super(TroncalSIPMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_troncal_sip')


class TroncalSIPListView(ListView):
    """Vista para listar los Sip Trunks"""
    model = TroncalSIP
    paginate_by = 40
    template_name = 'lista_troncal_sip.html'


class TroncalSIPCreateView(TroncalSIPMixin, CreateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'base_create_update_form.html'


class TroncalSIPUpdateView(TroncalSIPMixin, UpdateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'base_create_update_form.html'


class RutaSalienteListView(ListView):
    """Vista para listar las rutas salientes"""
    model = RutaSaliente
    paginate_by = 40
    context_object_name = 'rutas_salientes'
    template_name = 'lista_rutas_salientes.html'


def escribir_ruta_saliente_config(ruta_saliente):
    # TODO: Modelar e implementar bien el objeto que tendrá esta responsabilidad
    print ("TODO: IMPLEMENTAR!!!")
    # Exception('No se pudo eliminar bien.')
    pass


class RutaSalienteMixin(object):

    def asignar_orden_troncales(self, ordentroncal_formset):
        """Escribe orden en troncales"""
        for i, form in enumerate(ordentroncal_formset.forms):
            form.instance.orden = i


class RutaSalienteCreateView(RutaSalienteMixin, CreateView):
    model = RutaSaliente
    template_name = 'ruta_saliente.html'
    form_class = RutaSalienteForm

    def get_context_data(self, **kwargs):
        context = super(RutaSalienteCreateView, self).get_context_data()
        context['patrondiscado_formset'] = PatronDeDiscadoFormset(prefix='patron_discado')
        context['ordentroncal_formset'] = OrdenTroncalFormset(prefix='orden_troncal')
        return context

    def form_valid(self, form):
        patrondiscado_formset = PatronDeDiscadoFormset(self.request.POST, prefix='patron_discado')
        ordentroncal_formset = OrdenTroncalFormset(self.request.POST, prefix='orden_troncal')
        if patrondiscado_formset.is_valid() and ordentroncal_formset.is_valid():
            form.save()
            ruta_saliente = form.instance
            patrondiscado_formset.instance = ruta_saliente
            patrondiscado_formset.save()
            self.asignar_orden_troncales(ordentroncal_formset)
            ordentroncal_formset.instance = ruta_saliente
            ordentroncal_formset.save()
            # muestra mensaje de éxito en creación
            message = _('Ruta saliente creada con éxito')
            messages.add_message(self.request, messages.SUCCESS, message)
            # inserta la configuración de la ruta saliente en asterisk
            escribir_ruta_saliente_config(ruta_saliente)
            return redirect('lista_rutas_salientes')
        return render(self.request, 'ruta_saliente.html',
                      {'patrondiscado_formset': patrondiscado_formset,
                       'ordentroncal_formset': ordentroncal_formset})


class RutaSalienteUpdateView(UpdateView):
    model = RutaSaliente
    template_name = 'ruta_saliente.html'
    form_class = RutaSalienteForm
