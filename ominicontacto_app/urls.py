
from django.conf.urls import url, patterns
from ominicontacto_app import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^ajax/mensaje_recibidos/',
        'ominicontacto_app.views.mensajes_recibidos_view',
        name='ajax_mensaje_recibidos'),
    url(r'^$', 'ominicontacto_app.views.index_view', name='index'),
    url(r'^user/nuevo/$',
        login_required(views.CustomerUserCreateView.as_view()),
        name='user_nuevo',
        ),
    url(r'^user/list/$', login_required(views.UserListView.as_view()),
        name='user_list',
        ),
    url(r'^user/update/(?P<pk>\d+)/$',
        login_required(views.CustomerUserUpdateView.as_view()),
        name='user_update',
        ),
    url(r'^user/agenteprofile/nuevo/(?P<pk_user>\d+)/$',
        login_required(views.AgenteProfileCreateView.as_view()),
        name='agenteprofile_nuevo',
        ),
)
