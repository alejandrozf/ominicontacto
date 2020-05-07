# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

# TODO: Refactorizar las vistas en módulos mas pequeños y borrar este.

from __future__ import unicode_literals

import json
import logging

from django.urls import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.db.models import Case, When, Max, Min

from configuracion_telefonia_app.forms import (
    RutaSalienteForm, TroncalSIPForm, RutaEntranteForm, PatronDeDiscadoFormset, OrdenTroncalFormset,
    OpcionDestinoIVRFormset, IVRForm, ValidacionTiempoFormset, IdentificadorClienteForm,
    OpcionDestinoValidacionFechaHoraFormset, OpcionDestinoPersonalizadoForm, )
from configuracion_telefonia_app.models import (
    RutaSaliente, RutaEntrante, TroncalSIP, OrdenTroncal, DestinoEntrante, IVR,
    OpcionDestino, GrupoHorario, ValidacionFechaHora, IdentificadorCliente,
    DestinoPersonalizado, )
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk, RestablecerConfiguracionTelefonicaError,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk,
    SincronizadorDeConfiguracionRutaEntranteAsterisk,
    SincronizadorDeConfiguracionIVRAsterisk,
    SincronizadorDeConfiguracionValidacionFechaHoraAsterisk,
    SincronizadorDeConfiguracionGrupoHorarioAsterisk,
    SincronizadorDeConfiguracionIdentificadorClienteAsterisk,
    SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk
)

logger = logging.getLogger(__name__)


# Debería extender del AbstractConfiguracionAsterisk
class SincronizadorDummy(object):
    def regenerar_asterisk(self, objeto):
        pass

    def eliminar_y_regenerar_asterisk(self, objeto):
        pass


def _asignar_destino_anterior(opcion_destino_formset, nodo_entrante):
    """Asigna un nodo entrante como anterior en la creación/modificación de sus opciones de
    destinos siguientes
    """
    for opcion_destino_form in opcion_destino_formset.forms:
        opcion_destino_form.instance.destino_anterior = nodo_entrante
    return opcion_destino_formset


