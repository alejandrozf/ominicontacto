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
            'CALLAGENTACTION': campana.tipo_interaccion,
            'RINGTIME': campana.queue_campana.timeout,
            'QUEUETIME': campana.queue_campana.wait,
            'MAXQCALLS': campana.queue_campana.maxlen,
            'SL': campana.queue_campana.servicelevel,
        }

        if campana.queue_campana.audio_para_contestadores:
            dict_campana.update({'AMDPLAY': "oml/{0}".format(
                    campana.queue_campana.audio_para_contestadores.get_filename_audio_asterisk())})

        if campana.queue_campana.audio_de_ingreso:
            dict_campana.update({'WELCOMEPLAY': "olc/{0}".format(
                campana.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())})

        if campana.formulario:
            dict_campana.update({'IDFORM': campana.formulario.pk})
        elif campana.sitio_externo:
            dict_campana.update({'IDEXTERNALURL': campana.sitio_externo.pk})

        return dict_campana

    def create_dict(self, campana):
        dict_campana = self._genera_dict(campana)
        return dict_campana
