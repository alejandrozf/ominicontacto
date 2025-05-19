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

"""
Vista para administrar el modelo Campana de tipo dialer
Observacion se copiaron varias vistas del modulo views_campana
"""

from functools import partial

from django.db import transaction
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView, FormView, CreateView, UpdateView, View

from constance import config as config_constance

from ominicontacto_app.models import Campana, ReglaIncidenciaPorCalificacion, ReglasIncidencia
from ominicontacto_app.services.dialer.campana_wombat import WombatDialerError
from ominicontacto_app.services.dialer import wombat_habilitado, get_dialer_service
from ominicontacto_app.services.dialer.wombat_api import WombatReloader
from ominicontacto_app.forms.base import (
    UpdateBaseDatosForm, ReglaIncidenciaPorCalificacionForm, ReglasIncidenciaForm)
from ominicontacto_app.views_campana import CampanaSupervisorUpdateView, CampanasDeleteMixin
from requests.exceptions import RequestException

from itertools import chain
import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaDialerListView(ListView):
    """
    Esta vista lista los objetos Campana de type dialer
    Vista copiada
    """

    template_name = 'campanas/campana_dialer/campana_list.html'
    context_object_name = 'campanas'
    model = Campana

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerListView, self).get_context_data(
            **kwargs)
        campanas = Campana.objects.obtener_campanas_dialer().select_related('queue_campana')
        # Filtra las campanas de acuerdo al usuario logeado si tiene permiso sobre
        # las mismas
        if self.request.user.is_authenticated and self.request.user and \
                not self.request.user.get_is_administrador():
            user = self.request.user
            campanas = Campana.objects.obtener_campanas_asignadas_o_creadas_by_user(campanas, user)

        # dialer_service = get_dialer_service
        # error_finalizadas = dialer_service.chequear_campanas_finalizada_eliminarlas(    ???
        #     campanas.filter(estado=Campana.ESTADO_ACTIVA))                              ???
        # if error_finalizadas:                                                           ???
        #     messages.add_message(self.request, messages.WARNING, error_finalizadas)     ???

        context['campanas'] = campanas
        context['inactivas'] = campanas.filter(estado=Campana.ESTADO_INACTIVA)
        context['pausadas'] = campanas.filter(estado=Campana.ESTADO_PAUSADA)
        context['activas'] = campanas.filter(estado=Campana.ESTADO_ACTIVA)
        context['borradas'] = campanas.filter(estado=Campana.ESTADO_BORRADA,
                                              oculto=False)
        context['finalizadas'] = campanas.filter(estado=Campana.ESTADO_FINALIZADA)

        context['campanas'] = context['campanas'].order_by("-id")
        context['inactivas'] = context['inactivas'].order_by("-id")
        context['pausadas'] = context['pausadas'].order_by("-id")
        context['activas'] = context['activas'].order_by("-id")
        context['borradas'] = context['borradas'].order_by("-id")
        context['finalizadas'] = context['finalizadas'].order_by("-id")

        context['canales_en_uso'] = Campana.objects.obtener_canales_dialer_en_uso()

        context['wombat_reload_enabled'] = False
        if wombat_habilitado():
            context['wombat_reload_enabled'] = config_constance.WOMBAT_DIALER_ALLOW_REFRESH
            if config_constance.WOMBAT_DIALER_ALLOW_REFRESH:
                context['wombat_state'] = config_constance.WOMBAT_DIALER_STATE
                if config_constance.WOMBAT_DIALER_STATE == WombatReloader.STATE_READY:
                    uptime = now() - config_constance.WOMBAT_DIALER_UP_SINCE
                    context['wombat_uptime'] = str(uptime).split('.')[0]
        return context


