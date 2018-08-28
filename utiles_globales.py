# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms import ValidationError
from django.utils.translation import ugettext as _


def validar_extension_archivo_audio(valor):
    if valor is not None and not valor.name.endswith('.wav'):
        raise ValidationError(_('Archivos permitidos: .wav'), code='invalid')
