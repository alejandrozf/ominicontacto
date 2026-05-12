import json
import uuid

import redis
from asgiref.sync import async_to_sync, sync_to_async

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, Page
from django.db import models
from django.http import QueryDict
from django.template.loader import render_to_string
from django.utils import translation
from ominicontacto_app.forms.base import GrabacionBusquedaFormEx
from ominicontacto_app.models import AgenteProfile
from ominicontacto_app.models import Campana
from ominicontacto_app.models import OpcionCalificacion
from ominicontacto_app.models import CalificacionCliente
from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import convert_fecha_datetime
from channels.db import database_sync_to_async

SEARCH_RECORDINGS_STATUS_QUEUED = "queued"
SEARCH_RECORDINGS_STATUS_RUNNING = "running"
SEARCH_RECORDINGS_STATUS_DONE = "done"
SEARCH_RECORDINGS_STATUS_FAILED = "failed"


class SearchRecordingTaskRegister(object):
    TASK_TTL_SECONDS = 3600 * 24

    @classmethod
    def _key(cls, task_id):
        return "OML:SEARCH_RECORDINGS:TASK:{task_id}".format(task_id=task_id)

    @classmethod
    def _connection(cls):
        return redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION["port"],
            decode_responses=True,
        )

    @classmethod
    def store(cls, task_id, user_id, status, result=None, error_message=None):
        redis_connection = cls._connection()
        payload = {
            "user_id": str(user_id),
            "status": status,
        }
        if result is not None:
            payload["result"] = json.dumps(result)
        if error_message is not None:
            payload["error_message"] = error_message
        redis_connection.hset(cls._key(task_id), mapping=payload)
        redis_connection.expire(
            cls._key(task_id),
            cls.TASK_TTL_SECONDS,
        )

    @classmethod
    def get(cls, task_id):
        redis_connection = cls._connection()
        payload = redis_connection.hgetall(cls._key(task_id))
        if not payload:
            return None
        if "result" in payload:
            payload["result"] = json.loads(payload["result"])
        return payload


_search_recordings_task_store_async = sync_to_async(SearchRecordingTaskRegister.store)
_search_recordings_task_get_async = sync_to_async(SearchRecordingTaskRegister.get)


