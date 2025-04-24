from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from import_export import fields
from import_export import widgets
from import_export.resources import ModelResource
from configuracion_telefonia_app.models import DestinoEntrante

from .models import AgenteProfile
from .models import SupervisorProfile
from .models import ClienteWebPhoneProfile
from .models import AutenticacionExternaDeUsuario
from .models import User


class AuthWidget(widgets.Widget):
    VALUES = {
        "LDAP": True,
        "Normal": False,
    }

    def clean(self, value, row=None, **kwargs):
        if value:
            activa = self.VALUES.get(value, None)
            return AutenticacionExternaDeUsuario(activa=activa)

    def render(self, value, obj=None):
        return "LDAP" if value.activa else "Normal"


class EmailWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        if not value and row["profile"] == User.AGENTE:
            raise ValueError(_("Este campo es requerido para un usuario de tipo Agente."))
        return value


class PasswordWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        return make_password(value or None)

    def render(self, value, obj=None):
        return ""


class ProfileField(fields.Field):
    class Widget(widgets.Widget):
        def render(self, group, obj=None):
            if group:
                return group.name
            return ""

    def __init__(self, attribute):
        super().__init__(attribute=attribute, widget=self.Widget())


class UserExportResource(ModelResource):
    profile = ProfileField(attribute="groups__first")
    password = fields.Field(attribute="password", widget=PasswordWidget())
    group = fields.Field(attribute="agenteprofile__grupo__nombre")
    auth = fields.Field(attribute="autenticacion_externa", widget=AuthWidget())

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "profile",
            "email",
            "password",
            "group",
            "auth",
        ]
        export_order = fields


class UserImportResource(ModelResource):
    email = fields.Field(attribute="email", widget=EmailWidget())
    password = fields.Field(attribute="password", widget=PasswordWidget())
    auth = fields.Field(attribute="autenticacion_externa", widget=AuthWidget())

    class Meta:
        model = User
        import_id_fields = ["username"]
        fields = [
            "username",
            "first_name",
            "last_name",
            "groups",
            "email",
            "password",
            "auth",
        ]
        export_order = fields
        use_transactions = True
        force_init_instance = True
        skip_diff = False
        clean_model_instances = True

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        dataset.append_col([None] * len(dataset), header="groups")
        dataset.append_col([None] * len(dataset), header="agenteprofile")
        dataset.append_col([None] * len(dataset), header="clientewebphoneprofile")
        dataset.append_col([None] * len(dataset), header="supervisorprofile")

    def before_import_row(self, row, row_number=None, **kwargs):
        profile = row.get("profile")
        if not profile:
            raise ValidationError({"profile": _("Este valor es requerido.")})
        profiles = kwargs.get("profiles", [])
        if profile not in profiles:
            raise ValidationError({"profile": _(f"El valor '{profile}' no existe.")})
        row["groups"] = profiles[profile]
        if profile == User.AGENTE:
            grupo = row.get("group")
            if not grupo:
                raise ValidationError({"group": _(f"Requerido los usuarios de tipo {profile}.")})
            grupos = kwargs.get("grupos", [])
            if grupo not in grupos:
                raise ValidationError({"group": _(f"El valor {grupo} no existe.")})
            row["agenteprofile"] = {
                "grupo_id": grupos[grupo],
                "reported_by_id": kwargs.get("user").pk,
            }
        elif profile == User.CLIENTE_WEBPHONE:
            row["clientewebphoneprofile"] = {}
        else:
            row["supervisorprofile"] = {
                "is_administrador": profile == User.ADMINISTRADOR,
                "is_customer": profile == User.REFERENTE,
            }

    def init_instance(self, row=None):
        instance = self._meta.model()
        profile = row.get("profile")
        if profile == User.AGENTE:
            instance.is_agente = True
        elif profile == User.CLIENTE_WEBPHONE:
            instance.is_cliente_webphone = True
        else:
            instance.is_supervisor = True
        return instance

    def save_m2m(self, instance, row, using_transactions, dry_run):
        super().save_m2m(instance, row, using_transactions, dry_run)
        profile = row.get("profile")
        if profile == User.AGENTE:
            agente_profile = AgenteProfile.objects.create(
                user_id=instance.pk,
                sip_extension=instance.id + 1000,
                grupo_id=row["agenteprofile"]["grupo_id"],
                reported_by_id=row["agenteprofile"]["reported_by_id"],
            )
            DestinoEntrante.objects.create(
                nombre=instance.username, tipo=DestinoEntrante.AGENTE, content_object=agente_profile
            )
        elif profile == User.CLIENTE_WEBPHONE:
            ClienteWebPhoneProfile.objects.create(
                user_id=instance.pk,
                sip_extension=instance.id + 1000,
            )
        else:
            SupervisorProfile.objects.create(
                user_id=instance.pk,
                sip_extension=instance.id + 1000,
                is_administrador=row["supervisorprofile"]["is_administrador"],
                is_customer=row["supervisorprofile"]["is_customer"],
            )
        if autenticacion_externa := getattr(instance, "autenticacion_externa", None):
            autenticacion_externa.save()
