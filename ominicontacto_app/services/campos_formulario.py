# -*- coding: utf-8 -*-

"""
Servicio de campos de formularios.
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError

logger = logging.getLogger(__name__)


class NoSePuedeModificarOrdenError(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class OrdenCamposCampanaService(object):

    def sube_campo_una_posicion(self, campo_de_formulario):
        """
        Este método intercambia el orden del objeto campo_de_formulario pasado
        por parámetro con el objeto campo_de_formulario con el siguiente orden.
        """

        campo_superior = campo_de_formulario.obtener_campo_siguiente()
        if not campo_superior:
            raise(NoSePuedeModificarOrdenError("No se encontro un siguiente "
                                               "campo para cambiar el orden."))

        orden_campo_de_formulario = campo_de_formulario.orden
        orden_campo_de_formulario_superior = campo_superior.orden

        campo_de_formulario.orden = 0
        campo_de_formulario.save()
        campo_superior.orden = orden_campo_de_formulario
        campo_superior.save()

        campo_de_formulario.orden = orden_campo_de_formulario_superior
        campo_de_formulario.save()

    def baja_campo_una_posicion(self, campo_de_formulario):
        """
        Este método intercambia el orden del objeto campo_de_formulario pasado
        por parámetro con el objeto campo_de_formulario con el anterior orden.
        """

        campo_inferior = campo_de_formulario.obtener_campo_anterior()
        if not campo_inferior:
            raise(NoSePuedeModificarOrdenError("No se encontro un campo "
                                               "anterior para cambiar el "
                                               "orden."))

        orden_campo_de_formulario = campo_de_formulario.orden
        orden_campo_de_formulario_inferior = campo_inferior.orden

        campo_de_formulario.orden = 0
        campo_de_formulario.save()
        campo_inferior.orden = orden_campo_de_formulario
        campo_inferior.save()

        campo_de_formulario.orden = orden_campo_de_formulario_inferior
        campo_de_formulario.save()
