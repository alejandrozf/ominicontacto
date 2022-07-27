import re
from collections import UserList
from email.utils import formataddr
from email.utils import parseaddr
from functools import partial
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from jsonschema import ValidationError
from jsonschema import validate
from yaml import safe_load_all


class Message(EmailMultiAlternatives):

    def __init__(self, context, schema, schema_samples, **kwargs):
        self.context = context
        self.schema = schema
        self.schema_samples = schema_samples
        super().__init__(**kwargs)

    @property
    def bodies(self):
        return {
            "html": next(alt[0]
                         for alt in self.alternatives
                         if alt[1] == "text/html") if self.alternatives else "",
            "text": self.body,
        }

    @property
    def meta(self):
        return {
            "subject": self.subject,
            "from": self.from_email,
            "to": self.to[0] if len(self.to) else self.to,
        }

    def validate(self, raise_exception=True):
        try:
            return validate(
                {
                    "context": self.context,
                    "from": self.from_email,
                    "to": self.to,
                },
                self.schema,
            )
        except ValidationError as error:
            if raise_exception:
                raise error
            else:
                return error


class Messages(UserList):

    def __str__(self):
        return "\n".join(str(data) for data in self.data)

    def append_or_extend(self, item_or_other):
        if isinstance(item_or_other, Messages):
            self.data.extend(item_or_other)
        else:
            self.data.append(item_or_other)

    def validate(self, raise_exception=True):
        return [
            msg.validate(raise_exception) if isinstance(msg, Message) else None for msg in self.data
        ]

    def send(self, fail_silently=False):
        return [msg.send(fail_silently) if isinstance(msg, Message) else None for msg in self.data]


def clean_email(value, regex=re.compile(r"#.*@")):
    if value:
        return regex.sub("@", value)
    return value


def get_absolute_url(request, url):
    return "{proto}://{host}/{url}".format(
        proto="https" if request.is_secure() else "http",
        host=get_current_site(request),
        url=url.lstrip("/"),
    )


def handle__user__created(request, user):
    """
    Sent to user.email from settings.DEFAULT_FROM_EMAIL when user is created.

    args:
    - request
    - user

    body:
    - user fullname
    - user username
    - user password
    - login url
    """
    urls = partial(get_absolute_url, request=request)
    urls_login = partial(urls, url=settings.LOGIN_URL)
    context = {
        "user": {
            "email": user.email,
            "name": user.get_full_name(),
            "password": user._password,
            "username": user.username,
        },
        "urls": {
            "login": urls_login(),
        },
    }
    return (
        context,
        settings.DEFAULT_FROM_EMAIL,
        formataddr((context["user"]["name"], context["user"]["email"])),
    )


def handle__user__password_updated(request, user):
    """
    Sent to user.email from settings.DEFAULT_FROM_EMAIL when user password is updated.

    args:
    - request
    - user

    body:
    - user fullname
    - user username
    - user password
    - login url
    """
    urls = partial(get_absolute_url, request=request)
    urls_login = partial(urls, url=settings.LOGIN_URL)
    context = {
        "user": {
            "email": user.email,
            "name": user.get_full_name(),
            "password": user._password,
            "username": user.username,
        },
        "urls": {
            "login": urls_login(),
        },
    }
    return (
        context,
        settings.DEFAULT_FROM_EMAIL,
        formataddr((context["user"]["name"], context["user"]["email"])),
    )


handlers = {
    "user.created": handle__user__created,
    "user.password-updated": handle__user__password_updated,
}


def create(name, schema_sample=None, schema_validate=True, **kwargs):
    if name not in handlers:
        raise Exception(name)
    schema, schema_samples = safe_load_all(
        render_to_string("message/emsg/{}/schema.yaml.j2".format(name))
    )
    if schema_sample is None:
        context, from_email, to_email = handlers[name](**kwargs)
    else:
        context, from_email, to_email = [
            schema_samples[schema_sample][key] for key in ("context", "from", "to")
        ]
    if isinstance(context, dict):
        msg = Message(
            context,
            schema,
            schema_samples,
            alternatives=[(
                render_to_string("message/emsg/{}/body.html.j2".format(name), context),
                "text/html",
            )],
            body=render_to_string("message/emsg/{}/body.text.j2".format(name), context).strip(),
            from_email=formataddr((parseaddr(from_email)[0], settings.DEFAULT_FROM_EMAIL)),
            reply_to=[from_email],
            subject=render_to_string(
                "message/emsg/{}/subject.text.j2".format(name),
                context,
            ).strip(),
            to=[clean_email(to_email)],
        )
    else:
        msg = Messages([
            Message(
                context_item,
                schema,
                schema_samples,
                alternatives=[(
                    render_to_string("message/emsg/{}/body.html.j2".format(name), context_item),
                    "text/html",
                )],
                body=render_to_string("message/emsg/{}/body.text.j2".format(name), context_item),
                from_email=formataddr((parseaddr(from_email_item)[0], settings.DEFAULT_FROM_EMAIL)),
                reply_to=[from_email_item],
                subject=render_to_string(
                    "message/emsg/{}/subject.text.j2".format(name),
                    context_item,
                ).strip(),
                to=[clean_email(to_email_item)],
            )
            for context_item, from_email_item, to_email_item in zip(context, from_email, to_email)
        ])
    if schema_validate:
        msg.validate()
    return msg
