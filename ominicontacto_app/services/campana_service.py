# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import FormularioDemo, Campana

import logging


class CampanaService():

    def crear_formulario(self, campana):
        assert isinstance(campana, Campana)
        for contacto in campana.bd_contacto.contactos.all():
            FormularioDemo.objects.create(campana=campana, contacto=contacto)

    def validar_modificacion_bd_contacto(self, campana, base_datos_modificar):
        error = None
        base_datos_actual = campana.bd_contacto
        metadata_actual = base_datos_actual.get_metadata()
        metadata_modidicar = base_datos_modificar.get_metadata()

        for columna_base, columna_modificar in zip(
                metadata_actual.nombres_de_columnas,
                metadata_modidicar.nombres_de_columnas):
            if columna_base != columna_modificar:
                error = "Los nombres de las columnas no coinciden"

        return error

