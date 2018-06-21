# -*- coding: utf-8 -*-

from ominicontacto_app.tests.utiles import OMLBaseTest


class TestsRutasEntrantes(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsRutasEntrantes, self).setUp(*args, **kwargs)
        self._crear_troncales_y_rutas()

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

        self.usr_sup = self.crear_user_supervisor()
        self.crear_supervisor_profile(self.usr_sup)

    def test_creacion_campana_entrante_crea_nodo_ruta_entrante(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_ruta_entrante(self):
        pass

    def test_usuario_administrador_puede_crear_ruta_entrante(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_ruta_entrante(self):
        pass

    def test_usuario_administrador_puede_modificar_ruta_entrante(self):
        pass

    def test_usuario_sin_administracion_no_puede_eliminar_ruta_entrante(self):
        pass

    def test_usuario_administrador_puede_eliminar_ruta_entrante(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_ivr(self):
        pass

    def test_usuario_administrador_puede_crear_ivr(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_ivr(self):
        pass

    def test_usuario_administrar_puede_modificar_ivr(self):
        pass

    def test_creacion_ivr_crea_nodo_generico_correspondiente(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_grupo_horario(self):
        pass

    def test_usuario_administrador_puede_crear_grupo_horario(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_grupo_horario(self):
        pass

    def test_usuario_administrar_puede_modificar_grupo_horario(self):
        pass

    def test_usuario_sin_administracion_no_puede_crear_validacion_fecha_hora(self):
        pass

    def test_usuario_administrador_puede_crear_validacion_fecha_hora(self):
        pass

    def test_usuario_sin_administracion_no_puede_modificar_validacion_fecha_hora(self):
        pass

    def test_usuario_administrar_puede_modificar_validacion_fecha_hora(self):
        pass

    def test_creacion_validacion_entrante_crea_nodo_generico_correspondiente(self):
        pass

    def test_form_ivr_escoger_audio_ppal_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_sistema_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_ppal_externo_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_sistema_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_time_out_externo_no_coincide_tipo_audio_es_invalido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_sistema_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_sistema_no_coincide_tipo_audio_es_invalido(
            self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_externo_coincide_tipo_audio_es_valido(self):
        pass

    def test_form_ivr_escoger_audio_destino_invalido_externo_no_coincide_tipo_audio_es_invalido(
            self):
        pass

    def test_form_validacion_fecha_hora_destinos_distintos_es_valido(self):
        pass

    def test_form_validacion_fecha_hora_destinos_iguales_es_invalido(self):
        pass

    def test_form_validacion_tiempo_hora_inicio_mayor_hora_final_es_invalido(self):
        pass

    def test_form_validacion_tiempo_hora_inicio_igual_hora_final_es_invalido(self):
        pass

    def test_form_validacion_tiempo_hora_inicio_menor_hora_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_dia_semana_inicio_menor_dia_semana_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_dia_semana_inicio_igual_dia_semana_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_dia_semana_inicio_mayor_dia_semana_final_es_invalido(self):
        pass

    def test_form_validacion_tiempo_dia_mes_inicio_menor_dia_mes_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_dia_mes_inicio_igual_dia_mes_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_dia_mes_inicio_mayor_dia_mes_final_es_invalido(self):
        pass

    def test_form_validacion_tiempo_mes_inicio_menor_mes_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_mes_inicio_igual_mes_final_es_valido(self):
        pass

    def test_form_validacion_tiempo_mes_inicio_mayor_mes_final_es_invalido(self):
        pass
