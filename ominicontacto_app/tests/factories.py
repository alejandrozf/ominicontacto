# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import faker

from factory import DjangoModelFactory, lazy_attribute, SubFactory, Sequence, post_generation

from django.utils import timezone

from ominicontacto_app.models import (BaseDatosContacto, Campana, CalificacionCampana, Calificacion,
                                      Formulario, Queuelog, SitioExterno, User)

faker = faker.Factory.create()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    last_session_key = lazy_attribute(lambda a: faker.text(15))


class SitioExternoFactory(DjangoModelFactory):
    class Meta:
        model = SitioExterno

    nombre = lazy_attribute(lambda a: faker.text(15))
    url = lazy_attribute(lambda a: "http://{0}.com".format(a.nombre.replace(" ", "_")))


class BaseDatosContactoFactory(DjangoModelFactory):
    class Meta:
        model = BaseDatosContacto

    nombre = lazy_attribute(lambda a: faker.text(128))

    nombre_archivo_importacion = Sequence(lambda n: "file_{0}.dat".format(n))
    metadata = lazy_attribute(lambda a: faker.paragraph(7))


class FormularioFactory(DjangoModelFactory):
    class Meta:
        model = Formulario

    nombre = lazy_attribute(lambda a: "ventas_{0}".format(faker.company()))
    descripcion = lazy_attribute(lambda a: faker.paragraph(10))


class CalificacionFactory(DjangoModelFactory):
    class Meta:
        model = Calificacion

    nombre = lazy_attribute(lambda a: "calificacion_{0}".format(faker.text(10)))


class CalificacionCampanaFactory(DjangoModelFactory):
    class Meta:
        model = CalificacionCampana

    nombre = lazy_attribute(lambda a: "calificacion_campana_{0}".format(faker.text(10)))

    @post_generation
    def calificacion(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for _calification in extracted:
                self.calification.add(_calification)


class CampanaFactory(DjangoModelFactory):
    class Meta:
        model = Campana

    estado = lazy_attribute(lambda a: faker.random_digit_not_null())
    fecha_inicio = lazy_attribute(lambda a: timezone.now())
    fecha_fin = lazy_attribute(lambda a: a.fecha_inicio)

    calificacion_campana = SubFactory(CalificacionCampanaFactory)
    bd_contacto = SubFactory(BaseDatosContactoFactory)
    formulario = SubFactory(FormularioFactory)
    campaign_id_wombat = lazy_attribute(lambda a: faker.random_number(7))
    type = lazy_attribute(lambda a: faker.random_int(1, 3))
    sitio_externo = SubFactory(SitioExternoFactory)
    reported_by = SubFactory(UserFactory)
    nombre_template = lazy_attribute(lambda a: faker.text(max_nb_chars=6))

    @post_generation
    def supervisors(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for supervisor in extracted:
                self.supervisors.add(supervisor)


class QueuelogFactory(DjangoModelFactory):
    class Meta:
        model = Queuelog

    time = lazy_attribute(lambda a: timezone.now())
    callid = lazy_attribute(lambda a: faker.text(32))
    queuename = lazy_attribute(lambda a: faker.text(32))
    campana_id = lazy_attribute(lambda a: faker.random_number(7))
    agent = lazy_attribute(lambda a: faker.text(32))
    campaign_id_wombat = lazy_attribute(lambda a: faker.random_number(7))
    event = lazy_attribute(lambda a: faker.text(128))
    data1 = lazy_attribute(lambda a: faker.text(128))
    data2 = lazy_attribute(lambda a: faker.text(128))
    data3 = lazy_attribute(lambda a: faker.text(128))
    data4 = lazy_attribute(lambda a: faker.text(128))
    data5 = lazy_attribute(lambda a: faker.text(128))
