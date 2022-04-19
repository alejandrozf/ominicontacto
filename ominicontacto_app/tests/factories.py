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
from __future__ import unicode_literals


import faker

from uuid import uuid4
import random
from factory import (DjangoModelFactory, lazy_attribute, SubFactory, Sequence, post_generation,
                     django)

from django.utils import timezone

from ominicontacto_app.models import (
    AgenteProfile, BaseDatosContacto, Campana, GrabacionMarca,
    ConfiguracionDePausa, ConjuntoDePausa, Grupo, Queue,
    NombreCalificacion, Formulario, FieldFormulario,
    SitioExterno, User, Contacto, SupervisorProfile,
    AgenteEnContacto, QueueMember, CalificacionCliente,
    OpcionCalificacion, ArchivoDeAudio, ParametrosCrm,
    ActuacionVigente, Pausa, RespuestaFormularioGestion,
    Blacklist, AgendaContacto, SistemaExterno,
    AgenteEnSistemaExterno, AuditoriaCalificacion,
    ConfiguracionDeAgentesDeCampana)

from reportes_app.models import LlamadaLog, ActividadAgenteLog

faker = faker.Factory.create()


class LlamadaLogFactory(DjangoModelFactory):
    class Meta:
        model = LlamadaLog
    time = lazy_attribute(lambda a: timezone.now())
    callid = lazy_attribute(lambda a: faker.ean8())
    campana_id = Sequence(lambda n: n)
    tipo_campana = lazy_attribute(lambda a: faker.random_int(1, 4))
    agente_id = Sequence(lambda n: n)
    event = Sequence(lambda n: "evento_{0}".format(n))
    numero_marcado = lazy_attribute(lambda a: str(
        faker.random_number(10, fix_len=True)))
    contacto_id = Sequence(lambda n: n)
    bridge_wait_time = lazy_attribute(lambda a: faker.random_number(3))
    duracion_llamada = lazy_attribute(lambda a: faker.random_number(3))
    archivo_grabacion = lazy_attribute(lambda a: faker.text(15))


class ActividadAgenteLogFactory(DjangoModelFactory):
    class Meta:
        model = ActividadAgenteLog
    time = lazy_attribute(lambda a: timezone.now())
    agente_id = Sequence(lambda n: n)
    event = Sequence(lambda n: "evento_{0}".format(n))
    pausa_id = Sequence(lambda n: n)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: "user_{0}".format(n))
    first_name = lazy_attribute(lambda a: faker.first_name())
    last_name = lazy_attribute(lambda a: faker.last_name())
    last_session_key = Sequence(lambda n: "session_{0}.dat".format(n))


class SitioExternoFactory(DjangoModelFactory):
    class Meta:
        model = SitioExterno

    nombre = lazy_attribute(lambda a: faker.text(15))
    url = lazy_attribute(lambda a: "http://{0}.com".format(a.nombre.replace(" ", "_")))
    disparador = SitioExterno.BOTON
    metodo = SitioExterno.GET
    formato = None
    objetivo = lazy_attribute(lambda a: faker.random_int(1, 2))


class SistemaExternoFactory(DjangoModelFactory):
    class Meta:
        model = SistemaExterno

    nombre = Sequence(lambda n: "Sistema_Externo_{0}".format(n))


class BlackListFactory(DjangoModelFactory):
    class Meta:
        model = Blacklist

    nombre = lazy_attribute(lambda a: faker.text(15))
    fecha_alta = lazy_attribute(lambda a: timezone.now())
    nombre_archivo_importacion = Sequence(lambda n: "file_{0}.dat".format(n))
    cantidad_contactos = lazy_attribute(lambda a: faker.random_number(2))


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


COLUMNAS_DB_DEFAULT = ['telefono', 'nombre', 'apellido', 'dni', 'telefono2', 'telefono3']


class BaseDatosContactoFactory(DjangoModelFactory):
    class Meta:
        model = BaseDatosContacto

    nombre = lazy_attribute(lambda a: "BD_contacto_{0}".format(uuid4()))

    nombre_archivo_importacion = Sequence(lambda n: "file_{0}.dat".format(n))
    metadata = '{"prim_fila_enc": false, "cant_col": 6, "nombres_de_columnas": '\
               '["' + '", "'.join(COLUMNAS_DB_DEFAULT) + '"],' + \
               ' "cols_telefono": [0, 4, 5]}'
    estado = BaseDatosContacto.ESTADO_DEFINIDA


