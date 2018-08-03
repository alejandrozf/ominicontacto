# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView

from configuracion_telefonia_app.forms import (RutaSalienteForm, TroncalSIPForm, RutaEntranteForm,
                                               PatronDeDiscadoFormset, OrdenTroncalFormset,
                                               OpcionDestinoIVRFormset, IVRForm,
                                               ValidacionTiempoFormset,
                                               OpcionDestinoValidacionFechaHoraFormset)
from configuracion_telefonia_app.models import (RutaSaliente, RutaEntrante, TroncalSIP,
                                                OrdenTroncal, DestinoEntrante, IVR, OpcionDestino,
                                                GrupoHorario, ValidacionFechaHora)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk, RestablecerConfiguracionTelefonicaError,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk,
    SincronizadorDeConfiguracionRutaEntranteAsterisk,
    SincronizadorDeConfiguracionIVRAsterisk,
    SincronizadorDeConfiguracionValidacionFechaHoraAsterisk,
    SincronizadorDeConfiguracionGrupoHorarioAsterisk
)


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
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
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
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
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
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
                   "con el siguiente error: {0} .".format(e))
        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )


def escribir_nodo_entrante_config(self, nodo_destino_entrante, sincronizador):
    try:
        sincronizador.regenerar_asterisk(nodo_destino_entrante)
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
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
    except RestablecerConfiguracionTelefonicaError, e:
        message = ("<strong>¡Cuidado!</strong> "
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
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> "
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
                    except RestablecerConfiguracionTelefonicaError, e:
                        message = ("<strong>¡Cuidado!</strong> "
                                   "con el siguiente error: {0} .".format(e))
                        messages.add_message(
                            self.request,
                            messages.WARNING,
                            message,
                        )
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

    def form_valid(self, form):
        return self.process_in_form_valid(form)


class TroncalSIPUpdateView(TroncalSIPMixin, UpdateView):
    model = TroncalSIP
    form_class = TroncalSIPForm
    template_name = 'base_create_update_form.html'

    def form_valid(self, form):
        return self.process_in_form_valid(form, update=True)


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
    paginate_by = 40
    context_object_name = 'rutas_salientes'
    template_name = 'lista_rutas_salientes.html'
    ordering = ['id']


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
            # TODO: usar el sincronizador correspondiente
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
        return reverse('lista_rutas_entrantes')

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


class RutaEntranteDeleteView(DeleteView):
    """Vista para eliminar una ruta entrante"""
    model = RutaEntrante
    success_url = reverse_lazy('lista_rutas_entrantes')
    template_name = 'eliminar_ruta_entrante.html'
    context_object_name = 'ruta_entrante'

    def get_object(self, queryset=None):
        return RutaEntrante.objects.get(pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        try:
            sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
            sincronizador.eliminar_y_regenerar_asterisk(self.get_object())
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> "
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
            repr_nombre = nodo_entrante.__unicode__()
            pk = nodo_entrante.pk
            data.append({'nombre': repr_nombre, 'id': pk})
        return JsonResponse(data, safe=False)


class IVRMixin(object):
    def get_success_url(self):
        return reverse('lista_ivrs')

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
            return redirect('lista_ivrs')
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
            return redirect('lista_ivrs')
        return render(
            self.request, 'editar_ivr.html',
            {'form': form, 'opcion_destino_formset': opcion_destino_formset})


class IVRContentCreateView(IVRCreateView):
    """Vista para crear un nodo de tipo IVR para solo renderizando el contenido
    del formulario
    """
    template_name = "content_ivr.html"


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
            except RestablecerConfiguracionTelefonicaError, e:
                message = ("<strong>¡Cuidado!</strong> con el siguiente error: {0} .".format(e))
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
    success_url = reverse_lazy('lista_grupos_horarios')
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
    success_url = reverse_lazy('lista_grupos_horarios')
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
    success_url = reverse_lazy('lista_grupos_horarios')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            sincronizador = SincronizadorDeConfiguracionGrupoHorarioAsterisk()
            sincronizador.eliminar_y_regenerar_asterisk(self.object)
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> con el siguiente error: {0} .".format(e))
            messages.add_message(self.request, messages.WARNING, message)
        if self.object.validaciones_fecha_hora.count() > 0:
            message = (
                _('No se puede eliminar un Grupo Horario utilizado en una Validacion Fecha Hora'))
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
        return reverse('lista_validaciones_fecha_hora')

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
    template_name = "crear_validacion_fecha_hora.html"
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
            DestinoEntrante.objects.get(
                object_id=validacion.pk, content_type=ContentType.objects.get_for_model(validacion))
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
        raise NotImplemented()

    def get_sincronizador_de_configuracion(self):
        raise NotImplemented()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        nodo = DestinoEntrante.get_nodo_ruta_entrante(self.object)
        if nodo.es_destino_en_flujo_de_llamada():
            message = (self.imposible_eliminar)
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())
        return super(DeleteNodoDestinoMixin, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        nodo = DestinoEntrante.get_nodo_ruta_entrante(self.object)
        if nodo.es_destino_en_flujo_de_llamada():
            messages.error(request, self.imposible_eliminar)
            return redirect(self.url_eliminar_name, self.get_object().id)

        try:
            sincronizador = self.get_sincronizador_de_configuracion()

            sincronizador.eliminar_y_regenerar_asterisk(self.get_object())
        except RestablecerConfiguracionTelefonicaError, e:
            message = ("<strong>¡Cuidado!</strong> "
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
