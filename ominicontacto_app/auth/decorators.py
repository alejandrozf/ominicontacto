from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def administrador_requerido(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator que verifica que el usuario es Administrador.
    """
    def es_administrador(user):
        if not user.is_authenticated():
            return False
        elif user.get_is_administrador():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: es_administrador(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def supervisor_normal_requerido(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                                login_url=None):
    """
    Decorator que verifica que el usuario es Supervisor Normal.
    """
    def es_supervisor_normal(user):
        if not user.is_authenticated():
            return False
        elif user.get_is_supervisor_normal():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: es_supervisor_normal(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def supervisor_customer_requerido(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                                  login_url=None):
    """
    Decorator que verifica que el usuario es Supervisor Customer.
    """
    def es_supervisor_customer(user):
        if not user.is_authenticated():
            return False
        elif user.get_is_supervisor_customer():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: es_supervisor_customer(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permiso_administracion_requerido(function=None,
                                     redirect_field_name=REDIRECT_FIELD_NAME,
                                     login_url=None):
    """
    Decorator que verifica que el usuario es Administrador, Supervisor Normal o Customer.
    """
    def tiene_permiso_administracion(user):
        if not user.is_authenticated():
            return False
        elif user.get_tiene_permiso_administracion():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: tiene_permiso_administracion(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def administrador_o_supervisor_requerido(function=None,
                                         redirect_field_name=REDIRECT_FIELD_NAME,
                                         login_url=None):
    """
    Decorator que verifica que el usuario es Administrador o Supervisor Normal.
    """
    def es_administrador_o_supervisor_normal(user):
        if not user.is_authenticated():
            return False
        elif user.get_es_administrador_o_supervisor_normal():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: es_administrador_o_supervisor_normal(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def agente_requerido(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator que verifica que el usuario es un Agente.
    """
    def is_agente(user):
        if not user.is_authenticated():
            return False
        elif user.get_is_agente():
            return True
        else:
            raise PermissionDenied
    actual_decorator = user_passes_test(
        lambda u: is_agente(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
