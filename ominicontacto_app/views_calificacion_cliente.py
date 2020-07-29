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
Vistas para manejar CalificacionCliente y los Formularios asociados a la Gestion correspondiente
"""

from __future__ import unicode_literals

import json
import logging as logging_

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView, CreateView
from django.views.generic.detail import DetailView

from simple_history.utils import update_change_reason

from ominicontacto_app.forms import (CalificacionClienteForm, FormularioNuevoContacto,
                                     RespuestaFormularioGestionForm)
from ominicontacto_app.models import (
    Contacto, Campana, CalificacionCliente, RespuestaFormularioGestion,
    OpcionCalificacion, SitioExterno, AgendaContacto)
from ominicontacto_app.services.sistema_externo.interaccion_sistema_externo import (
    InteraccionConSistemaExterno)

from reportes_app.models import LlamadaLog


logger = logging_.getLogger(__name__)


class CalificacionClienteFormView(FormView):
    """
    Vista para la creacion y actualización de las calificaciones.
    Además actualiza los datos del contacto.
    Para ser usada por un Agente (con subclase para Supervisor)
    """
    template_name = 'formulario/calificacion_create_update_agente.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_info_telefonos(self, telefono):
        """Devuelve información sobre los contactos que tienen un número de teléfono
        en la BD
        """
        contactos_info = list(self.campana.bd_contacto.contactos.filter(telefono=telefono))
        return contactos_info

    def get_contacto(self, id_contacto):
        if id_contacto is None or id_contacto == '-1':
            return None
        return get_object_or_404(Contacto, pk=id_contacto)

    def get_object(self):
        if self.contacto is not None:
            try:
                return CalificacionCliente.objects.get(
                    opcion_calificacion__campana=self.campana,
                    contacto_id=self.contacto.id)
            except CalificacionCliente.DoesNotExist:
                return None
        return None

    def _es_numero_privado(self, telefono):
        if not telefono:
            return False
        return not telefono.isdigit()

    def _get_agente(self):
        return self.request.user.get_agente_profile()

    def _usuario_esta_asignado_a_campana(self):
        agente = self._get_agente()
        return agente.esta_asignado_a_campana(self.campana)

    def _get_campos_bloqueados(self):
        if self.contacto:
            return self.campana.get_campos_no_editables()
        return []

    def _get_campos_ocultos(self):
        if self.contacto:
            return self.campana.get_campos_ocultos()
        return []

    def dispatch(self, *args, **kwargs):
        id_contacto = None
        self.call_data = None
        call_data_json = 'false'
        if 'call_data_json' in kwargs:
            call_data_json = kwargs['call_data_json']
            self.call_data = json.loads(call_data_json)
            self.campana = Campana.objects.get(pk=self.call_data['id_campana'])
            telefono = self.call_data['telefono']
            if self.call_data['id_contacto']:
                id_contacto = self.call_data['id_contacto']
        else:
            self.campana = Campana.objects.get(pk=kwargs['pk_campana'])
            telefono = kwargs.get('telefono', False)

        if 'pk_contacto' in kwargs:
            id_contacto = kwargs['pk_contacto']
        self.contacto = self.get_contacto(id_contacto)

        # Verifico que este asignado a la campaña:
        if not self._usuario_esta_asignado_a_campana():
            messages.warning(
                self.request, _("No tiene permiso para calificar llamadas de esa campaña."))
            return self._get_redireccion_campana_erronea()

        if self._es_numero_privado(telefono):
            self.contacto = None
        elif telefono and self.contacto is None:
            # se dispara desde una llamada desde el webphone
            contacto_info = self.get_info_telefonos(telefono)
            len_contacto_info = len(contacto_info)
            if len_contacto_info == 0:
                self.contacto = None
            elif len_contacto_info == 1:
                self.contacto = contacto_info[0]
            else:
                return HttpResponseRedirect(
                    reverse('campana_contactos_telefono_repetido',
                            kwargs={'pk_campana': self.campana.pk,
                                    'telefono': telefono,
                                    'call_data_json': call_data_json}))

        self.object = self.get_object()

        self.agente = self._get_agente()

        self.campos_bloqueados = self._get_campos_bloqueados()
        self.campos_ocultos = self._get_campos_ocultos()

        self.configuracion_sitio_externo = None
        # Si no hay call data no puedo interactuar con el sitio_externo
        if not self.call_data or self.campana.sitio_externo is None:
            return super(CalificacionClienteFormView, self).dispatch(*args, **kwargs)

        # Analizar interaccion con Sitio Externo
        en_recepcion_de_llamada = self.request.method == 'GET'
        sitio_externo = self.campana.sitio_externo
        # Metodo      Disparador            Formato         Target
        # GET/POST    Agente/JS/Server      HTML/JSON       Iframe/NewTab
        if sitio_externo.disparador == SitioExterno.SERVER:
            # Sólo disparar al recibir la llamada.
            if en_recepcion_de_llamada:
                servicio = InteraccionConSistemaExterno()
                error = servicio.ejecutar_interaccion(sitio_externo,
                                                      self.agente,
                                                      self.campana,
                                                      self.contacto,
                                                      self.call_data)
                if error is not None:
                    pass
        else:
            if sitio_externo.disparador == SitioExterno.AUTOMATICO:
                if sitio_externo.metodo == SitioExterno.GET and \
                        sitio_externo.objetivo == SitioExterno.EMBEBIDO:
                    return redirect(sitio_externo.get_url_interaccion(
                        self.agente, self.campana, self.contacto, self.call_data, True))
                elif en_recepcion_de_llamada:
                    self.configuracion_sitio_externo = \
                        sitio_externo.get_configuracion_de_interaccion(
                            self.agente, self.campana, self.contacto, self.call_data)
            else:
                self.configuracion_sitio_externo = sitio_externo.get_configuracion_de_interaccion(
                    self.agente, self.campana, self.contacto, self.call_data)

        return super(CalificacionClienteFormView, self).dispatch(*args, **kwargs)

    def get_calificacion_form_kwargs(self):
        calificacion_kwargs = {'instance': self.object}
        if self.request.method == 'GET' and self.contacto is not None:
            calificacion_kwargs['initial'] = {'contacto': self.contacto.id}
        elif self.request.method == 'POST':
            calificacion_kwargs['data'] = self.request.POST
        return calificacion_kwargs

    def get_form(self, historico_calificaciones=False):
        kwargs = self.get_calificacion_form_kwargs()
        kwargs['historico_calificaciones'] = historico_calificaciones
        return CalificacionClienteForm(campana=self.campana,
                                       es_auditoria=self.es_auditoria(),
                                       **kwargs)

    def get_contacto_form_kwargs(self):
        kwargs = {'prefix': 'contacto_form'}
        initial = {}
        if self.contacto is not None:
            kwargs['instance'] = self.contacto
            kwargs['campos_bloqueados'] = self.campos_bloqueados
        else:
            if 'call_data_json' in self.kwargs:
                initial['telefono'] = self.call_data['telefono']
            else:
                # TODO: Cuando las manuales vengan con call_data sacar esto
                initial['telefono'] = self.kwargs['telefono']

        kwargs['campos_ocultos'] = self.campos_ocultos
        kwargs['initial'] = initial

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def get_contacto_form(self):
        return FormularioNuevoContacto(base_datos=self.campana.bd_contacto,
                                       **self.get_contacto_form_kwargs())

    def _formulario_llamada_entrante(self):
        """Determina si estamos en presencia de un formulario
        generado por una llamada entrante
        """
        tipo_llamada = None
        if self.call_data is not None:
            tipo_llamada = int(self.call_data['call_type'])
        llamada_entrante = (tipo_llamada == LlamadaLog.LLAMADA_ENTRANTE)
        return llamada_entrante

    def get(self, request, *args, **kwargs):
        formulario_llamada_entrante = self._formulario_llamada_entrante()

        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form(historico_calificaciones=formulario_llamada_entrante)
        bd_metadata = self.campana.bd_contacto.get_metadata()
        campos_telefono = bd_metadata.nombres_de_columnas_de_telefonos + ['telefono']

        return self.render_to_response(self.get_context_data(
            contacto=self.contacto,
            campos_telefono=campos_telefono,
            contacto_form=contacto_form,
            calificacion_form=calificacion_form,
            campana=self.campana,
            llamada_entrante=formulario_llamada_entrante,
            call_data=self.call_data,
            configuracion_sitio_externo=json.dumps(self.configuracion_sitio_externo)))

    def post(self, request, *args, **kwargs):
        """
        Valida formulario de Contacto y de CalificacionCliente
        """
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form()
        contacto_form_valid = contacto_form.is_valid()
        calificacion_form_valid = calificacion_form.is_valid()
        self.usuario_califica = request.POST.get('usuario_califica', 'false') == 'true'
        formulario_llamada_entrante = self._formulario_llamada_entrante()
        # cuando el formulario es generado por una llamada entrante y el usuario no desea
        # calificar al contacto, solo validamos el formulario del contacto, ya que el de
        # calificación permanece oculto (en las dos siguientes validaciones)
        if formulario_llamada_entrante and not self.usuario_califica and contacto_form_valid:
            return self.form_valid(contacto_form)
        if formulario_llamada_entrante and not self.usuario_califica and not contacto_form_valid:
            return self.form_invalid(contacto_form)
        if contacto_form_valid and calificacion_form_valid:
            return self.form_valid(contacto_form, calificacion_form)
        else:
            return self.form_invalid(contacto_form, calificacion_form)

    def _check_metadata_no_accion_delete(self, calificacion):
        """ En caso que sea una calificacion de no gestion elimina metadatacliente"""
        if calificacion.opcion_calificacion.tipo != OpcionCalificacion.GESTION \
                and calificacion.get_venta():
            calificacion.get_venta().delete()

    def _obtener_call_id(self):
        if self.call_data is not None:
            return self.call_data.get('call_id')
        return self.object_calificacion.callid

    def _calificar_form(self, calificacion_form):
        calificacion_nueva = False
        if calificacion_form.instance.pk is None:
            calificacion_nueva = True
        self.object_calificacion = calificacion_form.save(commit=False)
        self.object_calificacion.callid = self._obtener_call_id()
        self.object_calificacion.agente = self.agente
        self.object_calificacion.contacto = self.contacto

        # TODO: Ver si hace falta guardar que es una llamada manual
        # El parametro manual no viene mas
        if self.object is None:
            es_calificacion_manual = 'manual' in self.kwargs and self.kwargs['manual']
            self.object_calificacion.es_calificacion_manual = es_calificacion_manual

        self.object_calificacion.save()
        # modificamos la entrada de la modificación en la instancia para así diferenciar
        # cambios realizados directamente desde una llamada de las otras modificaciones
        update_change_reason(self.object_calificacion, self.kwargs.get('from'))

        # check metadata en calificaciones de no accion y eliminar
        self._check_metadata_no_accion_delete(self.object_calificacion)

        if self.object_calificacion.es_gestion() and \
                not self.campana.tiene_interaccion_con_sitio_externo:
            return redirect(self.get_success_url_venta())
        else:
            message = _('Operación Exitosa! '
                        'Se llevó a cabo con éxito la calificación del cliente')
            messages.success(self.request, message)
        if self.object_calificacion.es_agenda() and calificacion_nueva:
            return redirect(self.get_success_url_agenda())
        elif self.object_calificacion.es_agenda():
            # se esta modificando una calificacion de agenda existente
            # con una agenda creada
            agenda_calificacion = AgendaContacto.objects.filter(
                contacto=self.contacto, campana=self.campana, agente=self.agente).first()
            if agenda_calificacion is not None:
                return redirect(self.get_success_url_agenda_update(agenda_calificacion.pk))
            else:
                return redirect(self.get_success_url_agenda())
        elif self.kwargs['from'] == 'reporte':
            return redirect(self.get_success_url_reporte())
        else:
            return redirect(self.get_success_url())

    def form_valid(self, contacto_form, calificacion_form=None):
        nuevo_contacto = False
        if self.contacto is None:
            nuevo_contacto = True
        self.contacto = contacto_form.save(commit=False)
        if nuevo_contacto:
            self.contacto.bd_contacto = self.campana.bd_contacto
        self.contacto.datos = contacto_form.get_datos_json()
        # TODO: OML-1016 Verificar bien que hacer aca (Hace falta hacer algo si ya se calificó?)
        if nuevo_contacto:
            self.contacto.es_originario = False
        self.contacto.save()
        if calificacion_form is not None:
            # el formulario de calificación no es generado por una llamada entrante
            return self._calificar_form(calificacion_form)
        else:
            # en el caso de una campaña entrante que el usuario no desea calificar
            message = _('Operación Exitosa! '
                        'Se llevó a cabo con éxito la creación del contacto')
            self.call_data['id_contacto'] = self.contacto.pk
            self.call_data['telefono'] = self.contacto.telefono
            url_calificar_llamada_entrante = reverse(
                'calificar_llamada', kwargs={'call_data_json': json.dumps(self.call_data)})
            messages.success(self.request, message)
            return redirect(url_calificar_llamada_entrante)

    def form_invalid(self, contacto_form, calificacion_form):
        """
        Re-renders the context data with the data-filled forms and errors.
        """
        bd_metadata = self.campana.bd_contacto.get_metadata()
        campos_telefono = bd_metadata.nombres_de_columnas_de_telefonos + ['telefono']

        return self.render_to_response(self.get_context_data(
            contacto=self.contacto,
            campos_telefono=campos_telefono,
            contacto_form=contacto_form,
            calificacion_form=calificacion_form,
            campana=self.campana,
            call_data=self.call_data,
            configuracion_sitio_externo=json.dumps(self.configuracion_sitio_externo))
        )

    def get_success_url_venta(self):
        return reverse('formulario_venta',
                       kwargs={"pk_calificacion": self.object_calificacion.id})

    def get_success_url_agenda(self):
        return reverse('agenda_contacto_create',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id})

    def get_success_url_agenda_update(self, agenda_contacto_pk):
        return reverse('agenda_contacto_update',
                       kwargs={"pk": agenda_contacto_pk})

    def get_success_url_reporte(self):
        return reverse('reporte_agente_calificaciones')

    def get_success_url(self):
        return reverse('recalificacion_formulario_update_or_create',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id})

    def es_auditoria(self):
        return False

    def _get_redireccion_campana_erronea(self):
        return redirect('view_blanco')


class AuditarCalificacionClienteFormView(CalificacionClienteFormView):
    # TODO: Analizar la posibilidad de que este template y el de agente compartan lineas.
    template_name = 'formulario/calificacion_create_update_supervisor.html'

    def es_auditoria(self):
        return True

    def _get_agente(self):
        return self.object.agente

    def _usuario_esta_asignado_a_campana(self):
        if self.request.user.get_is_administrador():
            return True
        supervisor = self.request.user.get_supervisor_profile()
        return supervisor.esta_asignado_a_campana(self.campana)

    def _get_campos_bloqueados(self):
        return []

    def _get_campos_ocultos(self):
        return []

    def get_success_url_venta(self):
        return reverse('auditar_formulario_venta',
                       kwargs={"pk_calificacion": self.object_calificacion.id})

    def get_success_url(self):
        return reverse('auditar_calificacion',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id})

    def get_success_url_agenda(self):
        return self.get_success_url()

    def get_success_url_agenda_update(self, agenda_contacto):
        return self.get_success_url()

    def _get_redireccion_campana_erronea(self):
        return redirect('index')


######################################
# Respuesta de Formulario de Gestión #
######################################
class RespuestaFormularioDetailView(DetailView):
    """Vista muestra el formulario de gestion recientemente creado"""
    template_name = 'formulario/respuesta_formulario_detalle.html'
    model = RespuestaFormularioGestion

    def get_context_data(self, **kwargs):
        context = super(
            RespuestaFormularioDetailView, self).get_context_data(**kwargs)
        respuesta = RespuestaFormularioGestion.objects.get(pk=self.kwargs['pk'])
        contacto = respuesta.calificacion.contacto
        bd_contacto = contacto.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas_de_datos
        datos = json.loads(contacto.datos)
        mas_datos = []
        campos_a_ocultar = respuesta.calificacion.opcion_calificacion.campana.get_campos_ocultos()
        for nombre, dato in zip(nombres, datos):
            if nombre not in campos_a_ocultar:
                mas_datos.append((nombre, dato))

        context['contacto'] = contacto
        context['mas_datos'] = mas_datos
        context['metadata'] = json.loads(respuesta.metadata)

        return context


class RespuestaFormularioCreateUpdateFormView(CreateView):
    """
    Vista "abstracta" para la creacion o edicion de una respuesta de Formulario de gestión
    """
    model = RespuestaFormularioGestion
    form_class = RespuestaFormularioGestionForm

    def _get_calificacion(self):
        raise NotImplementedError()

    def dispatch(self, *args, **kwargs):
        self.calificacion = self._get_calificacion()

        # Verifico que este asignado a la campaña:
        if not self._usuario_esta_asignado_a_campana():
            messages.warning(
                self.request, _("No tiene permiso para calificar llamadas de esa campaña."))
            return self._get_redireccion_campana_erronea()

        self.contacto = self.calificacion.contacto
        self.object = self.calificacion.get_venta()
        return super(RespuestaFormularioCreateUpdateFormView, self).dispatch(*args, **kwargs)

    def get_contacto_form_kwargs(self):
        kwargs = {'instance': self.contacto,
                  'prefix': 'contacto_form',
                  'initial': {}}
        if self.request.method == "POST":
            kwargs['data'] = self.request.POST
        return kwargs

    def get_contacto_form(self):
        return FormularioNuevoContacto(**self.get_contacto_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(RespuestaFormularioCreateUpdateFormView, self).get_form_kwargs()
        formulario = self.calificacion.opcion_calificacion.formulario
        campos = formulario.campos.all()
        kwargs['campos'] = campos
        if self.object:
            kwargs['instance'] = self.object
            for clave, valor in json.loads(self.object.metadata).items():
                kwargs['initial'].update({clave: valor})
        else:
            kwargs['initial'].update({'calificacion': self.calificacion.id, })
        return kwargs

    def get(self, request, *args, **kwargs):
        contacto_form = self.get_contacto_form()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(
            form=form, contacto_form=contacto_form))

    def form_valid(self, form, contacto_form):
        self.contacto = contacto_form.save(commit=False)
        self.contacto.datos = contacto_form.get_datos_json()
        self.contacto.save()

        self.object = form.save(commit=False)
        cleaned_data_respuesta = form.cleaned_data
        del cleaned_data_respuesta['calificacion']
        metadata = json.dumps(cleaned_data_respuesta)
        self.object.metadata = metadata
        self.object.calificacion = self.calificacion
        self.object.save()
        message = _('Operación Exitosa!'
                    'Se llevó a cabo con éxito el llenado del formulario del'
                    ' cliente')
        messages.success(self.request, message)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for validity.
        """
        contacto_form = self.get_contacto_form()
        form = self.get_form()

        if form.is_valid() and contacto_form.is_valid():
            return self.form_valid(form, contacto_form)
        else:
            return self.form_invalid(form, contacto_form)

    def form_invalid(self, form, contacto_form):

        message = '<strong>Operación Errónea!</strong> \
                  Error en el formulario revise bien los datos llenados.'

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data(
            form=form, contacto_form=contacto_form))

    def get_success_url(self):
        return reverse('formulario_detalle', kwargs={"pk": self.object.pk})


