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

"""Vista para administrar el modelo Campana de tipo entrantes"""

from __future__ import unicode_literals

from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (ListView, UpdateView, DeleteView, FormView)
from django.views.generic.base import RedirectView
from django.utils.translation import gettext_lazy as _

from ominicontacto_app.forms import CampanaSupervisorUpdateForm, ConfiguracionDeAgentesDeCampanaForm
from ominicontacto_app.models import Campana, SupervisorProfile, ConfiguracionDeAgentesDeCampana
from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk.redis_database import CampanaFamily

from configuracion_telefonia_app.views.base import DeleteNodoDestinoMixin, SincronizadorDummy

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanasDeleteMixin(object):
    """
    Encapsula comportamiento común a todas las campanas en el momento de
    eliminar
    """
    nodo_eliminado = _(u'<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # realizamos la eliminacion de la queue
        self.object.remover()
        # actualizamos el archivo de dialplan
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError as e:
            message = _("<strong>Operación Errónea!</strong> "
                        "No se pudo confirmar la creación del dialplan  "
                        "al siguiente error: {0}".format(e))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )

        messages.add_message(
            self.request,
            messages.SUCCESS,
            self.nodo_eliminado,
        )


class CampanaListView(ListView):
    """
    Esta vista lista los objetos Campana de tipo Entrantes
    """

    template_name = 'campanas/campana_entrante/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaListView, self).get_context_data(
            **kwargs)
        campanas = Campana.objects.obtener_campanas_entrantes().select_related('bd_contacto')
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_asignadas_o_creadas_by_user(campanas, user)
        # ordenar las campanas por ID
        context['campanas'] = campanas.order_by('id')
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA).order_by('id')
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False).order_by('id')
        return context


class CampanaDeleteView(DeleteNodoDestinoMixin, CampanasDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    # TODO: realizar refactor aquí, la vista de eliminación no debería tener dos métodos
    # 'delete'
    model = Campana
    template_name = 'campanas/campana_entrante/delete_campana.html'
    imposible_eliminar = _('No se puede eliminar una Campaña que es destino en un flujo de llamada')
    nodo_eliminado = _(u'<strong>Operación Exitosa!</strong>\
        Se llevó a cabo con éxito la eliminación de la campana.')
    url_eliminar_name = 'campana_elimina'

    def delete(self, request, *args, **kwargs):
        super(CampanaDeleteView, self).delete(request, *args, **kwargs)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        # No se puede volver a borrar una campaña.
        return Campana.objects.exclude(
            estado=Campana.ESTADO_BORRADA).get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_list')

    def get_sincronizador_de_configuracion(self):
        return SincronizadorDummy()


class OcultarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    pattern_name = 'campana_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_list'))


class DesOcultarCampanaView(RedirectView):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    pattern_name = 'campana_list'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_list'))


class CampanaSupervisorUpdateView(UpdateView):
    """
    Esta vista agrega supervisores a una campana
    """

    template_name = 'campanas/campana_dialer/campana_supervisors.html'
    model = Campana
    context_object_name = 'campana'
    form_class = CampanaSupervisorUpdateForm

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self):
        self.form_class = self.get_form_class()
        supervisores = SupervisorProfile.objects.exclude(borrado=True)
        supervisors_choices = [(supervisor.user.pk, ": ".join([supervisor.user.get_username(),
                                supervisor.user.get_full_name()])) for supervisor in
                               supervisores]
        kwargs = self.get_form_kwargs()
        kwargs['supervisors_choices'] = supervisors_choices
        kwargs['supervisors_required'] = True
        return self.form_class(**kwargs)

    def get_success_url(self):
        return reverse('campana_list')


class CampanaBorradasListView(CampanaListView):
    """
    Vista que lista las campañas entrantes pero de incluyendo las borradas ocultas
    """

    template_name = 'campanas/campana_entrante/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(CampanaBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})


class ConfiguracionDeAgentesDeCampanaView(FormView):
    form_class = ConfiguracionDeAgentesDeCampanaForm
    template_name = 'campanas/configuracion_de_agentes_de_campana.html'

    def dispatch(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        self.campana = get_object_or_404(Campana, pk=pk_campana)
        if not self.request.user.get_is_administrador():
            supervisor_profile = self.request.user.get_supervisor_profile()
            if not supervisor_profile.esta_asignado_a_campana(self.campana):
                msg = _('No tiene permiso para editar esa campaña.')
                messages.error(self.request, msg)
                redirect('index')
        return super(ConfiguracionDeAgentesDeCampanaView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ConfiguracionDeAgentesDeCampanaView, self).get_form_kwargs()
        kwargs['campana_type'] = self.campana.type
        try:
            kwargs['instance'] = self.campana.configuracion_de_agentes
        except ConfiguracionDeAgentesDeCampana.DoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        configuracion = form.save(commit=False)
        configuracion.campana = self.campana
        configuracion.save()
        url_por_tipo = {
            Campana.TYPE_MANUAL: 'campana_manual_list',
            Campana.TYPE_DIALER: 'campana_dialer_list',
            Campana.TYPE_ENTRANTE: 'campana_list',
            Campana.TYPE_PREVIEW: 'campana_preview_list'
        }
        campana_service = CampanaFamily()
        campana_service.regenerar_family(self.campana)
        return redirect(url_por_tipo[self.campana.type])
