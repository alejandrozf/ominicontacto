# -*- coding: utf-8 -*-
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)

from ominicontacto_app.models import User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User