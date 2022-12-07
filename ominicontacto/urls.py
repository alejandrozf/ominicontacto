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

"""ominicontacto URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, re_path
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.i18n import JavaScriptCatalog
import os

js_info_packages = ('ominicontacto_app',)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('ominicontacto_app.urls')),
    re_path(r'^', include('reciclado_app.urls')),
    re_path(r'^', include('reportes_app.urls')),
    re_path(r'^', include('configuracion_telefonia_app.urls')),
    re_path(r'^', include('supervision_app.urls')),
    re_path(r'^notification/message/', include('notification_app.message.urls')),
    re_path(r'^', include('api_app.urls')),
    re_path(r'^', include('whatsapp_app.urls')),
    re_path(r'^accounts/logout/$', auth_views.LogoutView.as_view(next_page='/accounts/login/'),
            name="logout"),
]

for (regex, module) in settings.ADDON_URLPATTERNS:
    urlpatterns += [re_path(regex, include(module)), ]

urlpatterns += [
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=js_info_packages),
            name='javascript-catalog'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
]

# TODO me funciona con el if de abajo el if de arriba es mas prolijo pero no funciona
# if settings.DEBUG:
if os.getenv('DJANGO_SETTINGS_MODULE') == 'ominicontacto.settings.develop':
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
