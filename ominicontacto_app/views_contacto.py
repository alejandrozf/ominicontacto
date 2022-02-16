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

"""
Vistas para el modelo de Contacto de la base de datos
"""

from __future__ import unicode_literals

import json

from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, CreateView, UpdateView, FormView, DeleteView,
                                  TemplateView)
from django.utils.translation import ugettext as _
from django.db.models import Q
from utiles_globales import obtener_paginas

from ominicontacto_app.forms import (BusquedaContactoForm, FormularioCampanaContacto,
                                     FormularioNuevoContacto, EscogerCampanaForm,
                                     BloquearCamposParaAgenteForm)
from ominicontacto_app.models import Campana, Contacto, BaseDatosContacto
from ominicontacto_app.services.click2call import Click2CallOriginator


URL_LISTA_CAMPANAS_POR_TIPO = {
    Campana.TYPE_ENTRANTE: 'campana_list',
    Campana.TYPE_MANUAL: 'campana_manual_list',
    Campana.TYPE_DIALER: 'campana_dialer_list',
    Campana.TYPE_PREVIEW: 'campana_preview_list',
}


class ContactoUpdateView(UpdateView):
    """Vista de agente para modificar un contacto"""
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = FormularioNuevoContacto

    def dispatch(self, request, *args, **kwargs):
        # Ver si el agente esta asignado a la campaña
        agente = self.request.user.get_agente_profile()
        id_campana = kwargs['pk_campana']
        self.campana = None
        queue_members = agente.get_campanas_activas_miembro().filter(
            queue_name__campana_id=id_campana)
        queue_member = queue_members.first()
        if not queue_member:
            message = _('Usted no tiene permiso para editar un contacto de esta campaña.')
            messages.warning(request, message)
            return redirect('contacto_list')

        self.campana = queue_member.queue_name.campana

        return super(ContactoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def get_form_kwargs(self):
        kwargs = super(ContactoUpdateView, self).get_form_kwargs()
        kwargs['campos_bloqueados'] = self.campana.get_campos_no_editables()
        kwargs['campos_ocultos'] = self.campana.get_campos_ocultos()
        return kwargs

    # TODO: Cuando cada base de datos solo pueda tener una campaña, se podrán mostrar
    #       los telefonos como click2call
    # def get_context_data(self, **kwargs):
    #     context = super(ContactoUpdateView, self).get_context_data(**kwargs)
    #     bd_metadata = self.object.bd_contacto.get_metadata()
    #     context['campos_telefono'] = bd_metadata.nombres_de_columnas_de_telefonos + ['telefono']
    #     return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.datos = form.get_datos_json()
        self.object.save()
        # TODO: OML-1016 - Ver si no hay que modificar datos en Wombat
        message = _('Se han guardado los cambios en el contacto.')
        messages.success(self.request, message)
        return super(ContactoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contacto_list')


class ContactoListView(FormView):
    """Vista que lista los contactos"""
    model = Contacto
    template_name = 'agente/contacto_list.html'

    form_class = EscogerCampanaForm

    def _obtener_campanas(self):
        agente = self.request.user.get_agente_profile()
        campanas_queues = agente.get_campanas_activas_miembro()
        ids_campanas = []
        for id_nombre in campanas_queues.values_list('id_campana', flat=True):
            split_id_nombre = id_nombre.split('_')
            id_campana = split_id_nombre[0]
            nombre_campana = '_'.join(split_id_nombre[1:])
            ids_campanas.append((id_campana, nombre_campana))
        return ids_campanas

    def get_form_kwargs(self):
        kwargs = super(ContactoListView, self).get_form_kwargs()
        ids_campanas = self._obtener_campanas()
        if ids_campanas:
            ids_campanas.insert(0, ('', '---------'))
        kwargs['campanas'] = ids_campanas
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ContactoListView, self).get_context_data(
            **kwargs)
        context['campanas'] = self._obtener_campanas()
        if not context.get('campana_nombre', False):
            context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        campana_pk = form.cleaned_data.get('campana')
        campana = Campana.objects.get(pk=campana_pk)
        total_contactos = campana.bd_contacto.contactos.count()
        total_no_calificados = campana.obtener_contactos_no_calificados().count()
        total_calificados = total_contactos - total_no_calificados
        bd_contacto = campana.bd_contacto
        bd_metadata = bd_contacto.get_metadata()
        bd_metadata_cols = " ".join(
            bd_metadata.nombres_de_columnas_de_datos)
        return self.render_to_response(
            self.get_context_data(
                form=form, campana=campana, total_contactos=total_contactos,
                total_no_calificados=total_no_calificados,
                total_calificados=total_calificados,
                bd_contacto=bd_contacto, bd_metadata=bd_metadata,
                bd_metadata_cols=bd_metadata_cols
            )
        )


class ContactosTelefonosRepetidosView(TemplateView):
    """Vista que muestra todos los contactos que comparten un número de teléfono en una campaña
    """

    template_name = 'agente/contactos_telefonos_repetidos.html'

    def get_context_data(self, **kwargs):
        context = super(ContactosTelefonosRepetidosView, self).get_context_data(**kwargs)
        pk_campana = kwargs.get('pk_campana', False)
        telefono = kwargs.get('telefono', False)
        call_data_json = kwargs.get('call_data_json', False)
        campana = get_object_or_404(Campana, pk=pk_campana)
        if call_data_json:
            context['call_data_json'] = call_data_json
            context['call_data'] = json.loads(call_data_json)

        context['campana'] = campana
        context['contactos'] = campana.bd_contacto.contactos.filter(telefono=telefono)
        return context


class ContactoBDContactoCreateView(CreateView):
    """Vista para agregar un contacto a una base de datos ya existente"""
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def dispatch(self, request, *args, **kwargs):
        self.campana = None
        if 'bd_contacto' in kwargs:
            try:
                self.bd_contacto = BaseDatosContacto.objects.get(pk=kwargs['bd_contacto'])
            except BaseDatosContacto.DoesNotExist:
                message = _('La base de datos no existe')
                messages.warning(request, message)
                return redirect('lista_base_datos_contacto', 1)
        if 'pk_campana' in kwargs:
            try:
                self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            except Campana.DoesNotExist:
                message = _('La campaña no existe')
                messages.warning(request, message)
                return redirect('index')
            if not self._user_tiene_permiso_en_campana(self.campana):
                message = _('No tiene permiso para agregar contactos a la Campaña.')
                messages.warning(request, message)
                return redirect(URL_LISTA_CAMPANAS_POR_TIPO[self.campana.type])
            self.bd_contacto = self.campana.bd_contacto

        return super(ContactoBDContactoCreateView, self).dispatch(request, *args, **kwargs)

    def _user_tiene_permiso_en_campana(self, campana):
        user = self.request.user
        if user.get_is_administrador():
            return True
        return campana.reported_by == user or campana.supervisors.filter(id=user.id).exists()

    def get_initial(self):
        initial = super(ContactoBDContactoCreateView, self).get_initial()
        initial.update({'bd_contacto': self.bd_contacto.id})

    def get_form_kwargs(self):
        kwargs = super(ContactoBDContactoCreateView, self).get_form_kwargs()
        kwargs['base_datos'] = self.bd_contacto
        return kwargs

    def form_valid(self, form):
        # TODO: Decidir si esto lo tiene que hacer el form o la vista
        self.object = form.save(commit=False)
        self.bd_contacto.cantidad_contactos += 1
        self.bd_contacto.save()
        self.object.datos = form.get_datos_json()
        self.object.save()

        # TODO: OML-1016
        # TODO: En caso de que la base corresponda a una campaña Dialer, agregar en Wombat

        # Si se agrega a una a una campaña Preview agregar AgenteEnContacto
        if self.campana is not None and self.campana.type == Campana.TYPE_PREVIEW:
            self.campana.adicionar_agente_en_contacto(self.object, -1)

        message = _('Contacto creado satisfactoriamente.')
        messages.success(self.request, message)

        return super(ContactoBDContactoCreateView, self).form_valid(form)

    def get_success_url(self):
        if self.campana is None:
            return reverse('lista_base_datos_contacto', kwargs={"page": 1})
        else:
            return reverse(URL_LISTA_CAMPANAS_POR_TIPO[self.campana.type])


class ContactoBDContactoListView(ListView):
    """Vista que lista los contactos de una base de datos"""
    model = Contacto
    template_name = 'base_datos_contacto/contacto_list_bd_contacto.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super(ContactoBDContactoListView, self).get_context_data(
            **kwargs)
        bd_contactos = BaseDatosContacto.objects.get(
            pk=self.kwargs['bd_contacto'])
        context['basedatoscontacto'] = bd_contactos
        metadata = bd_contactos.get_metadata()
        context['db_metadata'] = metadata
        context['db_metadata_cols'] = " ".join(
            metadata.nombres_de_columnas_de_datos)
        obtener_paginas(context, 7)
        return context

    def get_queryset(self):
        queryset = Contacto.objects.contactos_by_bd_contacto(
            self.kwargs['bd_contacto']).order_by('id')
        if 'search' in self.request.GET:
            search = self.request.GET.get('search')
            return queryset.filter(Q(telefono__icontains=search))
        else:
            return queryset


