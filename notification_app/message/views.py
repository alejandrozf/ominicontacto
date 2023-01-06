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
from inspect import getargspec
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView
from notification_app.message import emsg


class EmailListView(TemplateView):
    template_name = "message/emsg/list.html.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = []
        for template, handler in emsg.handlers.items():
            item = {
                "document": "\n".join([line.strip() for line in handler.__doc__.split("\n")]),
                "template": template,
                "urls": [
                    (
                        "schema-sample",
                        reverse("notification-message--emsg-detail", kwargs={"pk": template}),
                    ),
                ],
            }
            if self.request.user.is_superuser:
                params = {key: "~" for key in getargspec(handler).args[1:]}
                item["urls"].append((
                    "random-sample",
                    "{}?{}".format(item["urls"][0][1], urlencode(params)),
                ))
            items.append(item)
        context["items"] = items
        return context


class EmailDetailView(TemplateView):
    template_name = "message/emsg/detail.html.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        msgs = emsg.Messages()
        emsgs_kwargs = {
            "request": self.request
        }
        if self.request.GET:
            if not self.request.user.is_superuser:
                raise PermissionDenied
            if "user" in self.request.GET:
                key = "user"
                mgr = apps.get_model("ominicontacto_app.User").objects.all()
                val = self.request.GET[key]
                emsgs_kwargs[key] = mgr.order_by("?").first() if val == "~" else mgr.get(pk=val)
                emsgs_kwargs[key]._password = "[hidden]"
            msg = emsg.create(kwargs["pk"], **emsgs_kwargs)
            source = [(k, getattr(v, "pk", ""), str(v)) for k, v in emsgs_kwargs.items()]
        else:
            emsgs_kwargs["schema_sample"] = "default"
            msg = emsg.create(kwargs["pk"], **emsgs_kwargs)
            source = []
        msgs.append_or_extend(msg)
        msgs.validate()
        context["msgs"] = msgs
        context["source"] = sorted(source)
        return context