class ContactoFactory(DjangoModelFactory):
    class Meta:
        model = Contacto

    telefono = lazy_attribute(lambda a: str(
        faker.random_number(10, fix_len=True)))
    id_externo = None
    datos = lazy_attribute(
        lambda a: '["{0}", "{1}", "{2}", "{3}", "{4}"]'.format(
            faker.name(),
            faker.name(),
            faker.random_number(7),
            str(faker.random_number(10, fix_len=True)),
            str(faker.random_number(10, fix_len=True))
        )
    )
    bd_contacto = SubFactory(BaseDatosContactoFactory)


class FormularioFactory(DjangoModelFactory):
    class Meta:
        model = Formulario

    nombre = lazy_attribute(lambda a: "ventas_{0}".format(faker.company()))
    descripcion = lazy_attribute(lambda a: faker.paragraph(10))


class FieldFormularioFactory(DjangoModelFactory):
    class Meta:
        model = FieldFormulario

    formulario = SubFactory(FormularioFactory)
    nombre_campo = lazy_attribute(lambda a: "campo_{0}".format(uuid4()))
    # Cuidado al crear con este orden aleatorio
    orden = lazy_attribute(lambda a: faker.random_int(1, 1000))
    tipo = FieldFormulario.TIPO_TEXTO
    values_select = None
    is_required = False


class NombreCalificacionFactory(DjangoModelFactory):
    class Meta:
        model = NombreCalificacion

    nombre = lazy_attribute(lambda a: "calificacion_{0}".format(uuid4()))


