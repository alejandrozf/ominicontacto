# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

# TODO: Refactorizar las vistas en módulos mas pequeños y borrar este.

from __future__ import unicode_literals

import logging

from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    View, ListView, CreateView, UpdateView,
    DeleteView, TemplateView)
from configuracion_telefonia_app.forms import (
    TroncalSIPForm, IdentificadorClienteForm,
    OpcionDestinoValidacionFechaHoraFormset, OpcionDestinoPersonalizadoForm)
from configuracion_telefonia_app.models import (
    TroncalSIP, OrdenTroncal, DestinoEntrante,
    OpcionDestino, ValidacionFechaHora, IdentificadorCliente,
    DestinoPersonalizado)
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTroncalSipEnAsterisk, RestablecerConfiguracionTelefonicaError,
    SincronizadorDeConfiguracionValidacionFechaHoraAsterisk,
    SincronizadorDeConfiguracionIdentificadorClienteAsterisk,
    SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk
)
from ominicontacto_app.services.asterisk.trunk_status import TrunkStatusMonitor

from utiles_globales import obtener_paginas

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
        return super(TroncalSIPMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_troncal_sip', args=(1,))


class TroncalSIPListView(ListView):
    """Vista para listar los Sip Trunks"""
    model = TroncalSIP
    paginate_by = 40
    template_name = 'lista_troncal_sip.html'

    def get_context_data(self, **kwargs):
        context = super(TroncalSIPListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        trunks = context['page_obj'].object_list
        trunk_status_service = TrunkStatusMonitor()
        trunk_status_service.set_trunks_statuses(trunks)
        return context


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


class RutaSalienteListView(TemplateView):
    """Lista todas las rutas salientes"""
    template_name = "lista_rutas_salientes.html"


class RutaEntranteListView(TemplateView):
    """Lista todas las rutas entrantes"""
    template_name = "lista_rutas_entrantes.html"


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


class IVRListView(TemplateView):
    """Lista todos los nodos de tipo IVR"""
    template_name = "lista_ivrs.html"


class GrupoHorarioListView(TemplateView):
    """Lista los grupos horarios existentes"""
    template_name = "lista_grupos_horarios.html"


class ValidacionFechaHoraListView(ListView):
    """Lista los nodos de validación fecha/hora existentes"""
    model = ValidacionFechaHora
    template_name = 'lista_validaciones_fecha_hora.html'
    context_object_name = 'validaciones_fecha_hora'
    paginate_by = 40
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(ValidacionFechaHoraListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        return context


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
            if form.changed_data == ['nombre']:
                # si el nombre cambio actualizamos el nombre del destino entrante
                nodo_validacion = DestinoEntrante.get_nodo_ruta_entrante(validacion)
                nodo_validacion.nombre = validacion.nombre
                nodo_validacion.save()
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
    ERROR_DESTINO_LINEA = _("No se puede eliminar la campaña. Es usada como destino de las "
                            "siguientes Lineas de Whatsapp: {0}")

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
        lineas_whatsapp = nodo.lineas_destino_whatsapp()
        if lineas_whatsapp:
            permitido_eliminar = False
            nombres_lineas = lineas_whatsapp.values_list('nombre', flat=True)
            message = self.ERROR_DESTINO_LINEA.format(", ".join(nombres_lineas))
        elif nodo.es_destino_en_flujo_de_llamada():
            message = self.imposible_eliminar
            permitido_eliminar = False
        elif nodo.es_destino_failover():
            permitido_eliminar = False
            campanas_failover = nodo.campanas_destino_failover.values_list('name', flat=True)
            imposible_failover = _(
                'No se puede eliminar la campaña. Es usada como destino failover de las campañas:'
                ' {0}').format(", ".join(campanas_failover))
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
        lineas_whatsapp = nodo.lineas_destino_whatsapp()
        if lineas_whatsapp:
            permitido_eliminar = False
            nombres_lineas = lineas_whatsapp.values_list('nombre', flat=True)
            msg = self.ERROR_DESTINO_LINEA.format(", ".join(nombres_lineas))
            messages.error(request, msg)
        elif nodo.es_destino_en_flujo_de_llamada():
            permitido_eliminar = False
            messages.error(request, self.imposible_eliminar)
        elif nodo.es_destino_failover():
            permitido_eliminar = False
            campanas_failover = nodo.campanas_destino_failover.values_list('nombre', flat=True)
            imposible_failover = _(
                'No se puede eliminar la campaña. Es usada como destino failover de las campañas:'
                ' {0}').format(", ".join(campanas_failover))
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

    def get_context_data(self, **kwargs):
        context = super(IdentificadorClienteListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        return context


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

    def get_context_data(self, **kwargs):
        context = super(DestinoPersonalizadoListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        return context


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
            nodo_destino_personalizado.nombre = destino_personalizado.nombre
            nodo_destino_personalizado.save()
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
