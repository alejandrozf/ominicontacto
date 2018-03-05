# -*- coding: utf-8 -*-

"""
Vistas para manejar CalificacionCliente y los Formularios asociados a la Gestion correspondiente
"""

from __future__ import unicode_literals

import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from ominicontacto_app.models import (
    Contacto, Campana, CalificacionCliente, AgenteProfile, MetadataCliente,
    WombatLog, Calificacion, UserApiCrm)
from ominicontacto_app.forms import (CalificacionClienteForm, CalificacionClienteUpdateForm,
                                     FormularioContactoCalificacion, FormularioVentaFormSet)
from django.views.decorators.csrf import csrf_exempt
from ominicontacto_app.utiles import convertir_ascii_string
from ominicontacto_app.services.wombat_call_service import WombatCallService

import logging as logging_


logger = logging_.getLogger(__name__)


class GestorDeCalificaciones(object):

    def agente_calificara_contacto(self, campana, id_agente, wombat_id='0'):
        # Notificar a Wombat que se asigna el contacto al agente
        # Solamente si tengo wombat_id en los kwargs y es distinto de 0
        if campana.type == Campana.TYPE_DIALER and not wombat_id == '0':
            service = WombatCallService()
            service.asignar_agente(wombat_id, id_agente)

    def agente_califica_contacto(self, calificacion, id_opcion_vieja, wombat_id='0'):
        """
        Acciones a tomar una vez que se califica un contacto en una campaña
        """
        # Actualizar la calificacion en wombat
        # Optimizacion: Si no es nueva y no cambia la opcion, no hace falta calificar en Wombat
        es_dialer = calificacion.campana.type == Campana.TYPE_DIALER
        es_nueva = id_opcion_vieja is None
        cambio_calificacion = not es_nueva and not id_opcion_vieja == calificacion.calificacion.id

        actualizar_wombat = es_dialer and (es_nueva or cambio_calificacion)

        if actualizar_wombat:
            # Si recibo el parámetro 'wombat_id' es porque es una llamada disparada por Wombat
            llamada_disparada_por_wombat = wombat_id == '0'
            if llamada_disparada_por_wombat:
                service = WombatCallService()
                service.calificar(wombat_id,
                                  calificacion.calificacion.nombre)
            WombatLog.objects.actualizar_wombat_log_para_calificacion(calificacion)