class CampanaFactory(DjangoModelFactory):
    class Meta:
        model = Campana

    nombre = lazy_attribute(lambda a: "campana_{0}".format(uuid4()))
    estado = lazy_attribute(lambda a: faker.random_digit_not_null())
    fecha_inicio = lazy_attribute(lambda a: timezone.now())
    fecha_fin = lazy_attribute(lambda a: a.fecha_inicio)
    bd_contacto = SubFactory(BaseDatosContactoFactory)
    tipo_interaccion = Campana.FORMULARIO
    campaign_id_wombat = lazy_attribute(lambda a: faker.random_number(7))
    type = lazy_attribute(lambda a: faker.random_int(1, 3))
    sitio_externo = None
    reported_by = SubFactory(UserFactory)
    nombre_template = lazy_attribute(lambda a: faker.text(max_nb_chars=6))

    @post_generation
    def supervisors(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for supervisor in extracted:
                self.supervisors.add(supervisor)


class GrabacionMarcaFactory(DjangoModelFactory):
    class Meta:
        model = GrabacionMarca

    callid = lazy_attribute(lambda a: format(uuid4().int))
    descripcion = lazy_attribute(lambda a: faker.text(5))


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


class AgenteEnContactoFactory(DjangoModelFactory):
    class Meta:
        model = AgenteEnContacto
    agente_id = lazy_attribute(lambda a: faker.random_number(7))
    campana_id = lazy_attribute(lambda a: faker.random_number(7))
    contacto_id = lazy_attribute(lambda a: faker.random_number(7))
    datos_contacto = lazy_attribute(lambda a: faker.random_number(10))
    telefono_contacto = lazy_attribute(lambda a: faker.random_number(10))
    estado = AgenteEnContacto.ESTADO_INICIAL


class QueueMemberFactory(DjangoModelFactory):
    class Meta:
        model = QueueMember

    member = SubFactory(AgenteProfileFactory)
    queue_name = SubFactory(QueueFactory)
    membername = Sequence(lambda n: "membername_{0}.dat".format(n))
    interface = Sequence(lambda n: "interface_{0}.dat".format(n))
    penalty = lazy_attribute(lambda a: faker.random_int(0, 9))
    paused = lazy_attribute(lambda a: faker.random_number(2))
    id_campana = lazy_attribute(lambda a: "{0}_campana".format(uuid4()))


class OpcionCalificacionFactory(DjangoModelFactory):
    class Meta:
        model = OpcionCalificacion

    campana = SubFactory(CampanaFactory)
    tipo = lazy_attribute(lambda a: faker.random_int(0, 1))
    nombre = lazy_attribute(lambda a: faker.text(15))
    formulario = SubFactory(FormularioFactory)
    oculta = False


class CalificacionClienteFactory(DjangoModelFactory):
    class Meta:
        model = CalificacionCliente

    callid = lazy_attribute(lambda a: faker.ean8())
    opcion_calificacion = SubFactory(OpcionCalificacionFactory)
    contacto = SubFactory(ContactoFactory)
    agente = SubFactory(AgenteProfileFactory)
    fecha = lazy_attribute(lambda a: timezone.now())
    observaciones = lazy_attribute(lambda a: faker.text(15))


class AuditoriaCalificacionFactory(DjangoModelFactory):
    class Meta:
        model = AuditoriaCalificacion

    resultado = AuditoriaCalificacion.APROBADA
    calificacion = SubFactory(CalificacionClienteFactory)
    observaciones = lazy_attribute(lambda a: faker.text(15))


class ArchivoDeAudioFactory(DjangoModelFactory):
    class Meta:
        model = ArchivoDeAudio

    descripcion = lazy_attribute(lambda a: "descripcion_{0}".format(uuid4()))
    audio_original = django.FileField(filename='audio_original_file.wav')
    audio_asterisk = django.FileField(filename='audio_asterisk_file.wav')


class ParametrosCrmFactory(DjangoModelFactory):
    class Meta:
        model = ParametrosCrm

    campana = SubFactory(CampanaFactory)
    tipo = ParametrosCrm.CUSTOM
    nombre = Sequence(lambda n: "nombre_{0}".format(n))
    valor = Sequence(lambda n: "valor_{0}".format(n))


class ActuacionVigenteFactory(DjangoModelFactory):
    class Meta:
        model = ActuacionVigente

    campana = SubFactory(CampanaFactory)
    domingo = False
    lunes = True
    martes = True
    miercoles = True
    jueves = True
    viernes = True
    sabado = False
    hora_desde = timezone.now()
    hora_hasta = timezone.now() + timezone.timedelta(hours=3)


class PausaFactory(DjangoModelFactory):
    class Meta:
        model = Pausa

    nombre = Sequence(lambda n: "Pausa_{0}".format(n))
    tipo = lazy_attribute(lambda a: random.choice(('P', 'R')))


class RespuestaFormularioGestionFactory(DjangoModelFactory):
    class Meta:
        model = RespuestaFormularioGestion

    calificacion = SubFactory(CalificacionClienteFactory)
    metadata = lazy_attribute(
        lambda a: '["{0}", "{1}", "{2}", "{3}", "{4}"]'.format(
            faker.name(),
            faker.name(),
            faker.random_number(7),
            str(faker.random_number(10, fix_len=True)),
            str(faker.random_number(10, fix_len=True))
        )
    )


class AgendaContactoFactory(DjangoModelFactory):
    agente = SubFactory(AgenteProfileFactory)
    campana = SubFactory(CampanaFactory)
    contacto = SubFactory(ContactoFactory)
    observaciones = lazy_attribute(lambda a: faker.text(15))
    tipo_agenda = AgendaContacto.TYPE_PERSONAL
    fecha = lazy_attribute(lambda a: timezone.now().date())
    hora = lazy_attribute(lambda a: timezone.now().time())

    class Meta:
        model = AgendaContacto


class AgenteEnSistemaExternoFactory(DjangoModelFactory):

    agente = SubFactory(AgenteProfileFactory)
    sistema_externo = SubFactory(SistemaExternoFactory)
    id_externo_agente = Sequence(lambda n: "id_externo_agente_{0}".format(n))

    class Meta:
        model = AgenteEnSistemaExterno


class ConfiguracionDeAgentesDeCampanaFactory(DjangoModelFactory):
    set_auto_attend_inbound = True
    auto_attend_inbound = True
    set_auto_attend_dialer = True
    auto_attend_dialer = True
    set_auto_unpause = True
    auto_unpause = 0
    set_obligar_calificacion = True
    set_obligar_calificacion = True

    class Meta:
        model = ConfiguracionDeAgentesDeCampana


class ConjuntoDePausaFactory(DjangoModelFactory):
    class Meta:
        model = ConjuntoDePausa

    nombre = Sequence(lambda n: "Conjunto_De_Pausa_{0}".format(n))


class ConfiguracionDePausaFactory(DjangoModelFactory):
    pausa = SubFactory(PausaFactory)
    conjunto_de_pausa = SubFactory(ConjuntoDePausaFactory)
    time_to_end_pause = lazy_attribute(lambda a: faker.random_int(1, 1200))

    class Meta:
        model = ConfiguracionDePausa
