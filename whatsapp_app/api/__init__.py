# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

from rest_framework import routers


class ViewSetRouter(routers.SimpleRouter):

    def register(self, prefix, viewset, base_name=None):
        if base_name is None:
            base_name = viewset.__module__.rsplit(".", 1)[1].replace("_", "-")
        super(ViewSetRouter, self).register(prefix, viewset, base_name)
