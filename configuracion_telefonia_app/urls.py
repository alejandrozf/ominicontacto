# -*- coding: utf-8 -*-

from django.conf.urls import url

from configuracion_telefonia_app import views
from ominicontacto_app.auth.decorators import administrador_requerido


urlpatterns = [
    url(r'^configuracion_telefonia/troncal_sip/lista/$',
        administrador_requerido(views.TroncalSIPListView.as_view()),
        name='lista_troncal_sip',
        ),
    url(r'^configuracion_telefonia/troncal_sip/crear/$',
        administrador_requerido(views.TroncalSIPCreateView.as_view()),
        name='crear_troncal_sip',
        ),
    url(r'^configuracion_telefonia/troncal_sip/(?P<pk>\d+)/$',
        administrador_requerido(views.TroncalSIPUpdateView.as_view()),
        name='editar_troncal_sip',
        ),
]
