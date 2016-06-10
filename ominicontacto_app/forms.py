# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ominicontacto_app.models import User


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_agente',
                  'is_customer', 'is_supervisor')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
