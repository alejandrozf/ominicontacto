from asgiref.sync import async_to_sync

from django.core.paginator import Paginator
from django.db import models
from django.http import QueryDict
from django.template.loader import render_to_string
from ominicontacto_app.forms.base import GrabacionBusquedaFormEx
from ominicontacto_app.models import AgenteProfile
from ominicontacto_app.models import Campana
from ominicontacto_app.models import OpcionCalificacion
from ominicontacto_app.models import CalificacionCliente
from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import convert_fecha_datetime
from channels.db import database_sync_to_async


@database_sync_to_async
def _search_recordings_request(message, user):
    if user.get_is_agente():
        agente = user.get_agente_profile()
        campanas = Campana.objects.filter(
            pk__in=agente.queue_set.values_list("campana_id", flat=True),
        ).exclude(
            estado=Campana.ESTADO_BORRADA,
        )
        data = QueryDict(message["data"]).copy()
        data["agente"] = agente
        form = GrabacionBusquedaFormEx(
            campana_choices=[(c.id, c.nombre) for c in campanas],
            data=data,
        )
        role = "agente"
    elif user.get_es_administrador_o_supervisor_normal():
        supervisor = user.get_supervisor_profile()
        if user.get_is_administrador():
            campanas = Campana.objects.all()
        else:
            campanas = supervisor.campanas_asignadas()
        data = QueryDict(message["data"])
        form = GrabacionBusquedaFormEx(
            campana_choices=[(c.id, c.nombre) for c in campanas],
            data=data,
        )
        role = "supervisor"
    return (
        campanas,
        data,
        form.is_valid(),
        form.cleaned_data,
        form.errors,
        role
    )