def escribir_ruta_saliente_config(self, ruta_saliente):
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.regenerar_rutas_salientes(ruta_saliente)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def eliminar_ruta_saliente_config(self, ruta_saliente):
    """Elimina las ruta en asterisk"""
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.eliminar_ruta_y_regenerar_asterisk(ruta_saliente)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def escribir_ruta_entrante_config(self, ruta_entrante):
    try:
        sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
        sincronizador.regenerar_asterisk(ruta_entrante)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def eliminar_ruta_entrante_config(self, ruta_entrante):
    try:
        sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
        sincronizador.eliminar_y_regenerar_asterisk(ruta_entrante)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def escribir_nodo_entrante_config(self, nodo_destino_entrante, sincronizador):
    try:
        sincronizador.regenerar_asterisk(nodo_destino_entrante)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def eliminar_troncal_config(self, trunk):
    """Elimina trunk de asterisk"""
    try:
        sincronizador = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
        sincronizador.eliminar_troncal_y_regenerar_asterisk(trunk)
    except RestablecerConfiguracionTelefonicaError as e:
        message = _("<strong>¡Cuidado!</strong> "
                    "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


class TroncalSIPMixin(object):

    def process_in_form_valid(self, form, update=False):
        self.object = form.save(commit=False)
        self.object.save()
        try:
            sincronizador = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
            sincronizador.regenerar_troncales(self.object)
        except RestablecerConfiguracionTelefonicaError as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: {0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return self.form_invalid(form)
        # en caso de un update de un troncal vamos a verificar si el troncal se encuentra en una
        # ruta y actualizar astdb
        if update:
            ordenes_troncales = self.object.ordenes_en_rutas_salientes.all()
            if ordenes_troncales:
                for orden in ordenes_troncales:
                    ruta = orden.ruta_saliente
                    try:
                        sincronizador_ruta = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
                        sincronizador_ruta.regenerar_troncales_en_ruta_asterisk(ruta)
                    except RestablecerConfiguracionTelefonicaError as e:
                        message = _("<strong>¡Cuidado!</strong> "
                                    "con el siguiente error: {0} .".format(e))
                        messages.add_message(
                            self.request,
                            messages.WARNING,
                            message,
                        )
        return super(TroncalSIPMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_troncal_sip', args=(1,))


class TroncalSIPListView(ListView):
    """Vista para listar los Sip Trunks"""
    model = TroncalSIP
    paginate_by = 40
    template_name = 'lista_troncal_sip.html'


class TroncalSIPCreateView(TroncalSIPMixin, CreateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'create_update_troncal.html'

    def form_valid(self, form):
        return self.process_in_form_valid(form)


class TroncalSIPUpdateView(TroncalSIPMixin, UpdateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'create_update_troncal.html'

    def form_valid(self, form):
        return self.process_in_form_valid(form, update=True)


class TroncalSIPDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación de un troncal sip
    """
    model = TroncalSIP
    template_name = 'delete_troncal_sip.html'

    def get_success_url(self):
        return reverse('lista_troncal_sip', args=(1,))

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
        eliminar_troncal_config(self, self.get_object())
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
    context_object_name = 'rutas_salientes'
    template_name = 'lista_rutas_salientes.html'
    ordering = ['orden']


class OrdenarRutasSalientesView(View):
    http_method_names = ['post', ]

    def post(self, request):
        orden = request.POST.get('orden', '')
        if not orden:
            messages.warning(request, _(u'No se pudo guardar el orden'))
            return redirect('lista_rutas_salientes', page=1)

        orden = json.loads(orden)
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(orden)])
        rutas_ordenadas = RutaSaliente.objects.filter(pk__in=orden).order_by(preserved)

        cantidad = rutas_ordenadas.count()
        mayor = RutaSaliente.objects.aggregate(Max('orden'))['orden__max']
        menor = RutaSaliente.objects.aggregate(Min('orden'))['orden__min']
        # Con esto aseguro no repetir ordenes en la base
        i = mayor + 1
        # Para que el valor no se vaya muy alto vuelvo a empezar desde el 1
        if cantidad < (menor - 1):
            i = 1
        # TODO: Ver la manera de utilizar un bulk_update para no hacer 1 query por cada Ruta
        for ruta in rutas_ordenadas:
            ruta.orden = i
            ruta.save()
            i += 1

        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador._generar_y_recargar_archivos_conf_asterisk()
        messages.success(request, _(u'Orden guardado satisfactoriamente'))
        return redirect('lista_rutas_salientes', page=1)


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
            return redirect('lista_rutas_salientes', page=1)
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
    success_url = reverse_lazy('lista_rutas_salientes', args=(1,))
    template_name = 'eliminar_ruta_saliente.html'
    context_object_name = 'ruta_saliente'

    def dispatch(self, request, *args, **kwargs):
        ruta_saliente = RutaSaliente.objects.get(pk=self.kwargs['pk'])
        if ruta_saliente.campana_set.exists():
            message = _("No está permitido eliminar una Ruta Saliente asociado a una campaña")
            messages.warning(self.request, message)
            return HttpResponseRedirect(reverse('lista_rutas_salientes', args=(1,)))
        return super(EliminarRutaSaliente, self).dispatch(request, *args, **kwargs)

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


class RutaEntranteListView(ListView):
    """Lista todas las rutas entrantes"""
    template_name = "lista_rutas_entrantes.html"
    model = RutaEntrante
    paginate_by = 40
    context_object_name = 'rutas_entrantes'


class RutaEntranteMixin(object):

    def get_success_url(self):
        return reverse('lista_rutas_entrantes', args=(1,))

    def form_valid(self, form):
        form.save()
        # escribe ruta entrante en asterisk
        escribir_ruta_entrante_config(self, form.instance)
        return super(RutaEntranteMixin, self).form_valid(form)


class RutaEntranteCreateView(RutaEntranteMixin, CreateView):
    """Vista para crear una ruta entrante"""
    template_name = "crear_ruta_entrante.html"
    model = RutaEntrante
    form_class = RutaEntranteForm


class RutaEntranteUpdateView(RutaEntranteMixin, UpdateView):
    """Vista para modificar una ruta entrante"""
    template_name = "editar_ruta_entrante.html"
    model = RutaEntrante
    form_class = RutaEntranteForm

    def form_valid(self, form):
        # Antes de escribir los nuevos datos de la ruta entrante, borro los viejos.
        eliminar_ruta_entrante_config(self, self.get_object())
        return super(RutaEntranteUpdateView, self).form_valid(form)


class RutaEntranteDeleteView(DeleteView):
    """Vista para eliminar una ruta entrante"""
    model = RutaEntrante
    success_url = reverse_lazy('lista_rutas_entrantes', args=(1,))
    template_name = 'eliminar_ruta_entrante.html'
    context_object_name = 'ruta_entrante'

    def dispatch(self, request, *args, **kwargs):
        ruta_entrante = RutaEntrante.objects.get(pk=self.kwargs['pk'])
        if ruta_entrante.destino.tipo == 1:
            if ruta_entrante.destino.content_object.outr:
                message = _("No está permitido eliminar una Ruta Entrante asociada"
                            "con una campaña que tiene una Ruta Saliente.")
                messages.warning(self.request, message)
                return HttpResponseRedirect(reverse('lista_rutas_entrantes', args=(1,)))
        return super(RutaEntranteDeleteView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return RutaEntrante.objects.get(pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        try:
            sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
            sincronizador.eliminar_y_regenerar_asterisk(self.get_object())
        except RestablecerConfiguracionTelefonicaError as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: {0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

        messages.success(request, _(u'Se ha eliminado la Ruta Entrante.'))
        return super(RutaEntranteDeleteView, self).delete(request, *args, **kwargs)


class ApiObtenerDestinosEntrantes(View):
    """Devuelve todos los nodos DestinoEntrantes de un tipo"""

    def get(self, *args, **kwargs):
        tipo_destino = kwargs.get('tipo_destino')
        data = []
        for nodo_entrante in DestinoEntrante.objects.filter(tipo=tipo_destino):
            repr_nombre = str(nodo_entrante)
            pk = nodo_entrante.pk
            data.append({'nombre': repr_nombre, 'id': pk})
        return JsonResponse(data, safe=False)


class IVRMixin(object):
    def get_success_url(self):
        return reverse('lista_ivrs', args=(1,))

    def get_sincronizador_de_configuracion(self):
        sincronizador = SincronizadorDeConfiguracionIVRAsterisk()
        return sincronizador


class IVRListView(ListView):
    """Lista todos los nodos de tipo IVR"""
    template_name = "lista_ivrs.html"
    model = IVR
    paginate_by = 40
    context_object_name = 'ivrs'


class IVRCreateView(IVRMixin, CreateView):
    """Vista para crear un nodo de tipo IVR"""
    template_name = "crear_ivr.html"
    model = IVR
    form_class = IVRForm
    message = _('Se ha creado el IVR con éxito')

    def get_context_data(self, **kwargs):
        empty_queryset = OpcionDestino.objects.none()
        ivr_formset = OpcionDestinoIVRFormset(prefix='ivr', queryset=empty_queryset)
        context = super(IVRCreateView, self).get_context_data(**kwargs)
        context['opcion_destino_formset'] = ivr_formset
        return context

    def _crear_destinos_fijos(self, form, nodo_ivr):
        time_out_destination = form.cleaned_data['time_out_destination']
        invalid_destination = form.cleaned_data['invalid_destination']
        OpcionDestino.crear_opcion_destino(nodo_ivr, time_out_destination, IVR.VALOR_TIME_OUT)
        OpcionDestino.crear_opcion_destino(
            nodo_ivr, invalid_destination, IVR.VALOR_DESTINO_INVALIDO)

    def form_valid(self, form):
        ivr = form.save(commit=False)
        nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr, commit=False)
        opcion_destino_formset = OpcionDestinoIVRFormset(self.request.POST, prefix='ivr')
        opcion_destino_formset = _asignar_destino_anterior(opcion_destino_formset, nodo_ivr)
        if form.is_valid() and opcion_destino_formset.is_valid():
            ivr.save()
            nodo_ivr.content_object = ivr
            nodo_ivr.save()
            opcion_destino_formset = _asignar_destino_anterior(
                opcion_destino_formset, nodo_ivr)
            opcion_destino_formset.save()
            # crea opciones de destino fijas para los valores de los campos 'time_out_destination'
            # e 'invalid_destination'
            self._crear_destinos_fijos(form, nodo_ivr)
            # inserta la configuración de la ruta saliente en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, ivr, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect('lista_ivrs', page=1)
        return render(
            self.request, 'crear_ivr.html',
            {'form': form, 'opcion_destino_formset': opcion_destino_formset})


class IVRUpdateView(IVRMixin, UpdateView):
    """Vista para modificar un nodo de tipo IVR"""
    template_name = "editar_ivr.html"
    model = IVR
    form_class = IVRForm
    message = _('Se ha modificado el IVR con éxito')

    def _inicializar_opciones_destino(self, nodo_ivr):
        valores_fijos_ivr = (
            IVR.VALOR_TIME_OUT, IVR.VALOR_DESTINO_INVALIDO)
        queryset = nodo_ivr.destinos_siguientes.exclude(valor__in=valores_fijos_ivr)
        opcion_destino_formset = OpcionDestinoIVRFormset(queryset=queryset, prefix='ivr')
        return opcion_destino_formset

    def get_context_data(self, **kwargs):
        context = super(IVRUpdateView, self).get_context_data(**kwargs)
        ivr = context['form'].instance
        nodo_ivr = DestinoEntrante.objects.get(
            object_id=ivr.pk, content_type=ContentType.objects.get_for_model(ivr))
        ordentroncal_formset = self._inicializar_opciones_destino(nodo_ivr)
        context['opcion_destino_formset'] = ordentroncal_formset
        return context

    def _modificar_opciones_destino_fijas(self, form, nodo_ivr):
        # se modifican los valores de las opciones destino fijas si han sufrido cambios
        # TODO: refactorizar los bloques de código hacia un sólo método
        if 'time_out_destination' in form.changed_data:
            new_time_out_destination = form.cleaned_data['time_out_destination']
            opcion_destino_time_out = nodo_ivr.destinos_siguientes.get(valor=IVR.VALOR_TIME_OUT)
            opcion_destino_time_out.destino_siguiente = new_time_out_destination
            opcion_destino_time_out.save()
        if 'invalid_destination' in form.changed_data:
            new_invalid_destination = form.cleaned_data['invalid_destination']
            opcion_destino_invalid_destination = nodo_ivr.destinos_siguientes.get(
                valor=IVR.VALOR_DESTINO_INVALIDO)
            opcion_destino_invalid_destination.destino_siguiente = new_invalid_destination
            opcion_destino_invalid_destination.save()

    def form_valid(self, form):
        ivr = form.instance
        nodo_ivr = DestinoEntrante.objects.get(
            object_id=ivr.pk, content_type=ContentType.objects.get_for_model(ivr))
        opcion_destino_formset = OpcionDestinoIVRFormset(self.request.POST, prefix='ivr')
        opcion_destino_formset = _asignar_destino_anterior(opcion_destino_formset, nodo_ivr)
        if form.is_valid() and opcion_destino_formset.is_valid():
            form.save()
            opcion_destino_formset.save()
            # modifica las opciones de destino fijas para los valores de los campos
            # 'time_out_destination' e 'invalid_destination'
            self._modificar_opciones_destino_fijas(form, nodo_ivr)
            # inserta la configuración de la ruta saliente en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, ivr, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect('lista_ivrs', page=1)
        return render(
            self.request, 'editar_ivr.html',
            {'form': form, 'opcion_destino_formset': opcion_destino_formset})


class GrupoHorarioListView(ListView):
    """Lista los grupos horarios existentes"""
    model = GrupoHorario
    template_name = "lista_grupos_horarios.html"
    context_object_name = 'grupos_horarios'
    paginate_by = 40
    ordering = ['id']


class GrupoHorarioMixin(object):

    def form_valid(self, form):
        validacion_tiempo_formset = ValidacionTiempoFormset(
            self.request.POST, instance=form.instance, prefix='validacion_tiempo')
        if form.is_valid() and validacion_tiempo_formset.is_valid():
            grupo_horario = form.save()
            validacion_tiempo_formset.save()

            try:
                sincronizador = SincronizadorDeConfiguracionGrupoHorarioAsterisk()
                sincronizador.regenerar_asterisk(grupo_horario)
            except RestablecerConfiguracionTelefonicaError as e:
                message = _("<strong>¡Cuidado!</strong> con el siguiente error: {0} .".format(e))
                messages.add_message(self.request, messages.WARNING, message)

            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.success_url)
        return render(
            self.request, self.template_name,
            {'form': form, 'validacion_tiempo_formset': validacion_tiempo_formset})


class GrupoHorarioCreateView(GrupoHorarioMixin, CreateView):
    """Crea un grupo horario"""
    model = GrupoHorario
    template_name = "crear_grupo_horario.html"
    fields = ('nombre',)
    success_url = reverse_lazy('lista_grupos_horarios', args=(1,))
    message = _('Se ha creado el grupo horario con éxito')

    def get_context_data(self, **kwargs):
        context = super(GrupoHorarioCreateView, self).get_context_data(**kwargs)
        context['validacion_tiempo_formset'] = ValidacionTiempoFormset(prefix='validacion_tiempo')
        return context


class GrupoHorarioUpdateView(GrupoHorarioMixin, UpdateView):
    """Edita un grupo horario"""
    model = GrupoHorario
    template_name = 'editar_grupo_horario.html'
    fields = ('nombre',)
    success_url = reverse_lazy('lista_grupos_horarios', args=(1,))
    message = _('Se ha modificado el grupo horario con éxito')

    def get_context_data(self, **kwargs):
        context = super(GrupoHorarioUpdateView, self).get_context_data(**kwargs)
        grupo_horario = context['form'].instance
        initial_data = grupo_horario.validaciones_tiempo.values()
        context['validacion_tiempo_formset'] = ValidacionTiempoFormset(
            initial=initial_data, instance=grupo_horario, prefix='validacion_tiempo')
        return context


class GrupoHorarioDeleteView(DeleteView):
    """Elimina un grupo horario"""
    model = GrupoHorario
    template_name = 'eliminar_grupo_horario.html'
    context_object_name = 'grupo_horario'
    success_url = reverse_lazy('lista_grupos_horarios', args=(1,))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            sincronizador = SincronizadorDeConfiguracionGrupoHorarioAsterisk()
            sincronizador.eliminar_y_regenerar_asterisk(self.object)
        except RestablecerConfiguracionTelefonicaError as e:
            message = _("<strong>¡Cuidado!</strong> con el siguiente error: {0} .".format(e))
            messages.add_message(self.request, messages.WARNING, message)
        if self.object.validaciones_fecha_hora.count() > 0:
            message = _(
                'No se puede eliminar un Grupo Horario utilizado en una Validacion Fecha Hora')
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())

        message = _(u"Se ha eliminado el Grupo Horario.")
        messages.add_message(self.request, messages.SUCCESS, message)
        return super(GrupoHorarioDeleteView, self).dispatch(request, *args, **kwargs)


class ValidacionFechaHoraListView(ListView):
    """Lista los nodos de validación fecha/hora existentes"""
    model = ValidacionFechaHora
    template_name = 'lista_validaciones_fecha_hora.html'
    context_object_name = 'validaciones_fecha_hora'
    paginate_by = 40
    ordering = ['id']


class ValidacionFechaHoraMixin(object):

    def get_success_url(self):
        return reverse('lista_validaciones_fecha_hora', args=(1,))

    def get_sincronizador_de_configuracion(self):
        sincronizador = SincronizadorDeConfiguracionValidacionFechaHoraAsterisk()
        return sincronizador


class ValidacionFechaHoraCreateView(ValidacionFechaHoraMixin, CreateView):
    """Crea una validación de fecha/hora"""
    model = ValidacionFechaHora
    template_name = "crear_validacion_fecha_hora.html"
    fields = ('nombre', 'grupo_horario')
    message = _('Se ha creado la validacion horaria con éxito')

    def get_context_data(self, **kwargs):
        context = super(ValidacionFechaHoraCreateView, self).get_context_data(**kwargs)
        empty_queryset = OpcionDestino.objects.none()
        initial_data = [{'valor': ValidacionFechaHora.DESTINO_MATCH},
                        {'valor': ValidacionFechaHora.DESTINO_NO_MATCH}]
        validacion_fecha_hora_formset = OpcionDestinoValidacionFechaHoraFormset(
            prefix='validacion_fecha_hora', queryset=empty_queryset, initial=initial_data)
        context['validacion_fecha_hora_formset'] = validacion_fecha_hora_formset
        return context

    def form_valid(self, form):
        validacion_fecha_hora_formset = OpcionDestinoValidacionFechaHoraFormset(
            self.request.POST, prefix='validacion_fecha_hora')
        if form.is_valid() and validacion_fecha_hora_formset.is_valid():
            validacion = form.save()
            nodo_validacion = DestinoEntrante.crear_nodo_ruta_entrante(validacion)
            _asignar_destino_anterior(validacion_fecha_hora_formset, nodo_validacion)
            validacion_fecha_hora_formset.save()
            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, validacion, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())
        return render(
            self.request, self.template_name,
            {'form': form, 'validacion_fecha_hora_formset': validacion_fecha_hora_formset})


class ValidacionFechaHoraUpdateView(ValidacionFechaHoraMixin, UpdateView):
    """Edita una validación de fecha/hora"""
    model = ValidacionFechaHora
    template_name = "editar_validacion_fecha_hora.html"
    fields = ('nombre', 'grupo_horario')
    message = _('Se ha modificado la validacion horaria con éxito')

    def get_context_data(self, **kwargs):
        context = super(ValidacionFechaHoraUpdateView, self).get_context_data(**kwargs)
        validacion = context['form'].instance
        nodo_validacion = DestinoEntrante.objects.get(
            object_id=validacion.pk, content_type=ContentType.objects.get_for_model(validacion))
        queryset = nodo_validacion.destinos_siguientes.all()
        validacion_fecha_hora_formset = OpcionDestinoValidacionFechaHoraFormset(
            prefix='validacion_fecha_hora', queryset=queryset)
        context['validacion_fecha_hora_formset'] = validacion_fecha_hora_formset
        return context

    def form_valid(self, form):
        validacion_fecha_hora_formset = OpcionDestinoValidacionFechaHoraFormset(
            self.request.POST, prefix='validacion_fecha_hora')
        if form.is_valid() and validacion_fecha_hora_formset.is_valid():
            validacion = form.save()
            validacion_fecha_hora_formset.save()
            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, validacion, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())
        return render(
            self.request, self.template_name,
            {'form': form, 'validacion_fecha_hora_formset': validacion_fecha_hora_formset})


class DeleteNodoDestinoMixin(object):
    """
    Vista genérica para ser implementada por cada Nodo de Flujos de llamada
    """
    imposible_eliminar = _('No se puede eliminar un objeto que es destino en un flujo de llamada.')
    nodo_eliminado = _(u'Se ha eliminado el Nodo.')

    def eliminar_nodos_y_asociaciones(self):
        nodo = self.get_object()
        destino_entrante = DestinoEntrante.get_nodo_ruta_entrante(nodo)
        # Eliminar OpcionDestino que lo tienen como destino_anterior
        destino_entrante.destinos_siguientes.all().delete()
        # Eliminar DestinoEntrante
        destino_entrante.delete()

    @property
    def url_eliminar_name(self):
        raise NotImplementedError()

    def get_sincronizador_de_configuracion(self):
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        nodo = DestinoEntrante.get_nodo_ruta_entrante(self.object)
        permitido_eliminar = True
        if nodo.es_destino_en_flujo_de_llamada():
            message = self.imposible_eliminar
            permitido_eliminar = False
        elif nodo.es_destino_failover():
            permitido_eliminar = False
            campanas_failover = nodo.campanas_destino_failover.values_list('name', flat=True)
            imposible_failover = _(
                'No se puede eliminar la campaña. Es usada como destino failover de las campañas:'
                ' {0}').format(",".join(campanas_failover))
            message = imposible_failover
        if not permitido_eliminar:
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())
        return super(DeleteNodoDestinoMixin, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # TODO: analizar si se puede eliminar el código de validación de eliminación del objeto
        # pues es muy similar al del método 'dispatch' y al parecer no sería necesario
        nodo = DestinoEntrante.get_nodo_ruta_entrante(self.object)
        permitido_eliminar = True
        if nodo.es_destino_en_flujo_de_llamada():
            permitido_eliminar = False
            messages.error(request, self.imposible_eliminar)
        elif nodo.es_destino_failover():
            permitido_eliminar = False
            campanas_failover = nodo.campanas_destino_failover.values_list('nombre', flat=True)
            imposible_failover = _(
                'No se puede eliminar la campaña. Es usada como destino failover de las campañas:'
                ' {0}').format(",".join(campanas_failover))
            messages.error(request, imposible_failover)
        if not permitido_eliminar:
            return redirect(self.url_eliminar_name, self.get_object().id)

        try:
            sincronizador = self.get_sincronizador_de_configuracion()

            sincronizador.eliminar_y_regenerar_asterisk(self.get_object())
        except RestablecerConfiguracionTelefonicaError as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: {0} .".format(e))
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
            return redirect(self.url_eliminar_name, self.get_object().id)
        self.eliminar_nodos_y_asociaciones()

        if nodo.tipo != DestinoEntrante.CAMPANA:
            # las vistas de eliminación de campañas muestran su propio mensaje satisfactorio
            messages.success(request, self.nodo_eliminado)
        return super(DeleteNodoDestinoMixin, self).delete(request, *args, **kwargs)


class IVRDeleteView(IVRMixin, DeleteNodoDestinoMixin, DeleteView):
    model = IVR
    template_name = 'eliminar_ivr.html'
    url_eliminar_name = 'eliminar_ivr'
    imposible_eliminar = _('No se puede eliminar un IVR que es destino en un flujo de llamada.')
    nodo_eliminado = _(u'Se ha eliminado el IVR.')


class ValidacionFechaHoraDeleteView(ValidacionFechaHoraMixin, DeleteNodoDestinoMixin, DeleteView):
    """ Elimina una validacion Fecha Hora """
    model = ValidacionFechaHora
    template_name = 'eliminar_validacion_fecha_hora.html'
    url_eliminar_name = 'eliminar_validacion_fecha_hora'
    imposible_eliminar = _('No se puede eliminar una Validación Fecha Hora mientras sea'
                           ' destino en un flujo de llamada.')
    nodo_eliminado = _(u'Se ha eliminado la Validación Fecha Hora.')


class IdentificadorClienteListView(ListView):
    """Lista los nodos de validación fecha/hora existentes"""
    model = IdentificadorCliente
    template_name = 'lista_identificador_cliente.html'
    context_object_name = 'identificadores_cliente'
    paginate_by = 40
    ordering = ['id']


class IdentificadorClienteMixin(object):

    def get_success_url(self):
        return reverse('lista_identificador_cliente', args=(1,))

    def get_sincronizador_de_configuracion(self):
        sincronizador = SincronizadorDeConfiguracionIdentificadorClienteAsterisk()
        return sincronizador


class IdentificadorClienteCreateView(IdentificadorClienteMixin, CreateView):
    """Crea un IdentificadorCliente """
    model = IdentificadorCliente
    form_class = IdentificadorClienteForm
    template_name = "crear_identificacion_cliente.html"
    message = _('Se ha creado el Identificador de clientes con éxito')

    def get_context_data(self, **kwargs):
        context = super(IdentificadorClienteCreateView, self).get_context_data(**kwargs)
        empty_queryset = OpcionDestino.objects.none()
        initial_data = [{'valor': IdentificadorCliente.DESTINO_MATCH},
                        {'valor': IdentificadorCliente.DESTINO_NO_MATCH}]
        identificacion_cliente_formset = OpcionDestinoValidacionFechaHoraFormset(
            prefix='identificacion_cliente', queryset=empty_queryset, initial=initial_data)
        context['identificacion_cliente_formset'] = identificacion_cliente_formset
        return context

    def form_valid(self, form):
        identificacion_cliente_formset = OpcionDestinoValidacionFechaHoraFormset(
            self.request.POST, prefix='identificacion_cliente')

        validacion_ok = False
        salvar_opciones = False
        salvar_destino_false = False
        if form.is_valid():
            tipo_interaccion = form.cleaned_data.get('tipo_interaccion')
            es_interaccion_ext_tipo_2 = (
                tipo_interaccion == IdentificadorCliente.INTERACCION_EXTERNA_2)
            form_destino_false = identificacion_cliente_formset.forms[1]
            identificacion_cliente_formset_valid = identificacion_cliente_formset.is_valid()
            if identificacion_cliente_formset_valid:
                validacion_ok = True
                salvar_opciones = True
            elif es_interaccion_ext_tipo_2 and form_destino_false.is_valid():
                validacion_ok = True
                salvar_destino_false = True

        if validacion_ok:
            identificador = form.save()
            nodo_identificador = DestinoEntrante.crear_nodo_ruta_entrante(identificador)
            if salvar_opciones:
                _asignar_destino_anterior(identificacion_cliente_formset, nodo_identificador)
                identificacion_cliente_formset.save()
            elif salvar_destino_false:
                form_destino_false.instance.destino_anterior = nodo_identificador
                form_destino_false.save()

            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, identificador, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())

        else:
            return render(
                self.request, self.template_name,
                {'form': form, 'identificacion_cliente_formset': identificacion_cliente_formset})


class IdentificadorClienteUpdateView(IdentificadorClienteMixin, UpdateView):
    """Edita un IdentificadorCliente"""
    model = IdentificadorCliente
    form_class = IdentificadorClienteForm
    template_name = "editar_identificacion_cliente.html"
    message = _('Se ha modificado el Identificador de clientes con éxito')

    def get_context_data(self, **kwargs):
        context = super(IdentificadorClienteUpdateView, self).get_context_data(**kwargs)
        identificador = context['form'].instance
        nodo_identificador = DestinoEntrante.objects.get(
            object_id=identificador.pk,
            content_type=ContentType.objects.get_for_model(identificador))
        queryset = nodo_identificador.destinos_siguientes.all()
        identificacion_cliente_formset = OpcionDestinoValidacionFechaHoraFormset(
            prefix='identificacion_cliente', queryset=queryset)
        if identificador.tipo_interaccion == IdentificadorCliente.INTERACCION_EXTERNA_2:
            # cambiamos los forms ya que el formset pone por defecto
            # el form con valor en la primera posicion (que seria el destino True)
            form_destino_false, form_destino_true = identificacion_cliente_formset.forms
            identificacion_cliente_formset.forms = [form_destino_true, form_destino_false]
        context['identificacion_cliente_formset'] = identificacion_cliente_formset
        return context

    def _some_form_valid(self, identificacion_cliente_formset):
        for form in identificacion_cliente_formset.forms:
            if form.is_valid():
                return True
        return False

    def _get_form_destino_false(self, identificacion_cliente_formset):
        for form in identificacion_cliente_formset.forms:
            if form.is_valid() and form.instance.pk is not None:
                return form

    def form_valid(self, form):
        identificacion_cliente_formset = OpcionDestinoValidacionFechaHoraFormset(
            self.request.POST, prefix='identificacion_cliente')
        validacion_ok = False
        salvar_opciones = False
        salvar_destino_false = False
        if form.is_valid():
            tipo_interaccion = form.cleaned_data.get('tipo_interaccion')
            es_interaccion_ext_tipo_2 = (
                tipo_interaccion == IdentificadorCliente.INTERACCION_EXTERNA_2)
            identificacion_cliente_formset_valid = identificacion_cliente_formset.is_valid()
            if identificacion_cliente_formset_valid:
                validacion_ok = True
                salvar_opciones = True
            elif es_interaccion_ext_tipo_2 and self._some_form_valid(
                    identificacion_cliente_formset):
                validacion_ok = True
                salvar_destino_false = True

        if validacion_ok:
            identificador = form.save()
            nodo_identificador = DestinoEntrante.objects.get(
                object_id=identificador.pk,
                content_type=ContentType.objects.get_for_model(identificador))
            if salvar_opciones:
                OpcionDestino.objects.filter(destino_anterior=nodo_identificador).delete()
                _asignar_destino_anterior(identificacion_cliente_formset, nodo_identificador)
                identificacion_cliente_formset.save()
            elif salvar_destino_false:
                form_destino_false = self._get_form_destino_false(identificacion_cliente_formset)
                OpcionDestino.objects.filter(destino_anterior=nodo_identificador).delete()
                form_destino_false.instance.destino_anterior = nodo_identificador
                form_destino_false.save()

            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, identificador, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())
        return render(
            self.request, self.template_name,
            {'form': form, 'identificacion_cliente_formset': identificacion_cliente_formset})


class IdentificadorClienteDeleteView(IdentificadorClienteMixin, DeleteNodoDestinoMixin, DeleteView):
    model = IdentificadorCliente
    template_name = 'eliminar_identificador_cliente.html'
    url_eliminar_name = 'eliminar_identificador_cliente'
    imposible_eliminar = _('No se puede eliminar un Identificador de clientes '
                           'que es destino en un flujo de llamada.')
    nodo_eliminado = _(u'Se ha eliminado el Identificador de Clientes.')


class DestinoPersonalizadoListView(ListView):
    """Muestra la lista de los destinos personalizados"""
    model = DestinoPersonalizado
    template_name = 'lista_destino_personalizados.html'
    paginate_by = 40
    ordering = ['id']
    context_object_name = 'destinos_personalizados'


class DestinoPersonalizadoMixin(object):

    def get_success_url(self):
        return reverse('lista_destinos_personalizados', args=(1,))

    def get_sincronizador_de_configuracion(self):
        sincronizador = SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk()
        return sincronizador


class DestinoPersonalizadoCreateView(DestinoPersonalizadoMixin, CreateView):
    """Crea un Destino Personalizado"""
    model = DestinoPersonalizado
    fields = ('nombre', 'custom_destination')
    template_name = 'crear_destino_personalizado.html'
    message = _('Se ha creado el nodo de Destino Personalizado con éxito')

    def get_context_data(self, **kwargs):
        context = super(DestinoPersonalizadoCreateView, self).get_context_data(**kwargs)
        opcion_destino_failover_form = OpcionDestinoPersonalizadoForm(prefix='failover_form')
        context['opcion_destino_failover_form'] = opcion_destino_failover_form
        return context

    def form_valid(self, form):
        opcion_destino_failover_form = OpcionDestinoPersonalizadoForm(
            self.request.POST, prefix='failover_form')
        if form.is_valid() and opcion_destino_failover_form.is_valid():
            destino_personalizado = form.save()
            nodo_destino_personalizado = DestinoEntrante.crear_nodo_ruta_entrante(
                destino_personalizado)
            opcion_destino_failover_form.instance.destino_anterior = nodo_destino_personalizado
            opcion_destino_failover_form.save()
            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, destino_personalizado, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())
        return render(
            self.request, self.template_name,
            {'form': form, 'opcion_destino_failover_form': opcion_destino_failover_form})


class DestinoPersonalizadoUpdateView(DestinoPersonalizadoMixin, UpdateView):
    """Modifica Destino Personalizado"""
    model = DestinoPersonalizado
    fields = ('nombre', 'custom_destination')
    template_name = 'editar_destino_personalizado.html'
    message = _('Se ha modificado el nodo de Destino Personalizado con éxito')

    def get_context_data(self, **kwargs):
        context = super(DestinoPersonalizadoUpdateView, self).get_context_data(**kwargs)
        destino_personalizado = context['form'].instance
        nodo_destino_personalizado = DestinoEntrante.objects.get(
            object_id=destino_personalizado.pk,
            content_type=ContentType.objects.get_for_model(destino_personalizado))
        opcion_destino_failover_form = OpcionDestinoPersonalizadoForm(
            prefix='failover_form', instance=nodo_destino_personalizado.destinos_siguientes.first())
        context['opcion_destino_failover_form'] = opcion_destino_failover_form
        return context

    def form_valid(self, form):
        nodo_destino_personalizado = DestinoEntrante.objects.get(
            object_id=form.instance.pk,
            content_type=ContentType.objects.get_for_model(form.instance))
        opcion_destino_failover_form = OpcionDestinoPersonalizadoForm(
            self.request.POST, prefix='failover_form',
            instance=nodo_destino_personalizado.destinos_siguientes.first())
        if form.is_valid() and opcion_destino_failover_form.is_valid():
            destino_personalizado = form.save()
            opcion_destino_failover_form.save()
            # escribe el nodo creado y sus relaciones en asterisk
            sincronizador = self.get_sincronizador_de_configuracion()
            escribir_nodo_entrante_config(self, destino_personalizado, sincronizador)
            # muestra mensaje de éxito
            messages.add_message(self.request, messages.SUCCESS, self.message)
            return redirect(self.get_success_url())
        return render(
            self.request, self.template_name,
            {'form': form, 'opcion_destino_failover_form': opcion_destino_failover_form})


class DestinoPersonalizadoDeleteView(DestinoPersonalizadoMixin, DeleteNodoDestinoMixin, DeleteView):
    """Elimina Destino Personalizado"""
    model = DestinoPersonalizado
    template_name = 'eliminar_destino_personalizado.html'
