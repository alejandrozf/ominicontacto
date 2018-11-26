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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import (View, ListView, CreateView, UpdateView, FormView, DeleteView,
                                  TemplateView)

from ominicontacto_app.forms import (BusquedaContactoForm, FormularioCampanaContacto,
                                     ContactoForm, FormularioNuevoContacto, EscogerCampanaForm)
from ominicontacto_app.models import Campana, Contacto, BaseDatosContacto
from ominicontacto_app.utiles import convertir_ascii_string


# TODO: Verificar que esta vista no va mas y borrarla
# class ContactoCreateView(CreateView):
#    """Vista para crear un contacto"""
#    model = Contacto
#    template_name = 'agente/contacto_create_update_form.html'
#    form_class = ContactoForm
#
#    def get_success_url(self):
#        return reverse('view_blanco')


class ContactoUpdateView(UpdateView):
    """Vista para modificar un contacto"""
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = ContactoForm

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def get_success_url(self):
        return reverse('view_blanco')


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
        return self.render_to_response(self.get_context_data(
            form=form, campana=campana))


class ContactosTelefonosRepetidosView(TemplateView):
    """Vista que muestra todos los contactos que comparten un número de teléfono en una campaña
    """

    template_name = 'agente/contactos_telefonos_repetidos.html'

    def get_context_data(self, **kwargs):
        context = super(ContactosTelefonosRepetidosView, self).get_context_data(**kwargs)
        pk_campana = kwargs.get('pk_campana', False)
        telefono = kwargs.get('telefono', False)
        campana = get_object_or_404(Campana, pk=pk_campana)
        context['campana'] = campana
        context['contactos'] = campana.bd_contacto.contactos.filter(telefono=telefono)
        return context


class API_ObtenerContactosCampanaView(View):
    def _procesar_api(self, request, campana):
        search = request.GET['search[value]']
        contactos = campana.bd_contacto.contactos.all()
        if search != '':
            contactos = campana.bd_contacto.contactos.filter(
                telefono__iregex=search)
        return contactos

    def _procesar_contactos_salida(self, request, campana, contactos_filtrados):
        total_contactos = campana.bd_contacto.contactos.count()
        total_contactos_filtrados = contactos_filtrados.count()
        start = int(request.GET['start'])
        length = int(request.GET['length'])
        draw = int(request.GET['draw'])
        data = [[pk, telefono, ''] for pk, telefono
                in contactos_filtrados.values_list('pk', 'telefono')]
        result_dict = {
            'draw': draw,
            'recordsTotal': total_contactos,
            'recordsFiltered': total_contactos_filtrados,
            'data': data[start:start + length],
        }
        return result_dict

    def get(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        campana = Campana.objects.get(pk=pk_campana)
        contactos = self._procesar_api(request, campana)
        result_dict = self._procesar_contactos_salida(request, campana, contactos)
        return JsonResponse(result_dict)


class ContactoBDContactoCreateView(CreateView):
    """Vista para agregar un contacto a una base de datos ya existente"""
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def get_initial(self):
        initial = super(ContactoBDContactoCreateView, self).get_initial()
        initial.update({'bd_contacto': self.kwargs['bd_contacto']})

    def get_form(self):
        self.form_class = self.get_form_class()
        base_datos = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        base_datos = BaseDatosContacto.objects.get(pk=self.kwargs['bd_contacto'])
        base_datos.cantidad_contactos += 1
        base_datos.save()
        self.object.bd_contacto = base_datos

        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        self.object.datos = json.dumps(datos)
        self.object.save()
        return super(ContactoBDContactoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('lista_base_datos_contacto')


class ContactoBDContactoListView(ListView):
    """Vista que lista los contactos de una base de datos"""
    model = Contacto
    template_name = 'base_datos_contacto/contacto_list_bd_contacto.html'

    def get_context_data(self, **kwargs):
        context = super(ContactoBDContactoListView, self).get_context_data(
            **kwargs)
        context['basedatoscontacto'] = BaseDatosContacto.objects.get(
            pk=self.kwargs['bd_contacto'])
        return context

    def get_queryset(self):
        return Contacto.objects.contactos_by_bd_contacto(
            self.kwargs['bd_contacto'])


class ContactoBDContactoUpdateView(UpdateView):
    """Vista para modificar un contacto de la base de datos"""
    model = Contacto
    template_name = 'base_create_update_form.html'
    form_class = FormularioNuevoContacto

    def get_initial(self):
        initial = super(ContactoBDContactoUpdateView, self).get_initial()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        base_datos = contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        for nombre, dato in zip(nombres, datos):
            initial.update({convertir_ascii_string(nombre): dato})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        base_datos = contacto.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas

        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        contacto = self.get_object()
        base_datos = contacto.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        self.object.datos = json.dumps(datos)
        self.object.save()
        return super(ContactoBDContactoUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contacto_list_bd_contacto',
                       kwargs={'bd_contacto': self.object.bd_contacto.pk})


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
        if self.request.user.is_authenticated()\
                and self.request.user.get_agente_profile():
            agente = self.request.user.get_agente_profile()
        if not agente.get_campanas_activas_miembro():
            message = ("Este agente no esta asignado a ninguna campaña activa")
            messages.warning(self.request, message)
        return super(FormularioSeleccionCampanaFormView,
                     self).dispatch(request, *args, **kwargs)

    def get_form(self):
        self.form_class = self.get_form_class()
        if self.request.user.is_authenticated()\
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
    """Esta vista agrega un nuevo contacto para la campana seleccionada
    """
    form_class = FormularioNuevoContacto
    template_name = 'contactos/nuevo_contacto_campana.html'

    def get_form(self):
        self.form_class = self.get_form_class()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def form_valid(self, form):
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        base_datos = campana.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        telefono = form.cleaned_data.get('telefono')

        datos = []
        nombres.remove('telefono')

        for nombre in nombres:
            campo = form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        contacto = Contacto.objects.create(
            telefono=telefono, datos=json.dumps(datos),
            bd_contacto=base_datos)
        agente = self.request.user.get_agente_profile()

        if campana.type == Campana.TYPE_PREVIEW:
            campana.adicionar_agente_en_contacto(contacto)

        return HttpResponseRedirect(
            reverse('calificacion_formulario_update_or_create',
                    kwargs={"pk_campana": self.kwargs['pk_campana'],
                            "pk_contacto": contacto.pk,
                            "id_agente": agente.pk}))

    def get_success_url(self):
        reverse('view_blanco')
