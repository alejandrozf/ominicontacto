# -*- coding: utf-8 -*-

"""
Vistas para el modelo de Contacto de la base de datos
"""

from __future__ import unicode_literals

import json

from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import DeleteView
from django.views.generic import View, ListView, CreateView, UpdateView, FormView
from ominicontacto_app.models import Campana, Contacto, BaseDatosContacto
from django.core.urlresolvers import reverse
from ominicontacto_app.forms import ContactoForm, FormularioNuevoContacto, EscogerCampanaForm
from ominicontacto_app.utiles import convertir_ascii_string


class ContactoCreateView(CreateView):
    """Vista para crear un contacto"""
    model = Contacto
    template_name = 'agente/contacto_create_update_form.html'
    form_class = ContactoForm

    def get_success_url(self):
        return reverse('view_blanco')


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
