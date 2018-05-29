# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.timezone import timedelta

register = Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def format_seconds(seconds):
    return str(timedelta(seconds=seconds))
