# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from configuracion_telefonia_app.models import RutaSaliente, TroncalSIP, OrdenTroncal
from configuracion_telefonia_app.forms import (RutaSalienteForm, TroncalSIPForm,
                                               PatronDeDiscadoFormset, OrdenTroncalFormset)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk, RestablecerConfiguracionTelefonicaError,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk
)


class TroncalSIPMixin(object):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        try:
            sincronizador = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
            sincronizador.regenerar_troncales(self.object)
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> "
                       "con el siguiente error: {0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return self.form_invalid(form)
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


class TroncalSIPDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación de un troncal sip
    """
    model = TroncalSIP
    template_name = 'delete_troncal_sip.html'

    def get_success_url(self):
        return reverse('lista_troncal_sip')

    def dispatch(self, request, *args, **kwargs):
        troncal_sip = self.get_object()
        if OrdenTroncal.objects.filter(troncal=troncal_sip).exists():
            message = (_('No se puede eliminar un troncal que está siendo usado en una ruta'
                         'saliente'))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())
        return super(TroncalSIPDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        super(TroncalSIPDeleteView, self).delete(request, *args, **kwargs)
        message = (_('Troncal Sip eliminado con éxito'))
        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return TroncalSIP.objects.get(pk=self.kwargs['pk'])


class RutaSalienteListView(ListView):
    """Vista para listar las rutas salientes"""
    model = RutaSaliente
    paginate_by = 40
    context_object_name = 'rutas_salientes'
    template_name = 'lista_rutas_salientes.html'
    ordering = ['id']


def escribir_ruta_saliente_config(self, ruta_saliente):
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.regenerar_rutas_salientes(ruta_saliente)
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
                   "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


class RutaSalienteMixin(object):

    def form_valid(self, form):
        ruta_saliente = form.save(commit=False)
        patrondiscado_formset = PatronDeDiscadoFormset(
            self.request.POST, instance=ruta_saliente, prefix='patron_discado')
        ordentroncal_formset = OrdenTroncalFormset(
            self.request.POST, instance=ruta_saliente, prefix='orden_troncal')
        if patrondiscado_formset.is_valid() and ordentroncal_formset.is_valid():
            form.save()
            patrondiscado_formset.save()
            ordentroncal_formset.save()
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            # inserta la configuración de la ruta saliente en asterisk
            escribir_ruta_saliente_config(self, ruta_saliente)
            return redirect('lista_rutas_salientes')
        return render(self.request, 'ruta_saliente.html',
                      {'form': form, 'patrondiscado_formset': patrondiscado_formset,
                       'ordentroncal_formset': ordentroncal_formset})


class RutaSalienteCreateView(RutaSalienteMixin, CreateView):
    model = RutaSaliente
    template_name = 'crear_ruta_saliente.html'
    form_class = RutaSalienteForm
    message = _('Ruta saliente creada con éxito')

    def get_context_data(self, **kwargs):
        context = super(RutaSalienteCreateView, self).get_context_data()
        context['patrondiscado_formset'] = PatronDeDiscadoFormset(prefix='patron_discado')
        context['ordentroncal_formset'] = OrdenTroncalFormset(prefix='orden_troncal')
        return context


class RutaSalienteUpdateView(RutaSalienteMixin, UpdateView):
    model = RutaSaliente
    template_name = 'editar_ruta_saliente.html'
    form_class = RutaSalienteForm
    message = _('Ruta saliente modificada con éxito')

    def _inicializar_patrones_discado(self, ruta_saliente):
        initial_data = ruta_saliente.patrones_de_discado.values()
        patrondiscado_formset = PatronDeDiscadoFormset(
            initial=initial_data, instance=ruta_saliente, prefix='patron_discado')
        return patrondiscado_formset

    def _inicializar_troncales(self, ruta_saliente):
        initial_data = ruta_saliente.secuencia_troncales.values()
        ordentroncal_formset = OrdenTroncalFormset(
            initial=initial_data, instance=ruta_saliente, prefix='orden_troncal')
        return ordentroncal_formset

    def get_context_data(self, **kwargs):
        pk_ruta_saliente = self.kwargs.get('pk')
        ruta_saliente = get_object_or_404(RutaSaliente, pk=pk_ruta_saliente)
        patrondiscado_formset = self._inicializar_patrones_discado(ruta_saliente)
        ordentroncal_formset = self._inicializar_troncales(ruta_saliente)
        context = super(RutaSalienteUpdateView, self).get_context_data()
        context['patrondiscado_formset'] = patrondiscado_formset
        context['ordentroncal_formset'] = ordentroncal_formset
        return context


class EliminarRutaSaliente(DeleteView):
    model = RutaSaliente
    success_url = reverse_lazy('lista_rutas_salientes')
    template_name = 'eliminar_ruta_saliente.html'
    context_object_name = 'ruta_saliente'

    def get_context_data(self, **kwargs):
        context = super(EliminarRutaSaliente, self).get_context_data(**kwargs)
        huerfanos = []
        ruta_saliente = self.object
        for orden in ruta_saliente.secuencia_troncales.all():
            troncal = orden.troncal
            if troncal.ordenes_en_rutas_salientes.count() <= 1:
                huerfanos.append(orden.troncal)
        context['troncales_huerfanos'] = huerfanos
        return context

    def delete(self, request, *args, **kwargs):
        try:
            eliminar_ruta_saliente_config(self, self.get_object())
        except Exception:
            messages.error(request, _(u'No se ha podido eliminar la Ruta Saliente.'))
            return redirect('eliminar_ruta_saliente', pk=kwargs['pk'])

        messages.success(request, _(u'Se ha eliminado la Ruta Saliente.'))
        return super(EliminarRutaSaliente, self).delete(request, *args, **kwargs)


def eliminar_ruta_saliente_config(self, ruta_saliente):
    """Elimina las ruta en asterisk"""
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.eliminar_ruta_y_regenerar_asterisk(ruta_saliente)
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
                   "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