class CalificacionClienteFormView(FormView):
    """
    Vista para la creacion y actualización de las calificaciones.
    Además actualiza los datos del contacto.
    """
    template_name = 'formulario/calificacion_create_update.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_contacto(self):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def get_object(self):
        try:
            return CalificacionCliente.objects.get(campana_id=self.kwargs['pk_campana'],
                                                   contacto_id=self.kwargs['pk_contacto'])
        except CalificacionCliente.DoesNotExist:
            return None

    def dispatch(self, *args, **kwargs):
        try:
            self.campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
            self.contacto = self.get_contacto()
        except Contacto.DoesNotExist:
            return HttpResponseRedirect(reverse('campana_dialer_busqueda_contacto',
                                                kwargs={"pk_campana":
                                                        self.kwargs['pk_campana']}))

        self.object = self.get_object()
        return super(CalificacionClienteFormView, self).dispatch(*args, **kwargs)

    def get_calificacion_form_kwargs(self):
        if self.request.method == 'GET':
            initial = {'campana': self.kwargs['pk_campana'],
                       'contacto': self.kwargs['pk_contacto'],
                       'agente': self.kwargs['id_agente']}
            return {'instance': self.object, 'initial': initial}
        elif self.request.method == 'POST':
            return {'instance': self.object, 'data': self.request.POST}

    def get_calificacion_form(self):
        kwargs = self.get_calificacion_form_kwargs()
        if self.object is None:
            calificacion_form = CalificacionClienteForm(**kwargs)
        else:
            calificacion_form = CalificacionClienteUpdateForm(**kwargs)
        return calificacion_form

    def get_contacto_form_kwargs(self):
        if self.request.method == 'GET':
            # TODO: Pasar esta logica al formulario?
            base_datos = self.contacto.bd_contacto
            nombres = base_datos.get_metadata().nombres_de_columnas[1:]
            datos = json.loads(self.contacto.datos)
            initial = {}
            for nombre, dato in zip(nombres, datos):
                initial.update({convertir_ascii_string(nombre): dato})
            return {'instance': self.contacto, 'initial': initial}
        elif self.request.method == 'POST':
            return {'instance': self.contacto, 'data': self.request.POST}

    def get_campos_formulario_contacto(self):
        # TODO: Pasar esta logica al formulario?
        base_datos = self.contacto.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return campos

    def get_contacto_form(self):
        return FormularioContactoCalificacion(campos=self.get_campos_formulario_contacto(),
                                              **self.get_contacto_form_kwargs())

    def get(self, request, *args, **kwargs):
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_calificacion_form()

        gestor_de_calificaciones = GestorDeCalificaciones()
        gestor_de_calificaciones.agente_calificara_contacto(self.campana,
                                                            kwargs['id_agente'],
                                                            kwargs['wombat_id'])

        return self.render_to_response(self.get_context_data(
            contacto_form=contacto_form, calificacion_form=calificacion_form))

    def post(self, request, *args, **kwargs):
        """
        Valida formulario de Contacto y de CalificacionCliente
        """
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_calificacion_form()
        if contacto_form.is_valid() and calificacion_form.is_valid():
            return self.form_valid(contacto_form, calificacion_form)
        else:
            return self.form_invalid(contacto_form, calificacion_form)

    def form_valid(self, contacto_form, calificacion_form):
        contacto = contacto_form.save(commit=False)
        # TODO: Pasar esta logica al formulario?
        base_datos = contacto.bd_contacto
        metadata = base_datos.get_metadata()
        nombres = metadata.nombres_de_columnas
        datos = []
        nombres.remove('telefono')
        for nombre in nombres:
            campo = contacto_form.cleaned_data.get(convertir_ascii_string(nombre))
            datos.append(campo)
        contacto.datos = json.dumps(datos)
        contacto.save()

        id_opcion_vieja = None
        if self.object is not None:
            id_opcion_vieja = calificacion_form.initial['calificacion']
        self.object_calificacion = calificacion_form.save(commit=False)
        self.object_calificacion.set_es_venta()
        self.object_calificacion.save()

        # Finalizar relacion de contacto con agente
        # Optimizacion: si ya hay calificacion ya se termino la relacion agente contacto antes.
        if self.campana.type == Campana.TYPE_PREVIEW and self.object is None:
            self.campana.gestionar_finalizacion_relacion_agente_contacto(contacto.id)

        gestor_de_calificaciones = GestorDeCalificaciones()
        gestor_de_calificaciones.agente_califica_contacto(
            self.object_calificacion, id_opcion_vieja, self.kwargs['wombat_id'])

        if self.object_calificacion.es_venta:
            return redirect(self.get_success_url_venta())
        else:
            message = 'Operación Exitosa!\
                        Se llevó a cabo con éxito la calificacion del cliente'
            messages.success(self.request, message)

        if self.object_calificacion.calificacion.es_reservada():
            return redirect(self.get_success_url_agenda())
        elif self.kwargs['from'] == 'reporte':
            return redirect(self.get_success_url_reporte())
        else:
            return redirect(self.get_success_url())

    def form_invalid(self, contacto_form, calificacion_form):
        """
        Re-renders the context data with the data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(contacto_form=contacto_form,
                                                             calificacion_form=calificacion_form))

    def get_success_url_venta(self):
        return reverse('formulario_venta',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "pk_contacto": self.kwargs['pk_contacto'],
                               "id_agente": self.kwargs['id_agente']})

    def get_success_url_agenda(self):
        return reverse('agenda_contacto_create',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "pk_contacto": self.kwargs['pk_contacto'],
                               "id_agente": self.kwargs['id_agente']})

    def get_success_url_reporte(self):
        return reverse('reporte_agente_calificaciones',
                       kwargs={"pk_agente": self.object_calificacion.agente.pk})

    def get_success_url(self):
        return reverse('calificacion_formulario_update_or_create',
                       kwargs={"pk_campana": self.kwargs['pk_campana'],
                               "pk_contacto": self.kwargs['pk_contacto'],
                               "wombat_id": self.kwargs['wombat_id'],
                               "id_agente": self.kwargs['id_agente']})


@csrf_exempt
def calificacion_cliente_externa_view(request):
    """Servicio externo para calificar via post"""
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        # tener en cuenta que se espera json con estas claves
        data_esperada = ['pk_campana', 'id_cliente', 'id_calificacion', 'id_agente',
                         'user_api', 'password_api']
        for data in data_esperada:
            if data not in received_json_data.keys():
                return JsonResponse({'status': 'Error en falta {0}'.format(data)})

        try:
            usuario = UserApiCrm.objects.get(
                usuario=received_json_data['user_api'])

            if usuario.password == received_json_data['password_api']:
                campana = Campana.objects.get(pk=received_json_data['pk_campana'])
                contacto = Contacto.objects.get(pk=received_json_data['id_cliente'])
                opcion_calificacion = Calificacion.objects.get(
                    pk=received_json_data['id_calificacion'])
                agente = AgenteProfile.objects.get(pk=received_json_data['id_agente'])
                try:
                    calificacion = CalificacionCliente.objects.get(
                        contacto=contacto, campana=campana)
                    id_opcion_vieja = calificacion.calificacion.id
                    calificacion.calificacion = opcion_calificacion
                    calificacion.agente = agente
                    calificacion.save()
                except CalificacionCliente.DoesNotExist:
                    calificacion = CalificacionCliente.objects.create(
                        campana=campana, contacto=contacto, calificacion=opcion_calificacion,
                        agente=agente)
                    id_opcion_vieja = None

                gestor_de_calificaciones = GestorDeCalificaciones()
                gestor_de_calificaciones.agente_califica_contacto(calificacion, id_opcion_vieja)

            else:
                return JsonResponse({'status': 'no coinciden usuario y/o password'})
        except UserApiCrm.DoesNotExist:
            return JsonResponse({'status': 'no existe este usuario {0}'.format(
                received_json_data['user_api'])})
        except Campana.DoesNotExist:
            return JsonResponse({'status': 'no existe esta campaña {0}'.format(
                received_json_data['pk_campana'])})
        except Contacto.DoesNotExist:
            return JsonResponse({'status': 'no existe este contacto {0}'.format(
                received_json_data['id_cliente'])})
        except CalificacionCliente.DoesNotExist:
            return JsonResponse({'status': 'no existe esta calificación {0}'.format(
                received_json_data['id_calificacion'])})
        except AgenteProfile.DoesNotExist:
            return JsonResponse({'status': 'no existe este perfil de agente {0}'.format(
                received_json_data['id_agente'])})
        return JsonResponse({'status': 'OK'})
    else:
        return JsonResponse({'status': 'este es un metodo post'})


class FormularioCreateFormView(CreateView):
    """En esta vista se crea el formulario de gestion"""
    template_name = 'formulario/formulario_create.html'
    model = MetadataCliente
    form_class = FormularioContactoCalificacion

    def get_object(self, queryset=None):
        return Contacto.objects.get(pk=self.kwargs['pk_contacto'])

    def get_initial(self):
        initial = super(FormularioCreateFormView, self).get_initial()
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        base_datos = contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        for nombre, dato in zip(nombres, datos):
            initial.update({convertir_ascii_string(nombre): dato})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        self.object = self.get_object()
        base_datos = self.object.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        agente = AgenteProfile.objects.get(pk=self.kwargs['id_agente'])
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        self.object = self.get_object()
        form = self.get_form()
        venta_form = FormularioVentaFormSet(initial=[
            {'campana': campana.id,
             'contacto': self.object.id,
             'agente': agente.id}],
            form_kwargs={'campos': campana.formulario.campos.all()}
        )

        return self.render_to_response(self.get_context_data(
            form=form, venta_form=venta_form))

    def get_context_data(self, **kwargs):
        context = super(
            FormularioCreateFormView, self).get_context_data(**kwargs)

        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        context['pk_formulario'] = campana.formulario.pk
        contacto = Contacto.objects.get(pk=self.kwargs['pk_contacto'])
        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))
        context['contacto'] = contacto
        context['mas_datos'] = mas_datos

        return context

    def form_valid(self, form, venta_form):
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
        self.object_venta = venta_form.save(commit=False)
        cleaned_data_venta = venta_form.cleaned_data[0]
        del cleaned_data_venta['agente']
        del cleaned_data_venta['campana']
        del cleaned_data_venta['contacto']
        del cleaned_data_venta['id']
        metadata = json.dumps(cleaned_data_venta)
        self.object_venta[0].metadata = metadata
        self.object_venta[0].save()
        message = 'Operación Exitosa!' \
                  'Se llevó a cabo con éxito el llenado del formulario del' \
                  ' cliente'
        messages.success(self.request, message)
        return HttpResponseRedirect(reverse('formulario_detalle',
                                            kwargs={"pk": self.object_venta[0].pk}))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        venta_form = FormularioVentaFormSet(
            self.request.POST, form_kwargs={'campos': campana.formulario.campos.all()},
            instance=self.object)

        if form.is_valid():
            if venta_form.is_valid():
                return self.form_valid(form, venta_form)
            else:
                return self.form_invalid(form, venta_form)
        else:
            return self.form_invalid(form, venta_form)

    def form_invalid(self, form, venta_form):

        message = '<strong>Operación Errónea!</strong> \
                  Error en el formulario revise bien los datos llenados.'

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data(
            form=form, venta_form=venta_form))

    def get_success_url(self):
        # reverse('formulario_detalle',
        #         kwargs={"pk": self.kwargs['pk_campana'],
        #                 "pk_contacto": self.kwargs['pk_contacto'],
        #                 "id_agente": self.kwargs['id_agente']
        #                 }
        #         )
        reverse('view_blanco')


class FormularioDetailView(DetailView):
    """Vista muestra el formulario de gestion recientemente creado"""
    template_name = 'formulario/formulario_detalle.html'
    model = MetadataCliente

    def get_context_data(self, **kwargs):
        context = super(
            FormularioDetailView, self).get_context_data(**kwargs)
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk'])
        campana = Campana.objects.get(pk=metadata.campana.pk)
        contacto = Contacto.objects.get(pk=metadata.contacto.pk)
        bd_contacto = campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['contacto'] = contacto
        context['mas_datos'] = mas_datos
        context['metadata'] = json.loads(metadata.metadata)

        return context


class FormularioUpdateFormView(UpdateView):
    """Vista para actualizar un formulario de gestion"""
    template_name = 'formulario/formulario_create.html'
    model = MetadataCliente
    form_class = FormularioContactoCalificacion

    def get_object(self, queryset=None):
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        return metadata.contacto

    def get_initial(self):
        initial = super(FormularioUpdateFormView, self).get_initial()
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        contacto = metadata.contacto
        base_datos = contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(contacto.datos)
        for nombre, dato in zip(nombres, datos):
            initial.update({convertir_ascii_string(nombre): dato})
        return initial

    def get_form(self):
        self.form_class = self.get_form_class()
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        self.object = self.get_object()
        base_datos = self.object.bd_contacto
        metadata = base_datos.get_metadata()
        campos = metadata.nombres_de_columnas
        return self.form_class(campos=campos, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(
            FormularioUpdateFormView, self).get_context_data(**kwargs)
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])

        context['pk_formulario'] = metadata.campana.formulario.pk

        bd_contacto = metadata.campana.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas[2:]
        datos = json.loads(metadata.contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))
        context['contacto'] = metadata.contacto
        context['mas_datos'] = mas_datos

        return context

    def get(self, request, *args, **kwargs):
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        self.object = self.get_object()
        form = self.get_form()
        initial = {
            'campana': metadata.campana.id,
            'contacto': self.object.id,
            'agente': metadata.agente.id
        }
        for clave, valor in json.loads(metadata.metadata).items():
            initial.update({clave: valor})
        venta_form = FormularioVentaFormSet(
            initial=[initial],
            form_kwargs={'campos': metadata.campana.formulario.campos.all()},
        )

        return self.render_to_response(self.get_context_data(
            form=form, venta_form=venta_form))

    def form_valid(self, form, venta_form):
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
        self.object_venta = venta_form.save(commit=False)
        metadata_cliente = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        cleaned_data_venta = venta_form.cleaned_data[0]
        del cleaned_data_venta['agente']
        del cleaned_data_venta['campana']
        del cleaned_data_venta['contacto']
        del cleaned_data_venta['id']
        metadata = json.dumps(cleaned_data_venta)
        metadata_cliente.metadata = metadata
        metadata_cliente.save()
        message = 'Operación Exitosa!' \
                  'Se llevó a cabo con éxito el llenado del formulario del' \
                  ' cliente'
        messages.success(self.request, message)
        return HttpResponseRedirect(reverse('formulario_detalle',
                                            kwargs={"pk": metadata_cliente.pk}))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        metadata = MetadataCliente.objects.get(pk=self.kwargs['pk_metadata'])
        campana = metadata.campana
        venta_form = FormularioVentaFormSet(
            self.request.POST, form_kwargs={'campos': campana.formulario.campos.all()},
            instance=self.object)

        if form.is_valid():
            if venta_form.is_valid():
                return self.form_valid(form, venta_form)
            else:
                return self.form_invalid(form, venta_form)
        else:
            return self.form_invalid(form, venta_form)

    def form_invalid(self, form, venta_form):

        message = '<strong>Operación Errónea!</strong> \
                  Error en el formulario revise bien los datos llenados.'

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data(
            form=form, venta_form=venta_form))

    def get_success_url(self):
        # reverse('formulario_detalle',
        #         kwargs={"pk": self.kwargs['pk_campana'],
        #                 "pk_contacto": self.kwargs['pk_contacto'],
        #                 "id_agente": self.kwargs['id_agente']
        #                 }
        #         )
        reverse('view_blanco')
