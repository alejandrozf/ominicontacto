# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.models import FormularioDemo, Campana

import logging


class CampanaService():

    def crear_formulario(self, campana):
        assert isinstance(campana, Campana)
        for contacto in campana.bd_contacto.contactos.all():
            FormularioDemo.objects.create(campana=campana, contacto=contacto,
                                          id_cliente=contacto.id_cliente,
                                          nombre=contacto.nombre,
                                          apellido=contacto.apellido,
                                          telefono=contacto.telefono,
                                          email=contacto.email,
                                          datos=contacto.datos)
