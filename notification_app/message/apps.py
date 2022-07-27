import django
from django.utils.translation import ugettext_lazy as _


class Config(django.apps.AppConfig):

    name = "notification_app.message"

    verbose_name = "NotificationMessage"

    def configuraciones_de_permisos(self):
        return [
            {
                "nombre": "notification-message--emsg-list",
                "roles": [
                    "Administrador",
                ]
            },
            {
                "nombre": "notification-message--emsg-detail",
                "roles": [
                    "Administrador",
                ]
            },
        ]

    informacion_de_permisos = {
        "notification-message--emsg-list": {
            "descripcion": _("Lista de los mensajes de correos que el sistema soporta"),
            "version": ""
        },
        "notification-message--emsg-detail": {
            "descripcion": _("Obtiene detalle de un mensaje de correo"),
            "version": ""
        },
    }