class PlayCampanaDialerView(View):
    """
    Esta vista actualiza la campañana activándola.
    """
    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_pk'])
        try:
            dialer_service = get_dialer_service()
            dialer_service.iniciar_campana(campana)
            campana.play()
            message = _(u'<strong>Operación Exitosa!</strong>\
                        Se llevó a cabo con éxito la activación de\
                        la Campaña.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        except (WombatDialerError, RequestException) as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: ") + "{0} .".format(e)
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class PausarCampanaDialerView(View):
    """
    Esta vista actualiza la campañana pausandola.
    """

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_pk'])
        try:
            dialer_service = get_dialer_service()
            dialer_service.pausar_campana(campana)
            campana.pausar()
            message = _('<strong>Operación Exitosa!</strong>\
                         Se llevó a cabo con éxito la pausa de\
                         la Campaña.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        except (WombatDialerError, RequestException) as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: ") + "{0} .".format(e)
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )

        return HttpResponseRedirect(reverse('campana_dialer_list'))


class ActivarCampanaDialerView(View):
    """
    Esta vista actualiza la campañana activándola.
    """

    def post(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=request.POST['campana_pk'])
        try:
            dialer_service = get_dialer_service()
            dialer_service.reanudar_campana(campana)
            campana.activar()
            message = _('<strong>Operación Exitosa!</strong>\
                         Se llevó a cabo con éxito la activación dela Campaña.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        except (WombatDialerError, RequestException) as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: ") + "{0} .".format(e)
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class CampanaDialerDeleteView(CampanasDeleteMixin, DeleteView):
    """
    Esta vista se encarga de la eliminación de una campana
    """
    model = Campana
    template_name = 'campanas/campana_dialer/delete_campana.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        dialer_service = get_dialer_service()
        # remueve campana de wombat
        remover = dialer_service.eliminar_campana(self.object)
        if not remover:
            message = _("<strong>Operación Errónea!</strong> "
                        "No se pudo eliminar la campana {0} del discador").format(
                            self.object.nombre)
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            super(CampanaDialerDeleteView, self).delete(request, *args, **kwargs)
            self.object.remover()
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_success_url(self):
        return reverse('campana_dialer_list')


class OcultarCampanaDialerView(View):
    """
    Esta vista actualiza la campañana ocultandola.
    """

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.ocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class DesOcultarCampanaDialerView(View):
    """
    Esta vista actualiza la campañana haciendola visible.
    """

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        campana.desocultar()
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class UpdateBaseDatosDialerView(FormView):
    """
    Esta vista actualiza la base de datos de una campana y sincroniza la base de datos
    /lista en wombat
    """

    model = Campana
    context_object_name = 'campana'
    form_class = UpdateBaseDatosForm
    template_name = 'base_create_update_form.html'

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_form(self):
        self.form_class = self.get_form_class()
        self.object = self.get_object()
        metadata = self.object.bd_contacto.get_metadata()
        nombres_de_columnas = metadata.nombres_de_columnas_de_datos
        tts_choices = zip(nombres_de_columnas, nombres_de_columnas)
        return self.form_class(tts_choices=tts_choices, **self.get_form_kwargs())

    def form_valid(self, form):
        evitar_duplicados = form.cleaned_data.get('evitar_duplicados')
        evitar_sin_telefono = form.cleaned_data.get('evitar_sin_telefono')
        prefijo_discador = form.cleaned_data.get('prefijo_discador')
        columnas = form.cleaned_data.get('telefonos')
        bd_contacto = form.cleaned_data.get('bd_contacto')
        self.object = self.get_object()
        base_actual = self.object.bd_contacto
        error = base_actual.validar_bd_de_reemplazo(bd_contacto)
        if error:
            return self.form_invalid(form, error=error)
        if self.object.bd_contacto == bd_contacto:
            message = _('Atención!\
                         Ud ha escogido la misma base de datos, corre riesgo de calificar los'
                        ' mismos contactos pisando la calificación previa.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )

        params = {
            'telefonos': columnas,
            'evitar_duplicados': evitar_duplicados,
            'evitar_sin_telefono': evitar_sin_telefono,
            'prefijo_discador': prefijo_discador
        }
        with transaction.atomic():
            self.object.bd_contacto = bd_contacto
            self.object.estado = Campana.ESTADO_INACTIVA
            self.object.save()
            if wombat_habilitado():
                # Intento cambiar la BD en wombat como parte de la transaccion
                self._cambiar_bd_contactos_en_dialer(params)

        # Cambio BD en OMniDialer una vez que ya se cambió en base
        if not wombat_habilitado():
            transaction.on_commit(partial(self._cambiar_bd_contactos_en_dialer, params))

        message = _('Operación Exitosa!\
                     Se llevó a cabo con éxito el cambio de base de datos.')

        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )

        return redirect(self.get_success_url())

    def _cambiar_bd_contactos_en_dialer(self, params):
        dialer_service = get_dialer_service()
        dialer_service.cambiar_bd_contactos(self.object, params)

    def form_invalid(self, form, error=None):

        message = _('<strong>Operación Errónea!</strong> \
                     La base de datos es erronea. ') + '{0}'.format(error)

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse('campana_dialer_list')


class CampanaDialerSupervisorUpdateView(CampanaSupervisorUpdateView):
    """
    Esta vista agrega supervisores a una campana dialer
    logica copiado para campana_preview
    """

    def get_success_url(self):
        return reverse('campana_dialer_list')

    def _get_redirecccion_campana_erronea(self):
        return redirect('campana_dialer_list')


class CampanaDialerBorradasListView(CampanaDialerListView):
    """
    Vista que lista las campañas dialer pero de incluyendo las borradas ocultas
    """

    template_name = 'campanas/campana_dialer/campanas_borradas.html'

    def get_context_data(self, **kwargs):
        context = super(CampanaDialerBorradasListView, self).get_context_data(**kwargs)
        context['borradas'] = context['campanas'].filter(estado=Campana.ESTADO_BORRADA)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(CampanaDialerBorradasListView, self).get(request, *args, **kwargs)
        else:
            return JsonResponse({'result': 'desconectado'})


class FinalizarCampanasActivasView(View):
    """
    Esta vista finaliza las campanas activas de acuerdo si tienen contactos pendientes en wombat
    """

    def post(self, request, *args, **kwargs):
        campanas = Campana.objects.obtener_campanas_dialer().filter(estado=Campana.ESTADO_ACTIVA)
        dialer_service = get_dialer_service()
        error_finalizadas = dialer_service.finalizar_campanas_sin_llamadas_pendientes(campanas)
        if error_finalizadas:
            messages.add_message(self.request, messages.WARNING, error_finalizadas)
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class FinalizarCampanaDialerView(View):
    """
    Esta vista actualiza la campañana finalizandola.
    """
    def post(self, request, *args, **kwargs):
        campana_id = request.POST.get('campana_pk')
        campana = Campana.objects.get(pk=campana_id)
        try:
            dialer_service = get_dialer_service()
            dialer_service.terminar_campana(campana)
            campana.finalizar()
            message = _('<strong>Operación Exitosa!</strong>\
                             Se llevó a cabo con éxito la finalización de\
                             la Campaña.')

            messages.add_message(
                self.request,
                messages.SUCCESS,
                message,
            )
        except (WombatDialerError, RequestException) as e:
            message = _("<strong>¡Cuidado!</strong> "
                        "con el siguiente error: ") + "{0} .".format(e)
            messages.add_message(
                self.request,
                messages.WARNING,
                message,
            )
        return HttpResponseRedirect(reverse('campana_dialer_list'))


class VerificarPremisoEnCampanaMixin():

    def _user_tiene_permiso_en_campana(self, campana):
        user = self.request.user
        if user.get_is_administrador():
            return True
        return campana.reported_by == user or campana.supervisors.filter(id=user.id).exists()


class ReglasDeIncidenciaDeCalificacionesListView(ListView, VerificarPremisoEnCampanaMixin):
    template_name = 'campanas/campana_dialer/reglas_incidencia_calificacion_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaDeCalificacionesListView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReglasDeIncidenciaDeCalificacionesListView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        return context

    def get_queryset(self):
        """Returns user ordernado por id"""
        qs = chain(
            self.campana.reglas_incidencia.all(),
            ReglaIncidenciaPorCalificacion.objects.filter(
                opcion_calificacion__campana_id=self.campana.id))
        return qs


class ReglasDeIncidenciaDeCalificacionesDeleteView(DeleteView, VerificarPremisoEnCampanaMixin):
    model = ReglaIncidenciaPorCalificacion
    template_name = 'campanas/campana_dialer/reglas_incidencia_calificacion_delete.html'

    def dispatch(self, request, *args, **kwargs):
        regla = self.get_object()
        self.campana = regla.opcion_calificacion.campana
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaDeCalificacionesDeleteView, self).dispatch(
            request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        dialer_service = get_dialer_service()
        remover = dialer_service.eliminar_regla_de_incidencia(self.object, es_de_calificacion=True)
        if not remover:
            message = _("<strong>Operación Errónea!</strong> "
                        "No se pudo eliminar la Regla de Incidencia por calificación: {0}").format(
                            self.object.opcion_calificacion.nombre)
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            super(ReglasDeIncidenciaDeCalificacionesDeleteView, self).delete(
                request, *args, **kwargs)
            messages.success(request, _('Regla de incidencia eliminada.'))
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})


