# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ominicontacto_app.models import AgenteProfile, User, Modulo, AgenteEnContacto
from ominicontacto_app.forms import (
    CustomUserChangeForm,
    CustomUserCreationForm
)


#  Heredamos del UserAdmin original para usar nuestros formularios customizados
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (
            None, {
                'fields': (
                    'is_agente',
                    'is_supervisor'
                )
            }
        ),
    )


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    list_display = (
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
        'is_supervisor',
        'last_login',
        'date_joined'
    )


@admin.register(AgenteProfile)
class AgenteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_id'
    )


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre'
    )


@admin.register(AgenteEnContacto)
class AgenteEnContactoAdmin(admin.ModelAdmin):
    list_display = (
        'contacto_id',
        'agente_id',
        'campana_id',
        'datos_contacto',
        'estado'
    )

    list_filter = (
        'agente_id',
        'campana_id',
    )