class SearchRecordingsMixin(object):
    """
    client-brow -> client-cons (search_recordings.request)
    client-cons -> worker-cons (search_recordings.enqueue)
    worker-cons -> client-cons (search_recordings.dequeue)
    client-cons -> client-brow (search_recordings.respond)
    """

    @database_sync_to_async
    def _parse_and_validate_recording_search_request(self, message):
        user = self.scope["user"]
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

    async def search_recordings_request(self, message):
        with translation.override(self.current_language):
            task_id = message.get("task_id") or str(uuid.uuid4())
            (
                campanas,
                data,
                form_is_valid,
                form_cleaned_data,
                form_errors,
                role
            ) = await self._parse_and_validate_recording_search_request(message)
            if form_is_valid:
                await _search_recordings_task_store_async(
                    task_id,
                    self.scope["user"].id,
                    SEARCH_RECORDINGS_STATUS_QUEUED,
                )
                await self.channel_layer.send(
                    "background-tasks",
                    {
                        "type": "search_recordings.enqueue",
                        "task_id": task_id,
                        "addressee": {
                            "group": self.groups[1],
                            "channel_name": self.channel_name,
                            "role": role,
                        },
                        "requester": {
                            "user_id": self.scope["user"].id,
                            "username": self.scope["user"].get_username(),
                        },
                        "query": form_cleaned_data,
                        "campana_choice": [campana.id for campana in campanas],
                        "current_language": self.current_language,
                        "context": {
                            "BASE_URL": data["BASE_URL"],
                        },
                    },
                )
                await self.send_json({
                    "type": "search_recordings.status",
                    "task_id": task_id,
                    "status": SEARCH_RECORDINGS_STATUS_QUEUED,
                })
            else:
                await self.send_json({
                    "type": "search_recordings.respond",
                    "task_id": task_id,
                    "result": {
                        "errors": form_errors
                    },
                })

    async def search_recordings_resume(self, message):
        task_id = message.get("task_id")
        if not task_id:
            return
        task = await _search_recordings_task_get_async(task_id)
        if not task or task.get("user_id") != str(self.scope["user"].id):
            return
        await self.send_json({
            "type": "search_recordings.status",
            "task_id": task_id,
            "status": task.get("status"),
            "error_message": task.get("error_message"),
        })

    def search_recordings_enqueue(self, message):
        with translation.override(message['current_language']):
            task_id = message.get("task_id", "unknown")
            requester = message.get("requester", {})
            try:
                SearchRecordingTaskRegister.store(
                    task_id,
                    requester.get("user_id"),
                    SEARCH_RECORDINGS_STATUS_RUNNING,
                )
                async_to_sync(self.channel_layer.group_send)(
                    message["addressee"]["group"], {
                        "type": "search_recordings.status",
                        "task_id": task_id,
                        "addressee": {
                            "channel_name": message["addressee"]["channel_name"]
                        },
                        "status": SEARCH_RECORDINGS_STATUS_RUNNING,
                    }
                )
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
                try:
                    page = paginator.page(message["query"]["pagina"])
                except EmptyPage:
                    page = Page([], message["query"]["pagina"], paginator)
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
                            "_pagination.html",
                            {
                                "page": page,
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
                            _page_object_dict[grabacion.callid]['contacto_id'] = (
                                grabacion.contacto_id
                            )
                            _page_object_dict[grabacion.callid]['campana_id'] = (
                                grabacion.campana_id
                            )
                            _page_object_dict[grabacion.callid]['callid'] = grabacion.callid
                        elif _page_object_dict[grabacion.callid]['origen'].time > grabacion.time:
                            if 'transfer' not in _page_object_dict[grabacion.callid]:
                                _page_object_dict[grabacion.callid]['transfer'] = []
                            aux = _page_object_dict[grabacion.callid]['origen']
                            _page_object_dict[grabacion.callid]['origen'] = grabacion
                            _page_object_dict[grabacion.callid]['contacto_id'] = (
                                grabacion.contacto_id
                            )
                            _page_object_dict[grabacion.callid]['transfer'].append(aux)
                            _page_object_dict[grabacion.callid]['campana_id'] = (
                                grabacion.campana_id
                            )
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
                            "_pagination.html",
                            {
                                "page": page,
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
                result = {
                    "fragments": fragments,
                }
                SearchRecordingTaskRegister.store(
                    task_id,
                    requester.get("user_id"),
                    SEARCH_RECORDINGS_STATUS_DONE,
                    result=result,
                )
                async_to_sync(self.channel_layer.group_send)(
                    message["addressee"]["group"], {
                        "type": "search_recordings.status",
                        "task_id": task_id,
                        "addressee": {
                            "channel_name": message["addressee"]["channel_name"]
                        },
                        "status": SEARCH_RECORDINGS_STATUS_DONE,
                    }
                )
            except Exception:
                SearchRecordingTaskRegister.store(
                    task_id,
                    requester.get("user_id"),
                    SEARCH_RECORDINGS_STATUS_FAILED,
                    error_message="No se pudo generar el reporte.",
                )
                async_to_sync(self.channel_layer.group_send)(
                    message["addressee"]["group"], {
                        "type": "search_recordings.status",
                        "task_id": task_id,
                        "addressee": {
                            "channel_name": message["addressee"]["channel_name"]
                        },
                        "status": SEARCH_RECORDINGS_STATUS_FAILED,
                        "error_message": "No se pudo generar el reporte.",
                    }
                )
                raise

    async def search_recordings_dequeue(self, message):
        if message["addressee"]["channel_name"] == self.channel_name:
            await self.send_json({
                "type": "search_recordings.respond",
                "task_id": message.get("task_id"),
                "result": message["result"],
            })

    async def search_recordings_status(self, message):
        if message["addressee"]["channel_name"] == self.channel_name:
            await self.send_json({
                "type": "search_recordings.status",
                "task_id": message.get("task_id"),
                "status": message.get("status"),
                "error_message": message.get("error_message"),
            })
