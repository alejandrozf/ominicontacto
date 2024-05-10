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
from reciclado_app import views

urlpatterns = [
    path('reciclar/<int:pk_campana>/dialer/',
         login_required(views.ReciclarCampanaDialerFormView.as_view()),
         name='reciclar_campana_dialer'),
    path('reciclar/<int:pk_campana>/preview/',
         login_required(views.ReciclarCampanaPreviewFormView.as_view()),
         name='reciclar_campana_preview'),
]
