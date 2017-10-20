# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import faker

from uuid import uuid4

from factory import DjangoModelFactory, lazy_attribute, SubFactory, Sequence, post_generation

from django.utils import timezone

from ominicontacto_app.models import (AgenteProfile, BaseDatosContacto, Campana, Grupo, Queue,
                                      CalificacionCampana, Calificacion, Formulario, Grabacion,
                                      GrabacionMarca, Queuelog, SitioExterno, User, Contacto,
                                      SupervisorProfile, AgenteEnContacto)

faker = faker.Factory.create()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = lazy_attribute(lambda a: faker.name())
    last_session_key = Sequence(lambda n: "session_{0}.dat".format(n))


class SitioExternoFactory(DjangoModelFactory):
    class Meta:
        model = SitioExterno

    nombre = lazy_attribute(lambda a: faker.text(15))
    url = lazy_attribute(lambda a: "http://{0}.com".format(a.nombre.replace(" ", "_")))


class GrupoFactory(DjangoModelFactory):
    class Meta:
        model = Grupo
    nombre = Sequence(lambda n: "grupo_{0}.dat".format(n))
    auto_unpause = lazy_attribute(lambda a: faker.random_number(2))


class AgenteProfileFactory(DjangoModelFactory):
    class Meta:
        model = AgenteProfile

    user = SubFactory(UserFactory)
    sip_extension = lazy_attribute(lambda a: faker.ean8())
    grupo = SubFactory(GrupoFactory)
    estado = lazy_attribute(lambda a: faker.random_int(1, 3))
    reported_by = SubFactory(UserFactory)
    #  TODO: hacer atributos: 'modulos', 'sip_password'


class SupervisorProfileFactory(DjangoModelFactory):
    class Meta:
        model = SupervisorProfile

    user = SubFactory(UserFactory)
    sip_extension = lazy_attribute(lambda a: faker.ean8())
    #  TODO: hacer atributo 'sip_password'


class BaseDatosContactoFactory(DjangoModelFactory):
    class Meta:
        model = BaseDatosContacto

    nombre = lazy_attribute(lambda a: "BD_contacto_{0}".format(uuid4()))

    nombre_archivo_importacion = Sequence(lambda n: "file_{0}.dat".format(n))
    metadata = lazy_attribute(lambda a: faker.paragraph(7))
    estado = BaseDatosContacto.ESTADO_DEFINIDA


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

    nombre = lazy_attribute(lambda a: "campana_{0}".format(uuid4()))
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


class GrabacionFactory(DjangoModelFactory):
    class Meta:
        model = Grabacion

    fecha = lazy_attribute(lambda a: timezone.now())
    tipo_llamada = lazy_attribute(lambda a: faker.random_int(1, 3))
    id_cliente = lazy_attribute(lambda a: faker.text(5))
    tel_cliente = lazy_attribute(lambda a: str(faker.random_number(7)))
    grabacion = lazy_attribute(lambda a: faker.text(max_nb_chars=5))
    sip_agente = lazy_attribute(lambda a: faker.random_number(5))
    campana = SubFactory(CampanaFactory)
    uid = lazy_attribute(lambda a: format(uuid4().int))


class GrabacionMarcaFactory(DjangoModelFactory):
    class Meta:
        model = GrabacionMarca

    uid = lazy_attribute(lambda a: format(uuid4().int))
    descripcion = lazy_attribute(lambda a: faker.text(5))


class ContactoFactory(DjangoModelFactory):
    class Meta:
        model = Contacto

    telefono = lazy_attribute(lambda a: faker.random_number(10))
    datos = lazy_attribute(lambda a: faker.text())
    bd_contacto = SubFactory(BaseDatosContactoFactory)


class QueueFactory(DjangoModelFactory):
    class Meta:
        model = Queue
    campana = SubFactory(CampanaFactory)
    name = lazy_attribute(lambda a: "queue_{0}".format(uuid4()))
    maxlen = lazy_attribute(lambda a: faker.random_number(5))
    wrapuptime = lazy_attribute(lambda a: faker.random_number(5))
    servicelevel = lazy_attribute(lambda a: faker.random_number(5))
    strategy = 'rrmemory'
    eventmemberstatus = True
    eventwhencalled = True
    weight = lazy_attribute(lambda a: faker.random_number(5))
    ringinuse = True
    setinterfacevar = True

    wait = lazy_attribute(lambda a: faker.random_number(5))
    queue_asterisk = lazy_attribute(lambda a: faker.random_int(10))


class AgenteEnContactoFactory(DjangoModelFactory):
    class Meta:
        model = AgenteEnContacto
    agente_id = lazy_attribute(lambda a: faker.random_number(7))
    campana_id = lazy_attribute(lambda a: faker.random_number(7))
    contacto_id = lazy_attribute(lambda a: faker.random_number(7))
    datos_contacto = lazy_attribute(lambda a: faker.random_number(10))
    telefono_contacto = lazy_attribute(lambda a: faker.random_number(10))
    estado = AgenteEnContacto.ESTADO_ENTREGADO
