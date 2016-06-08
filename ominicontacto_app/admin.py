# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ominicontacto_app.models import AgenteProfile, User, Modulo
from ominicontacto_app.forms import (
    CustomUserChangeForm,
    CustomUserCreationForm
)



# Heredamos del UserAdmin original para usar nuestros formularios customizados
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (
            None, {
                'fields': (
                    'is_agente',
                    'is_customer',
                    'is_supervisor'
                )
            }
        ),
    )


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    list_display =  (
        'id',
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'is_superuser',
        'is_agente',
        'is_customer',
        'is_supervisor',
        'last_login',
        'date_joined'
    )


@admin.register(AgenteProfile)
class AgenteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'active',
        'user_id'
    )


@admin.register(Modulo)
class AgenteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre'
    )