class ReglasDeIncidenciaDeCalificacionesCreateView(CreateView, VerificarPremisoEnCampanaMixin):
    model = ReglaIncidenciaPorCalificacion
    template_name = 'base_create_update_form.html'
    form_class = ReglaIncidenciaPorCalificacionForm

    def dispatch(self, request, *args, **kwargs):
        self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaDeCalificacionesCreateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReglasDeIncidenciaDeCalificacionesCreateView, self).get_form_kwargs()
        kwargs['campana'] = self.campana
        return kwargs

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})

    def form_valid(self, form):
        regla = form.save(commit=False)
        try:
            dialer_service = get_dialer_service()
            dialer_service.crear_regla_de_incidencia_de_calificacion(regla)
        except WombatDialerError as e:
            error_message = _("Error al registrar regla de incidencia: ") + "{0} .".format(e)
            logger.error(error_message)
            messages.error(_('No se pudo guardar la regla de incidencia.'))
            return self.form_invalid(form)

        regla.save()

        return super(ReglasDeIncidenciaDeCalificacionesCreateView, self).form_valid(form)


class ReglasDeIncidenciaDeCalificacionesUpdateView(UpdateView, VerificarPremisoEnCampanaMixin):
    model = ReglaIncidenciaPorCalificacion
    template_name = 'base_create_update_form.html'
    form_class = ReglaIncidenciaPorCalificacionForm

    def dispatch(self, request, *args, **kwargs):
        regla = self.get_object()
        self.wombat_id_anterior = regla.wombat_id
        self.campana = regla.opcion_calificacion.campana
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaDeCalificacionesUpdateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReglasDeIncidenciaDeCalificacionesUpdateView, self).get_form_kwargs()
        kwargs['campana'] = self.campana
        return kwargs

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})

    def form_valid(self, form):
        regla = form.save(commit=False)
        try:
            dialer_service = get_dialer_service()
            editado = dialer_service.editar_regla_de_incidencia(regla, self.campana,
                                                                self.wombat_id_anterior,
                                                                es_de_calificacion=True)
            if not editado:
                messages.error(_('No se pudo guardar la regla de incidencia.'))
                return self.form_invalid(form)
        except WombatDialerError as e:
            error_message = _("Error al editar regla de incidencia: ") + "{0} .".format(e)
            logger.error(error_message)
            messages.error(_('No se pudo guardar la regla de incidencia.'))
            return self.form_invalid(form)

        regla.save()

        return super(ReglasDeIncidenciaDeCalificacionesUpdateView, self).form_valid(form)


