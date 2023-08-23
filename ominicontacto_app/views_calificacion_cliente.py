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
Vistas para manejar CalificacionCliente y los Formularios asociados a la Gestion correspondiente
"""

from __future__ import unicode_literals

import json
import logging as logging_
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _
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
    OpcionCalificacion, SitioExterno, AgendaContacto, ReglaIncidenciaPorCalificacion)
from ominicontacto_app.services.sistema_externo.interaccion_sistema_externo import (
    InteraccionConSistemaExterno)
from ominicontacto_app.services.campana_service import CampanaService
from ominicontacto_app.services.redis.call_contact_cache import CallContactCache
from api_app.services.calificacion_llamada import CalificacionLLamada
from notification_app.notification import RedisStreamNotifier
from configuracion_telefonia_app.models import DestinoEntrante

from reportes_app.models import LlamadaLog
from notification_app.notification import AgentNotifier


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

    def campana_es_entrante_con_identificador_de_cliente(self):
        if not self.campana.es_entrante:
            return False
        destino_campana = DestinoEntrante.get_nodo_ruta_entrante(self.campana)
        for anterior in destino_campana.destinos_anteriores.all():
            if anterior.destino_anterior.tipo == DestinoEntrante.IDENTIFICADOR_CLIENTE:
                return True
        return False

    def get_contacto(self, id_contacto):
        if id_contacto is None or id_contacto == '-1':
            return None

        # Patch para poder atender ids de contacto erroneos de campañas entrantes con CallID
        try:
            contacto = Contacto.objects.get(pk=id_contacto)
        except Contacto.DoesNotExist:
            if self.campana_es_entrante_con_identificador_de_cliente():
                message = _('El Identificador de contacto recibido no permite '
                            'definir al contacto: {0}'.format(id_contacto))
                messages.warning(self.request, message)
                return None
            return get_object_or_404(Contacto, pk=id_contacto)
        return contacto

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

    def _get_campos_obligatorios(self):
        return self.campana.get_campos_obligatorios()

    def dispatch(self, *args, **kwargs):
        id_contacto = None
        self.call_data = None
        call_data_json = 'false'
        notificar_contacto_existente = False

        if 'call_data_json' in kwargs and kwargs['call_data_json']:
            call_data_json = kwargs['call_data_json']
            self.call_data = json.loads(call_data_json)
            self.campana = Campana.objects.get(pk=self.call_data['id_campana'])
            telefono = self.call_data['telefono']
            if self.call_data['id_contacto']:
                id_contacto = self.call_data['id_contacto']

            if id_contacto is None or id_contacto == '-1':
                callid = self.call_data['call_id']
                call_contact_cache = CallContactCache()
                # Busco si la llamada ya está asociada a un contacto
                id_contacto = call_contact_cache.get_call_contact_id(callid)
                # Me aseguro que si hay contacto, exista en la base de datos de esta campaña
                if id_contacto:
                    if not self.campana.bd_contacto.contactos.filter(id=id_contacto).exists():
                        id_contacto = None
                    else:
                        notificar_contacto_existente = True
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
        if notificar_contacto_existente:
            AgentNotifier().notify_contact_saved(
                self.agente.user_id, self.call_data['call_id'], id_contacto)

        self.campos_bloqueados = self._get_campos_bloqueados()
        self.campos_ocultos = self._get_campos_ocultos()
        self.campos_obligatorios = self._get_campos_obligatorios()

        self.configuracion_sitio_externo = None
        # Si no hay call data no puedo interactuar con el sitio_externo
        if not self.call_data or self.campana.sitio_externo is None:
            return super(CalificacionClienteFormView, self).dispatch(*args, **kwargs)

        if self.campana.sitio_externo.disparador is not SitioExterno.CALIFICACION:
            # Analizar interaccion con Sitio Externo
            en_recepcion_de_llamada = self.request.method == 'GET'
            sitio_externo = self.campana.sitio_externo
            # Metodo      Disparador            Formato         Target
            # GET/POST    Agente/JS/Server      HTML/JSON       Iframe/NewTab
            if sitio_externo.disparador == SitioExterno.SERVER:
                # Sólo disparar al recibir la llamada.
                if en_recepcion_de_llamada:
                    servicio = InteraccionConSistemaExterno()
                    error = servicio.ejecutar_interaccion(
                        sitio_externo,
                        self.agente,
                        self.campana,
                        self.contacto,
                        self.call_data
                    )
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
                    self.configuracion_sitio_externo = \
                        sitio_externo.get_configuracion_de_interaccion(
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
        kwargs['campos_obligatorios'] = self.campos_obligatorios
        kwargs['initial'] = initial

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def get_contacto_form(self):
        return FormularioNuevoContacto(
            base_datos=self.campana.bd_contacto,
            **self.get_contacto_form_kwargs(),
            es_campana_entrante=self.campana.type == Campana.TYPE_ENTRANTE,
            control_de_duplicados=self.campana.control_de_duplicados
        )

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

        force_disposition = False
        if self.call_data:
            force_disposition = self.agente.grupo.obligar_calificacion
            if 'force_disposition' in self.call_data:
                force_disposition = self.call_data['force_disposition']
        if force_disposition:
            calificacion_llamada = CalificacionLLamada()
            calificacion_llamada.create_family(self.agente, self.call_data,
                                               self.kwargs['call_data_json'], calificado=False,
                                               gestion=False, id_calificacion=None)
        if calificacion_form.instance and kwargs['from'] == 'recalificacion':
            sitio_externo = self.campana.sitio_externo
            if calificacion_form.instance.opcion_calificacion.interaccion_crm and \
                    sitio_externo and sitio_externo.disparador == SitioExterno.CALIFICACION \
                    and self.call_data and sitio_externo.objetivo:
                agente = self.request.user.get_agente_profile()
                call_data = json.loads(self.kwargs['call_data_json']) \
                    if self.kwargs['call_data_json'] else {}
                call_data['id_contacto'] = self.contacto.pk
                call_data['id_calificacion'] = calificacion_form.instance.id
                call_data['formulario'] = ""
                call_data['nombre_opcion_calificacion'] = \
                    calificacion_form.instance.opcion_calificacion.nombre
                self.configuracion_sitio_externo = \
                    sitio_externo.get_configuracion_de_interaccion(
                        agente, self.campana, self.contacto, call_data)

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

        # No está agendado hasta que se haya creado la agenda correspondiente (?)
        if not self.object_calificacion.es_agenda():
            self.object_calificacion.agendado = False

        self.object_calificacion.save()
        redis_stream_notifier = RedisStreamNotifier()
        redis_stream_notifier.send('calification', self.agente.id)
        # modificamos la entrada de la modificación en la instancia para así diferenciar
        # cambios realizados directamente desde una llamada de las otras modificaciones
        update_change_reason(self.object_calificacion, self.kwargs.get('from'))

        # check metadata en calificaciones de no accion y eliminar
        self._check_metadata_no_accion_delete(self.object_calificacion)

        # Verificar si es dialer y hay regla de incidencia por calificacion
        if self.call_data and 'dialer_id' in self.call_data:
            regla = ReglaIncidenciaPorCalificacion.objects.filter(
                opcion_calificacion=self.object_calificacion.opcion_calificacion)
            if regla:
                regla = regla[0]
                campana_service = CampanaService()
                campana_service.notificar_incidencia_por_calificacion(
                    self.call_data['dialer_id'], regla)

        if self.object_calificacion.es_gestion() and \
                not self.campana.tipo_interaccion == Campana.SITIO_EXTERNO:
            if self.agente.grupo.obligar_calificacion:
                calificacion_llamada = CalificacionLLamada()
                call_data_json = self.kwargs['call_data_json'] \
                    if 'call_data_json' in self.kwargs else None
                call_data = self.call_data
                calificado = False
                if self.call_data is None:
                    calificado = True
                    call_data = {}
                    call_data['call_id'] = calificacion_form.instance.callid
                    call_data['id_campana'] = \
                        calificacion_form.instance.opcion_calificacion.campana_id
                    call_data['telefono'] = calificacion_form.instance.contacto.telefono
                calificacion_llamada.create_family(self.agente, call_data,
                                                   call_data_json, calificado=calificado,
                                                   gestion=True,
                                                   id_calificacion=calificacion_form.instance.pk)
            return redirect(self.get_success_url_venta())
        else:
            message = _('Operación Exitosa! '
                        'Se llevó a cabo con éxito la calificación del cliente')
            messages.success(self.request, message)
            self.disparar_interaccion_sitio_externo()
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

    def disparar_interaccion_sitio_externo(self):
        # Disparar InteraccionSitioExterno si corresponde
        calificacion = self.object_calificacion
        sitio_externo = calificacion.opcion_calificacion.campana.sitio_externo
        if calificacion.opcion_calificacion.interaccion_crm and sitio_externo and \
                sitio_externo.disparador == SitioExterno.CALIFICACION and self.call_data and \
                sitio_externo.objetivo is None:
            servicio = InteraccionConSistemaExterno()
            self.call_data['formulario'] = ''  # No es de gestión, no tiene formulario
            self.call_data['id_calificacion'] = calificacion.id
            self.call_data['nombre_opcion_calificacion'] = \
                calificacion.opcion_calificacion.nombre
            servicio.ejecutar_interaccion(
                sitio_externo,
                self.agente,
                calificacion.opcion_calificacion.campana,
                self.contacto,
                self.call_data
            )

    def form_valid(self, contacto_form, calificacion_form=None):
        try:
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

            if nuevo_contacto and self.call_data is not None:
                self.call_data['id_contacto'] = self.contacto.id

            callid = None
            if self.call_data is not None and self.call_data['call_id']:
                callid = self.call_data['call_id']
                # Si es un nuevo contacto y tengo un callid, los asocio en CallContactCache
                if nuevo_contacto:
                    call_contact_cache = CallContactCache()
                    call_contact_cache.set_call_contact_id(callid, self.contacto.id)
                    AgentNotifier().notify_contact_saved(
                        self.agente.user_id, self.call_data['call_id'], self.contacto.id)

            # Actualizar el contacto en LlamadaLog
            # TODO: Verificar si es necesario hacerlo siempre o solo si es nuevo el contacto
            if callid:
                llamadalog = LlamadaLog.objects.filter(callid=callid)
                if llamadalog:
                    llamadalog.update(contacto_id=self.contacto.id)

            # TODO: Pasar esto dentro de _calificar_form() ?
            if not calificacion_form or not calificacion_form.instance.es_gestion():
                force_disposition = False  # No debería ser =self.agente.grupo.obligar_calificacion?
                if self.call_data:
                    force_disposition = self.agente.grupo.obligar_calificacion
                    if 'force_disposition' in self.call_data:
                        force_disposition = self.call_data['force_disposition']
                es_agenda = False
                if calificacion_form is not None:
                    es_agenda = calificacion_form.instance.es_agenda()
                if force_disposition:
                    calificacion_llamada = CalificacionLLamada()
                    calificacion_llamada.create_family(self.agente, self.call_data,
                                                       self.kwargs['call_data_json'],
                                                       calificado=True,
                                                       gestion=False,
                                                       id_calificacion=None,
                                                       es_agenda=es_agenda)

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
        except ValidationError as e:
            messages.error(self.request, e.message)
            return self.render_to_response(self.get_context_data(
                contacto_form=contacto_form,
                calificacion_form=calificacion_form))

    def form_invalid(self, contacto_form, calificacion_form=None):
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
        kwargs = {"pk_calificacion": self.object_calificacion.id}
        if self.call_data:
            kwargs.update(call_data_json=json.dumps(self.call_data))
        return reverse('formulario_venta', kwargs=kwargs)

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
        kwargs = {"pk_campana": self.campana.id,
                  "pk_contacto": self.contacto.id}
        if self.call_data:
            self.call_data['force_disposition'] = False
            kwargs.update(call_data_json=json.dumps(self.call_data))
        return reverse('recalificacion_formulario_update_or_create',
                       kwargs=kwargs)

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

    def _get_campos_obligatorios(self):
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

    def dispatch(self, *args, **kwargs):
        self.call_data = json.loads(kwargs['call_data_json']) \
            if 'call_data_json' in kwargs else None
        return super(RespuestaFormularioDetailView, self).dispatch(*args, **kwargs)

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

        sitio_externo = respuesta.calificacion.opcion_calificacion.campana.sitio_externo
        if respuesta.calificacion.opcion_calificacion.interaccion_crm and sitio_externo and \
                sitio_externo.disparador == SitioExterno.CALIFICACION and sitio_externo.objetivo:
            campana = respuesta.calificacion.opcion_calificacion.campana
            agente = self.request.user.get_agente_profile()
            if self.request.method == 'GET' and self.call_data:
                call_data = self.call_data
                call_data['id_contacto'] = contacto.pk
                call_data['formulario'] = respuesta.metadata
                call_data['id_calificacion'] = respuesta.calificacion.id
                call_data['nombre_opcion_calificacion'] = \
                    respuesta.calificacion.opcion_calificacion.nombre
                configuracion_sitio_externo = \
                    sitio_externo.get_configuracion_de_interaccion(
                        agente, campana, contacto, call_data)
                context['configuracion_sitio_externo'] = json.dumps(configuracion_sitio_externo)
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
        self.call_data = kwargs['call_data_json'] \
            if 'call_data_json' in kwargs else None
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
        return \
            FormularioNuevoContacto(**self.get_contacto_form_kwargs(),
                                    control_de_duplicados=self.calificacion.
                                    opcion_calificacion.campana.control_de_duplicados)

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
        self.agente = self.request.user.get_agente_profile()
        force_disposition = self.agente.grupo.obligar_calificacion
        if self.call_data:
            call_data = json.loads(self.call_data)
            if 'force_disposition' in call_data:
                force_disposition = call_data['force_disposition']
        if force_disposition:
            calificacion_llamada = CalificacionLLamada()
            call_data = {}
            call_data['call_id'] = self.calificacion.callid
            call_data['id_campana'] = self.calificacion.opcion_calificacion.campana_id
            call_data['telefono'] = self.contacto.telefono
            calificacion_llamada.create_family(self.agente, call_data,
                                               None, calificado=True,
                                               gestion=False, id_calificacion=None)

        message = _('Operación Exitosa!'
                    'Se llevó a cabo con éxito el llenado del formulario del'
                    ' cliente')
        messages.success(self.request, message)
        self.disparar_interaccion_sitio_externo()
        return HttpResponseRedirect(self.get_success_url())

    def disparar_interaccion_sitio_externo(self):
        # Sólo La respuesta creada por agente debe dispararla
        return

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
        kwargs = {"pk": self.object.pk}
        if self.call_data:
            kwargs.update(call_data_json=self.call_data)
        return reverse('formulario_detalle', kwargs=kwargs)


class RespuestaFormularioCreateUpdateAgenteFormView(RespuestaFormularioCreateUpdateFormView):
    template_name = 'formulario/respuesta_formulario_gestion_agente.html'

    def get_contacto_form_kwargs(self):
        kwargs = super(
            RespuestaFormularioCreateUpdateAgenteFormView, self).get_contacto_form_kwargs()
        campana = self.calificacion.opcion_calificacion.campana
        kwargs['campos_bloqueados'] = campana.get_campos_no_editables()
        kwargs['campos_ocultos'] = campana.get_campos_ocultos()
        kwargs['campos_obligatorios'] = campana.get_campos_obligatorios()
        return kwargs

    def _get_calificacion(self):
        return CalificacionCliente.objects.get(id=self.kwargs['pk_calificacion'])

    def _usuario_esta_asignado_a_campana(self):
        self.agente = self.request.user.get_agente_profile()
        return self.agente.esta_asignado_a_campana(self.calificacion.opcion_calificacion.campana)

    def _get_redireccion_campana_erronea(self):
        return redirect('view_blanco')

    def disparar_interaccion_sitio_externo(self):
        # Disparar InteraccionSitioExterno si corresponde
        sitio_externo = self.calificacion.opcion_calificacion.campana.sitio_externo
        if self.calificacion.opcion_calificacion.interaccion_crm and sitio_externo and \
                sitio_externo.disparador == SitioExterno.CALIFICACION and self.call_data and \
                sitio_externo.objetivo is None:
            servicio = InteraccionConSistemaExterno()
            call_data = json.loads(self.call_data)
            call_data['formulario'] = self.object.metadata
            call_data['id_calificacion'] = self.calificacion.id
            call_data['nombre_opcion_calificacion'] = \
                self.calificacion.opcion_calificacion.nombre
            servicio.ejecutar_interaccion(
                sitio_externo,
                self.agente,
                self.calificacion.opcion_calificacion.campana,
                self.contacto,
                call_data
            )


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