class ContactoBDContactoUpdateView(UpdateView):
    """Vista de Supervisor para modificar un contacto de la base de datos"""
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.datos = form.get_datos_json()
        self.object.save()
        # TODO: OML-1016 - Ver si no hay que modificar datos en Wombat
        return super(ContactoBDContactoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contacto_list_bd_contacto',
                       kwargs={'bd_contacto': self.object.bd_contacto.pk})


# TODO: Validar bien que se pueda borrar el contacto. Ver relaciones.
class ContactoBDContactoDeleteView(DeleteView):
    """
    Esta vista se encarga de la eliminación de un contacto
    """
    model = Contacto
    template_name = 'base_datos_contacto/delete_contacto.html'

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        base_datos_contactos = self.object.bd_contacto
        base_datos_contactos.cantidad_contactos -= 1
        base_datos_contactos.save()
        self.object.delete()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('contacto_list_bd_contacto',
                       kwargs={'bd_contacto': self.object.bd_contacto.pk})


class BloquearCamposParaAgenteFormView(FormView):
    """Vista para seleccionar los campos que un agente no puede editar"""
    form_class = BloquearCamposParaAgenteForm
    template_name = "campanas/bloquear_campos_para_agente.html"

    def dispatch(self, request, *args, **kwargs):
        # Ver que el supervisor tenga permiso sobre la campaña
        try:
            self.campana = Campana.objects.get(id=kwargs['pk_campana'])
        except Campana.DoesNotExist:
            message = _('Campaña inexistente')
            messages.error(request, message)
            return reverse('index')

        if not request.user.get_is_administrador():
            supervisor = request.user.get_supervisor_profile()
            if not (self.campana.reported_by == supervisor or supervisor.esta_asignado_a_campana(
                    self.campana)):
                message = _('No tiene permiso para editar esa campaña.')
                messages.error(request, message)
                return redirect(URL_LISTA_CAMPANAS_POR_TIPO[self.campana.type])

        return super(BloquearCamposParaAgenteFormView,
                     self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BloquearCamposParaAgenteFormView, self).get_form_kwargs()
        kwargs['lang'] = {'bloquear': _('Bloquear {0}'), 'ocultar': _('Ocultar {0}')}
        bd_metadata = self.campana.bd_contacto.get_metadata()
        kwargs['campos'] = bd_metadata.nombres_de_columnas
        kwargs['campo_telefono'] = bd_metadata.nombre_campo_telefono
        campos_bloqueados = self.campana.get_campos_no_editables()
        prefijo = BloquearCamposParaAgenteForm.PREFIJO_BLOQUEAR
        for campo in campos_bloqueados:
            kwargs['initial'][prefijo + campo] = True
        campos_ocultos = self.campana.get_campos_ocultos()
        prefijo = BloquearCamposParaAgenteForm.PREFIJO_OCULTAR
        for campo in campos_ocultos:
            kwargs['initial'][prefijo + campo] = True
        return kwargs

    def form_valid(self, form):
        campos_bloqueados = form.lista_campos_bloqueados
        self.campana.set_campos_no_editables(campos_bloqueados)
        campos_ocultos = form.lista_campos_ocultos
        self.campana.set_campos_ocultos(campos_ocultos)
        self.campana.save()
        message = _('Ningún campo ha quedado restringido ni oculto.')
        if campos_bloqueados:
            message = _("Campos restringidos: {0}").format(', '.join(campos_bloqueados))
            if campos_ocultos:
                message += _("<br> Campos ocultos: {0}").format(', '.join(campos_ocultos))
        messages.success(self.request, message)
        return redirect(URL_LISTA_CAMPANAS_POR_TIPO[self.campana.type])