class SearchRecordingsMixin(object):
    """
    client-brow -> client-cons (search_recordings.request)
    client-cons -> worker-cons (search_recordings.enqueue)
    worker-cons -> client-cons (search_recordings.dequeue)
    client-cons -> client-brow (search_recordings.respond)
    """

    async def search_recordings_request(self, message):
        (
            campanas,
            data,
            form_is_valid,
            form_cleaned_data,
            form_errors,
            role
        ) = await _search_recordings_request(
            message,
            self.scope["user"]
        )
        if form_is_valid:
            await self.channel_layer.send(
                "background-tasks",
                {
                    "type": "search_recordings.enqueue",
                    "addressee": {
                        "group": self.groups[1],
                        "channel_name": self.channel_name,
                        "role": role,
                    },
                    "query": form_cleaned_data,
                    "campana_choice": [campana.id for campana in campanas],
                    "context": {
                        "BASE_URL": data["BASE_URL"],
                        "LANG_CODE": data["LANG_CODE"],
                    },
                },
            )
        else:
            await self.send_json({
                "type": "search_recordings.respond",
                "result": {
                    "errors": form_errors
                },
            })

    def search_recordings_enqueue(self, message):
        if message["query"]["agente"]:
            agente = AgenteProfile.objects.get(pk=message["query"]["agente"])
        else:
            agente = None
        queryset = LlamadaLog.objects.obtener_grabaciones_by_filtro(
            convert_fecha_datetime(message["query"]["fecha_desde"]),
            convert_fecha_datetime(message["query"]["fecha_hasta"]),
            message["query"]["tipo_llamada"],
            message["query"]["tel_cliente"],
            message["query"]["callid"],
            message["query"]["id_contacto_externo"],
            agente,
            message["query"]["campana"],
            Campana.objects.filter(pk__in=message["campana_choice"]),
            message["query"]["marcadas"],
            message["query"]["duracion"],
            message["query"]["gestion"],
            OpcionCalificacion.objects.filter(
                nombre=message["query"]["calificacion"],
            ).values_list("id", flat=True),
        )
        paginator = Paginator(queryset, message["query"]["grabaciones_x_pagina"])
        page = paginator.page(message["query"]["pagina"])
        if message["addressee"]["role"] == "agente":
            fragments = {
                "#table-body": render_to_string(
                    "agente/frame/busqueda_grabacion_ex/_table-body.html",
                    {
                        **message["context"],
                        "page": page,
                    },
                ),
                "#pagination": render_to_string(
                    "agente/frame/busqueda_grabacion_ex/_pagination.html",
                    {
                        "paginator": paginator,
                        "page_number": page.number,
                    },
                ),
            }
        elif message["addressee"]["role"] == "supervisor":
            # FIXME
            # - CONFIRM it works with paginated results
            # - port of BusquedaGrabacionSupervisorFormView._procesa_formato_transferencias
            _page_object_dict = {}
            for grabacion in page.object_list:
                if grabacion.callid not in _page_object_dict:
                    _page_object_dict[grabacion.callid] = {}
                    _page_object_dict[grabacion.callid]['origen'] = grabacion
                    _page_object_dict[grabacion.callid]['contacto_id'] = grabacion.contacto_id
                    _page_object_dict[grabacion.callid]['campana_id'] = grabacion.campana_id
                    _page_object_dict[grabacion.callid]['callid'] = grabacion.callid
                elif _page_object_dict[grabacion.callid]['origen'].time > grabacion.time:
                    if 'transfer' not in _page_object_dict[grabacion.callid]:
                        _page_object_dict[grabacion.callid]['transfer'] = []
                    aux = _page_object_dict[grabacion.callid]['origen']
                    _page_object_dict[grabacion.callid]['origen'] = grabacion
                    _page_object_dict[grabacion.callid]['contacto_id'] = grabacion.contacto_id
                    _page_object_dict[grabacion.callid]['transfer'].append(aux)
                    _page_object_dict[grabacion.callid]['campana_id'] = grabacion.campana_id
                else:
                    if 'transfer' not in _page_object_dict[grabacion.callid]:
                        _page_object_dict[grabacion.callid]['transfer'] = []
                    _page_object_dict[grabacion.callid]['transfer'].append(grabacion)
            page_object_list = list(_page_object_dict.values())
            # - port of BusquedaGrabacionFormView._get_calificaciones
            identificadores = [
                (
                    str(a['contacto_id']),
                    a['campana_id'],
                    a['callid'],
                )
                for a in page_object_list
            ]
            _filtro = models.Q()
            _callids = []
            for contacto_id, campana_id, callid in identificadores:
                if contacto_id and campana_id and not contacto_id == '-1':
                    _filtro = _filtro | models.Q(
                        contacto_id=contacto_id, opcion_calificacion__campana_id=campana_id
                    )
                else:
                    _callids.append(callid)
            calificaciones = CalificacionCliente.history.filter(
                _filtro | models.Q(callid__in=_callids)
            )
            fragments = {
                "#table-body": render_to_string(
                    "busqueda_grabacion_ex/_table-body.html",
                    {
                        **message["context"],
                        "calificaciones": calificaciones,
                        "page_object_list": page_object_list,
                    },
                ),
                "#pagination": render_to_string(
                    "busqueda_grabacion_ex/_pagination.html",
                    {
                        "paginator": paginator,
                        "page_number": page.number,
                    },
                ),
                "#calificaciones": render_to_string(
                    "busqueda_grabacion_ex/_calificaciones.html",
                    {
                        "calificaciones": calificaciones,
                    },
                ),
            }
        assert fragments
        async_to_sync(self.channel_layer.group_send)(
            message["addressee"]["group"], {
                "type": "search_recordings.dequeue",
                "addressee": {
                    "channel_name": message["addressee"]["channel_name"]
                },
                "result": {
                    "fragments": fragments,
                },
            }
        )

    async def search_recordings_dequeue(self, message):
        if message["addressee"]["channel_name"] == self.channel_name:
            await self.send_json({
                "type": "search_recordings.respond",
                "result": message["result"],
            })