class RespuestaFormularioCreateUpdateAgenteFormView(RespuestaFormularioCreateUpdateFormView):
    template_name = 'formulario/respuesta_formulario_gestion_agente.html'

    def get_contacto_form_kwargs(self):
        kwargs = super(
            RespuestaFormularioCreateUpdateAgenteFormView, self).get_contacto_form_kwargs()
        campana = self.calificacion.opcion_calificacion.campana
        kwargs['campos_bloqueados'] = campana.get_campos_no_editables()
        kwargs['campos_ocultos'] = campana.get_campos_ocultos()
        return kwargs

    def _get_calificacion(self):
        return CalificacionCliente.objects.get(id=self.kwargs['pk_calificacion'])

    def _usuario_esta_asignado_a_campana(self):
        agente = self.request.user.get_agente_profile()
        return agente.esta_asignado_a_campana(self.calificacion.opcion_calificacion.campana)

    def _get_redireccion_campana_erronea(self):
        return redirect('view_blanco')


class RespuestaFormularioCreateUpdateSupervisorFormView(RespuestaFormularioCreateUpdateFormView):
    template_name = 'formulario/respuesta_formulario_gestion_supervisor.html'

    def _get_calificacion(self):
        return CalificacionCliente.objects.get(id=self.kwargs['pk_calificacion'])

    def get_success_url(self):
        return reverse(
            'auditar_calificacion',
            kwargs={'pk_campana': self.calificacion.opcion_calificacion.campana.id,
                    'pk_contacto': self.calificacion.contacto.id})

    def _usuario_esta_asignado_a_campana(self):
        if self.request.user.get_is_administrador():
            return True
        supervisor = self.request.user.get_supervisor_profile()
        return supervisor.esta_asignado_a_campana(self.calificacion.opcion_calificacion.campana)

    def _get_redireccion_campana_erronea(self):
        return redirect('index')
