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

from django.shortcuts import render


def handler400(request, exception):
    response = render(request, '400.html')
    response.status_code = 400
    return response


def handler403(request, exception):
    response = render('403.html')
    response.status_code = 403
    return response


def handler404(request, exception):
    response = render('404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render('500.html')
    response.status_code = 500
    return response
