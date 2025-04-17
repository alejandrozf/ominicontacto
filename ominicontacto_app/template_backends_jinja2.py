# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from datetime import datetime
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.defaultfilters import date as date_filter
from django.utils import timezone
from django.utils import translation
from jinja2 import Environment
from jinja2.utils import markupsafe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from yaml import safe_dump


def now(format_string):
    tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
    return date_filter(datetime.now(tz=tzinfo), format_string)


def yaml_repr(data):
    return markupsafe.Markup(
        highlight(
            safe_dump(data, allow_unicode=True, width=240),
            get_lexer_by_name("yaml"),
            HtmlFormatter(noclasses=True),
        )
    )


def environment(**options):
    env = Environment(**options, extensions=["jinja2.ext.i18n"])
    env.install_gettext_translations(translation)
    env.globals.update({
        "now": now,
        "static": staticfiles_storage.url,
        "yaml_repr": yaml_repr,
    })
    return env
