# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from facebook_meta_app.api import page_configuration
from facebook_meta_app.api import campaigns


from facebook_meta_app.api import ViewSetRouter

router = ViewSetRouter(trailing_slash=False)

routes = (
    (r"page", page_configuration.MessengerMetaAppPageConfigurationViewSet),
    (r"campaigns", campaigns.MessengerMetaAppCampaignsViewSet),
)

for route in routes:
    router.register(*route)

api_urls_v1 = router.urls

urlpatterns = [
    # Aquí se pueden agregar otras rutas si es necesario
] + api_urls_v1