class ReglasDeIncidenciaDeleteView(DeleteView, VerificarPremisoEnCampanaMixin):
    model = ReglasIncidencia
    template_name = 'campanas/campana_dialer/reglas_incidencia_calificacion_delete.html'

    def dispatch(self, request, *args, **kwargs):
        regla = self.get_object()
        self.campana = regla.campana
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaDeleteView, self).dispatch(
            request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        dialer_service = get_dialer_service()
        remover = dialer_service.eliminar_regla_de_incidencia(self.object, es_de_calificacion=False)
        if not remover:
            message = _("<strong>Operación Errónea!</strong> "
                        "No se pudo eliminar la Regla de Incidencia: {0}").format(
                            self.object.estado)
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            super(ReglasDeIncidenciaDeleteView, self).delete(
                request, *args, **kwargs)
            messages.success(request, _('Regla de incidencia eliminada.'))
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})


class ReglasDeIncidenciaCreateView(CreateView, VerificarPremisoEnCampanaMixin):
    model = ReglasIncidencia
    template_name = 'base_create_update_form.html'
    form_class = ReglasIncidenciaForm

    def dispatch(self, request, *args, **kwargs):
        self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaCreateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReglasDeIncidenciaCreateView, self).get_form_kwargs()
        kwargs['campana'] = self.campana
        return kwargs

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})

    def form_valid(self, form):
        form.instance.campana = self.campana
        regla = form.save(commit=False)
        try:
            dialer_service = get_dialer_service()
            dialer_service.crear_regla_de_incidencia(regla)
        except WombatDialerError as e:
            error_message = _("Error al registrar regla de incidencia: ") + "{0} .".format(e)
            logger.error(error_message)
            messages.error(_('No se pudo guardar la regla de incidencia.'))
            return self.form_invalid(form)

        regla.save()

        return super(ReglasDeIncidenciaCreateView, self).form_valid(form)


