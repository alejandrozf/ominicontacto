# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.utiles import elimina_espacios


class CampanaFamily(object):

    def _genera_dict(self, campana):

        dict_campana = {
            'QNAME': "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),
            'TYPE': campana.type,
            'REC': campana.queue_campana.auto_grabacion,
            'AMD': campana.queue_campana.detectar_contestadores,
            'AMDPLAY': "oml/{0}".format(
                campana.queue_campana.audio_para_contestadores.get_filename_audio_asterisk()),
            'WELCOMEPLAY': "olc/{0}".format(
                campana.queue_campana.audio_de_ingreso.get_filename_audio_asterisk()),
            'CALLAGENTACTION': campana.tipo_interaccion,
            'IDFORM': campana.formulario.pk,
            'IDEXTERNALURL': campana.sitio_externo.pk,
            'RINGTIME': campana.queue_campana.timeout,
            'QUEUETIME': campana.queue_campana.wait,
            'MAXQCALLS': campana.queue_campana.maxlen,
            'SL': campana.queue_campana.servicelevel,
        }
        return dict_campana

    def create_dict(self, campana):
        dict_campana = self._genera_dict(campana)
        return dict_campana
