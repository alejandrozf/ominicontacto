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

import subprocess


def check_not_duplicated_values(list_values, setting_name):
    not_duplicated_values = len(list_values) == len(
        set(list_values))
    assert not_duplicated_values, "Hay valores duplicados para {0}".format(setting_name)


def check_template_context_processor_structure(template_context_processors_list):
    """Valida que la estructura de la lista de procesador de contextos en los templates
    esté correcta
    """
    # de momento solo chequeamos que la estructura no contenga middlewares duplicados
    # la idea es más adelante realizar más chequeos
    check_not_duplicated_values(template_context_processors_list, "TEMPLATE_CONTEXT_PROCESSORS")


def check_middleware_structure(MIDDLEWARE_CLASSES_STRUCTURE):
    """Valida que la estructura en los middleware esté correcta"""
    # de momento solo chequeamos que la estructura no contenga middlewares duplicados
    # la idea es más adelante realizar más chequeos
    check_not_duplicated_values(MIDDLEWARE_CLASSES_STRUCTURE, "MIDDLEWARE_CLASSES")


def check_setting_present(setting_var_val, setting_var_str):
    """Determina si una variable de settings esta tomando valor en OML"""
    assert setting_var_val is not None,  \
        "Falta definir setting para {0}".format(setting_var_str)


def process_middleware_settings(MIDDLEWARE_PREPPEND, MIDDLEWARE_APPEND, MIDDLEWARE_CLASSES,
                                TEMPLATES_CONTEXT_PROCESORS_APPEND, TEMPLATES):
    # se realizan las configuraciones y validaciones para los addons que tienen middleware
    MIDDLEWARE_CLASSES_STRUCTURE = MIDDLEWARE_PREPPEND + MIDDLEWARE_CLASSES
    MIDDLEWARE_CLASSES_STRUCTURE.extend(MIDDLEWARE_APPEND)
    check_middleware_structure(MIDDLEWARE_CLASSES_STRUCTURE)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES_STRUCTURE

    # se realizan las configuraciones y validaciones  para los addons que tienen
    # templates_context_processors propios
    TEMPLATES[0]['OPTIONS']['context_processors'].extend(TEMPLATES_CONTEXT_PROCESORS_APPEND)
    check_template_context_processor_structure(TEMPLATES[0]['OPTIONS']['context_processors'])
    return (MIDDLEWARE_PREPPEND, MIDDLEWARE_APPEND, MIDDLEWARE_CLASSES,
            TEMPLATES_CONTEXT_PROCESORS_APPEND, TEMPLATES)


def check_settings_variables(variables_pairs):
    for variable_pair in variables_pairs:
        check_setting_present(*variable_pair)


def check_asterisk_connect_settings(ASTERISK):
    for key in ('AMI_USERNAME', 'AMI_PASSWORD'):
        assert key in ASTERISK, \
            "Falta key '{0}' en configuracion de ASTERISK".\
            format(key)
        assert ASTERISK[key] is not None, \
            "Falta key '{0}' en configuracion de ASTERISK".\
            format(key)


def check_audio_conversor_settings(TMPL_OML_AUDIO_CONVERSOR):

    assert "<INPUT_FILE>" in TMPL_OML_AUDIO_CONVERSOR, \
        "Falta definir <INPUT_FILE> en TMPL_OML_AUDIO_CONVERSOR"

    assert "<OUTPUT_FILE>" in TMPL_OML_AUDIO_CONVERSOR, \
        "Falta definir <OUTPUT_FILE> en TMPL_OML_AUDIO_CONVERSOR"

    # 3 elementos como minimo: (1) comando (2/3) INPUT/OUTPUT
    assert len(TMPL_OML_AUDIO_CONVERSOR) >= 3, \
        "TMPL_OML_AUDIO_CONVERSOR debe tener al menos 3 elementos"

    ret = subprocess.call('which {0} > /dev/null 2> /dev/null'.format(
        TMPL_OML_AUDIO_CONVERSOR[0]), shell=True)

    assert ret == 0, "No se ha encontrado el ejecutable configurado " +\
        "en TMPL_OML_AUDIO_CONVERSOR: '{0}'".format(TMPL_OML_AUDIO_CONVERSOR[0])
