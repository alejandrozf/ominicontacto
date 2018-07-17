# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

from django.utils import timezone

from configuracion_telefonia_app.tests.factories import (RutaEntranteFactory,
                                                         IVRFactory, ValidacionFechaHoraFactory,
                                                         OpcionDestinoFactory)
from configuracion_telefonia_app.models import (RutaEntrante, DestinoEntrante, IVR,
                                                ValidacionFechaHora, OpcionDestino, GrupoHorario)
from ominicontacto_app.models import Campana


def crear_info_destino_entrante_random():
    # crea aleatoriamente modelo de información para nodo de ruta entrante
    nodos_factories = (IVRFactory, ValidacionFechaHoraFactory)
    return choice(nodos_factories)()


def crear_destino_entrante(info_nodo_entrante):
    # crea nodo de modelo DestinoEntrante a partir de modelo recibido
    dest = DestinoEntrante.crear_nodo_ruta_entrante(info_nodo_entrante, commit=False)
    dest.nombre += timezone.now().strftime("%H:%M:%S")
    dest.save()
    return dest


def crear_relacion_nodos_entrantes(destino_entrante1, destino_entrante2):
    # crea una relacion entre dos nodos de una ruta entrante
    opcion_destino = OpcionDestinoFactory(
        destino_anterior=destino_entrante1, destino_siguiente=destino_entrante2)
    return opcion_destino


def crear_destinos_desde_campanas_entrantes():
    for campana in Campana.objects.obtener_campanas_entrantes():
        DestinoEntrante.crear_nodo_ruta_entrante(campana)


def crear_ruta_entrante(n_hijos_ivr=11):
    """Crea todos los nodos de la configuración de una ruta entrante"""

    crear_destinos_desde_campanas_entrantes()

    # creamos la raíz de la ruta entrante y la relacionamos con un IVR
    ivr_siguiente = IVRFactory()
    nodo_inmediato_siguiente_raiz = crear_destino_entrante(ivr_siguiente)
    RutaEntranteFactory(destino=nodo_inmediato_siguiente_raiz)

    # creamos rutas a partir del nodo ivr
    for i in xrange(n_hijos_ivr):
        info_siguiente = crear_info_destino_entrante_random()
        nodo_entrante_siguiente_ivr = crear_destino_entrante(info_siguiente)
        crear_relacion_nodos_entrantes(nodo_inmediato_siguiente_raiz, nodo_entrante_siguiente_ivr)


def eliminar_todo_rutas_entrantes():
    # elimina todas las instancias de los modelos relacionados con las rutas entrantes
    RutaEntrante.objects.all().delete()
    DestinoEntrante.objects.all().delete()
    IVR.objects.all().delete()
    ValidacionFechaHora.objects.all().delete()
    GrupoHorario.objects.all().delete()
    OpcionDestino.objects.all().delete()
