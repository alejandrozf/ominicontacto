from django.utils.translation import ugettext as _

from api_app.views.permissions import TienePermisoOML


class TienePermisoCanalFacebookAgente(TienePermisoOML):
    message = _('No tiene permiso para usar la canalidad Meta Facebook.')

    def has_permission(self, request, view):
        if not super(TienePermisoCanalFacebookAgente, self).has_permission(request, view):
            return False

        if not request.user.is_agente:
            return True

        try:
            agente = request.user.get_agente_profile()
        except Exception:
            return False

        return bool(getattr(agente.grupo, 'meta_facebook_habilitado', False))
