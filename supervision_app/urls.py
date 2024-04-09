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

from django.urls import path
from django.contrib.auth.decorators import login_required
from supervision_app.views import (
    SupervisionAgentesView, SupervisionCampanasEntrantesView, SupervisionCampanasSalientesView,
    SupervisionCampanasDialerView
)

urlpatterns = [
    path('supervision/agentes/',
         login_required(SupervisionAgentesView.as_view()),
         name='supervision_agentes',
         ),
    path('supervision/campanas/entrantes/',
         login_required(SupervisionCampanasEntrantesView.as_view()),
         name='supervision_campanas_entrantes',
         ),
    path('supervision/campanas/salientes/',
         login_required(SupervisionCampanasSalientesView.as_view()),
         name='supervision_campanas_salientes',
         ),
    path('supervision/campanas/dialer/',
         login_required(SupervisionCampanasDialerView.as_view()),
         name='supervision_campanas_dialer',
         ),
]
