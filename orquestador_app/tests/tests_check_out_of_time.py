# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from configuracion_telefonia_app.tests.factories import GrupoHorarioFactory, ValidacionTiempoFactory
from orquestador_app.core.check_out_of_time import is_out_of_time
from whatsapp_app.tests.factories import LineaFactory


class CheckOutOfTimeTest(TestCase):

    def test_returns_false_when_any_validation_matches(self):
        grupo_horario = GrupoHorarioFactory()
        ValidacionTiempoFactory(
            grupo_horario=grupo_horario,
            tiempo_inicial=datetime.time(0, 0, 0),
            tiempo_final=datetime.time(22, 35, 0),
            dia_semana_inicial=2,
            dia_semana_final=2,
            dia_mes_inicio=None,
            dia_mes_final=None,
            mes_inicio=None,
            mes_final=None
        )
        ValidacionTiempoFactory(
            grupo_horario=grupo_horario,
            tiempo_inicial=datetime.time(0, 34, 0),
            tiempo_final=datetime.time(23, 34, 0),
            dia_semana_inicial=0,
            dia_semana_final=1,
            dia_mes_inicio=None,
            dia_mes_final=None,
            mes_inicio=None,
            mes_final=None
        )
        line = LineaFactory(horario=grupo_horario)

        timestamp = datetime.datetime(2026, 3, 25, 15, 47, 0)

        self.assertFalse(is_out_of_time(line, timestamp))

    def test_returns_true_when_no_validation_matches(self):
        grupo_horario = GrupoHorarioFactory()
        ValidacionTiempoFactory(
            grupo_horario=grupo_horario,
            tiempo_inicial=datetime.time(0, 0, 0),
            tiempo_final=datetime.time(22, 35, 0),
            dia_semana_inicial=2,
            dia_semana_final=2,
            dia_mes_inicio=None,
            dia_mes_final=None,
            mes_inicio=None,
            mes_final=None
        )
        line = LineaFactory(horario=grupo_horario)

        timestamp = datetime.datetime(2026, 3, 26, 15, 47, 0)

        self.assertTrue(is_out_of_time(line, timestamp))