class ReglasDeIncidenciaUpdateView(UpdateView, VerificarPremisoEnCampanaMixin):
    model = ReglasIncidencia
    template_name = 'base_create_update_form.html'
    form_class = ReglasIncidenciaForm

    def dispatch(self, request, *args, **kwargs):
        regla = self.get_object()
        self.wombat_id_anterior = regla.wombat_id
        self.estado_wombat_anterior = regla.get_estado_wombat()
        self.campana = regla.campana
        if not self._user_tiene_permiso_en_campana(self.campana):
            message = _('No tiene permiso para editar esta Campaña.')
            messages.warning(request, message)
            return redirect('campana_dialer_list')

        return super(ReglasDeIncidenciaUpdateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReglasDeIncidenciaUpdateView, self).get_form_kwargs()
        kwargs['campana'] = self.campana
        return kwargs

    def get_success_url(self):
        return reverse('disposition_incidence_list', kwargs={'pk_campana': self.campana.id})

    def form_valid(self, form):
        regla = form.save(commit=False)
        try:
            dialer_service = get_dialer_service()
            editado = dialer_service.editar_regla_de_incidencia(regla, self.campana,
                                                                self.wombat_id_anterior,
                                                                self.estado_wombat_anterior,
                                                                es_de_calificacion=False)
            if not editado:
                messages.error(_('No se pudo guardar la regla de incidencia.'))
                return self.form_invalid(form)
        except WombatDialerError as e:
            error_message = _("Error al editar regla de incidencia: ") + "{0} .".format(e)
            logger.error(error_message)
            messages.error(_('No se pudo guardar la regla de incidencia.'))
            return self.form_invalid(form)

        regla.save()

        return super(ReglasDeIncidenciaUpdateView, self).form_valid(form)