# TODO: Verificar si se usa esta vista y el template
class CampanaBusquedaContactoFormView(FormView):
    """Vista realiza la busqueda de contacto en una campana dialer
    """
    form_class = BusquedaContactoForm
    template_name = 'contactos/busqueda_contacto.html'

    def get(self, request, *args, **kwargs):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
            campana.bd_contacto)
        return self.render_to_response(self.get_context_data(
            listado_de_contacto=listado_de_contacto))

    def get_context_data(self, **kwargs):
        context = super(CampanaBusquedaContactoFormView, self).get_context_data(
            **kwargs)
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['campana'] = campana
        return context

    def form_valid(self, form):
        filtro = form.cleaned_data.get('buscar')
        try:
            campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            listado_de_contacto = Contacto.objects.\
                contactos_by_filtro_bd_contacto(campana.bd_contacto, filtro)
        except Contacto.DoesNotExist:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))

        if listado_de_contacto:
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))
        else:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
            return self.render_to_response(self.get_context_data(
                form=form, listado_de_contacto=listado_de_contacto))


class FormularioSeleccionCampanaFormView(FormView):
    """Vista para seleccionar una campana a la cual se le agregar un nuevo contacto
    """
    form_class = FormularioCampanaContacto
    template_name = 'contactos/seleccion_campana_form.html'

    def dispatch(self, request, *args, **kwargs):
        agente = self.request.user.get_agente_profile()
        if not agente.get_campanas_activas_miembro():
            message = _("Este agente no esta asignado a ninguna campaña activa")
            messages.warning(self.request, message)
        return super(FormularioSeleccionCampanaFormView,
                     self).dispatch(request, *args, **kwargs)

    def get_form(self):
        self.form_class = self.get_form_class()
        if self.request.user.is_authenticated\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
            campanas = [queue.queue_name.campana
                        for queue in agente.get_campanas_activas_miembro()]

        campana_choice = [(campana.id, campana.nombre) for campana in campanas]
        return self.form_class(campana_choice=campana_choice, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = form.cleaned_data.get('campana')
        return HttpResponseRedirect(
            reverse('nuevo_contacto_campana', kwargs={"pk_campana": campana}))

    def get_success_url(self):
        reverse('view_blanco')


class FormularioNuevoContactoFormView(FormView):
    """
        Vista de Agente para agregar un nuevo contacto para la campana seleccionada
    """
    form_class = FormularioNuevoContacto
    template_name = 'contactos/nuevo_contacto_campana.html'

    def dispatch(self, request, *args, **kwargs):
        self.accion = self.kwargs.get('accion', 'calificar')
        self.campana = get_object_or_404(Campana, pk=self.kwargs.get('pk_campana', '0'))
        self.telefono = self.kwargs.get('telefono', '')
        return super(FormularioNuevoContactoFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FormularioNuevoContactoFormView, self).get_context_data(**kwargs)
        context['accion'] = self.accion
        return context

    def get_form_kwargs(self):
        kwargs = super(FormularioNuevoContactoFormView, self).get_form_kwargs()
        kwargs['initial']['telefono'] = self.kwargs.get('telefono', '')
        kwargs['base_datos'] = self.campana.bd_contacto
        kwargs['campos_bloqueados'] = self.campana.get_campos_no_editables()
        kwargs['campos_ocultos'] = self.campana.get_campos_ocultos()

        return kwargs

    def form_valid(self, form):
        contacto = form.save(commit=False)
        contacto.datos = form.get_datos_json()
        contacto.es_originario = False
        contacto.save()

        agente = self.request.user.get_agente_profile()

        # TODO: OML-1016 - Ver si hay que agregar el contacto en Wombat.

        if self.campana.type == Campana.TYPE_PREVIEW:
            # Se crea el agente en contacto únicamente para esta campaña, asignado a este agente.
            self.campana.adicionar_agente_en_contacto(
                contacto, agente_id=agente.id, es_originario=False)

        if self.accion == 'calificar':
            return HttpResponseRedirect(
                reverse('calificacion_formulario_update_or_create',
                        kwargs={"pk_campana": self.kwargs['pk_campana'],
                                "pk_contacto": contacto.pk}))
        else:
            click2call_type = 'contactos'
            if self.telefono:
                telefono = self.telefono

            originator = Click2CallOriginator()
            transaction.on_commit(lambda: originator.call_originate(
                agente, self.campana.id, str(self.campana.type),
                contacto.id, telefono, click2call_type))
            message = _("Contacto creado satisfactoriamente. Efectuando llamada.")
            messages.success(self.request, message)
            return super(FormularioNuevoContactoFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('view_blanco')


class IdentificarContactoView(FormView):
    """
    Vista para identificar Contactos de llamadas entrantes, manuales o redials.
    Si son de llamadas entrantes deben ir a calificar. Manuales y redials van a edicion del contacto
    con click to call.
    Si no se sabe el id del contacto:
    - Listar los contactos de la campaña que tengan ese teléfono en alguno de sus campos
    - Si viene un id de contacto de sugerencia (por redial) ofrecer el ultimo contacto llamado
    - Ofrecer buscar contacto
    - Ofrecer para crear un contacto nuevo
    """
    template_name = 'agente/identificar_contacto.html'
    form_class = BusquedaContactoForm

    def dispatch(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana', False)
        self.campana = get_object_or_404(Campana, pk=pk_campana)
        pk_campana = kwargs.get('pk_campana', False)
        # Validar formato de telefono??
        self.telefono = kwargs.get('telefono', False)
        self.call_data_json = kwargs.get('call_data_json', '')

        return super(IdentificarContactoView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(IdentificarContactoView, self).get_form_kwargs()
        kwargs['initial']['buscar'] = self.telefono
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(IdentificarContactoView, self).get_context_data(**kwargs)
        context['campana'] = self.campana
        bd_metadata = self.campana.bd_contacto.get_metadata()
        context['campos_bd'] = bd_metadata.nombres_de_columnas_de_datos[:3]
        context['telefono'] = self.telefono
        context['call_data_json'] = self.call_data_json
        if 'contactos_encontrados' in kwargs:
            context['contactos_busqueda'] = kwargs['contactos_encontrados']
        else:
            context['contactos_busqueda'] = Contacto.objects.contactos_by_filtro_bd_contacto(
                bd_contacto=self.campana.bd_contacto, filtro=self.telefono)
        return context

    def form_valid(self, form):
        buscar = form.cleaned_data.get('buscar', '')
        contactos_encontrados = Contacto.objects.contactos_by_filtro_bd_contacto(
            bd_contacto=self.campana.bd_contacto, filtro=buscar)
        context = self.get_context_data(form=form, contactos_encontrados=contactos_encontrados)
        return self.render_to_response(context)
