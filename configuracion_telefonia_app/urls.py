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
    url(r'^configuracion_telefonia/troncal_sip/(?P<pk>\d+)/editar/$',
        administrador_requerido(views.TroncalSIPUpdateView.as_view()),
        name='editar_troncal_sip',
        ),
    url(r'^configuracion_telefonia/ruta_saliente/lista/$',
        administrador_requerido(views.RutaSalienteListView.as_view()),
        name='lista_rutas_salientes',
        ),
    url(r'^configuracion_telefonia/ruta_saliente/crear/$',
        administrador_requerido(views.RutaSalienteCreateView.as_view()),
        name='crear_ruta_saliente',
        ),
    url(r'^configuracion_telefonia/ruta_saliente/(?P<pk>\d+)/editar/$',
        administrador_requerido(views.RutaSalienteUpdateView.as_view()),
        name='editar_ruta_saliente',
        ),
]
