# -*- coding: utf-8 -*-

from django.shortcuts import render


def handler400(request):
    response = render(request, '400.html')
    response.status_code = 400
    return response


def handler403(request):
    response = render('403.html')
    response.status_code = 403
    return response


def handler404(request):
    response = render('404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render('500.html')
    response.status_code = 500
    return response
