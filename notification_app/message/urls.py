from django.urls import path
from . import views

urlpatterns = [
    path("emsg", views.EmailListView.as_view(), name="notification-message--emsg-list"),
    path("emsg/<pk>", views.EmailDetailView.as_view(), name="notification-message--emsg-detail"),
]
