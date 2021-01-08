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

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from supervision_app.views import (
    SupervisionAgentesView, SupervisionCampanasEntrantesView, SupervisionCampanasSalientesView,
    SupervisionCampanasDialerView
)

urlpatterns = [
    url(r'^supervision/agentes/$',
        login_required(SupervisionAgentesView.as_view()),
        name='supervision_agentes',
        ),
    url(r'^supervision/campanas/entrantes/$',
        login_required(SupervisionCampanasEntrantesView.as_view()),
        name='supervision_campanas_entrantes',
        ),
    url(r'^supervision/campanas/salientes/$',
        login_required(SupervisionCampanasSalientesView.as_view()),
        name='supervision_campanas_salientes',
        ),
    url(r'^supervision/campanas/dialer/$',
        login_required(SupervisionCampanasDialerView.as_view()),
        name='supervision_campanas_dialer',
        ),
]
