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
import requests

URL_LINE_HEALTH = 'https://partner.gupshup.io/partner/app/{}/health'
URL_PARTNER_TOKEN = 'https://partner.gupshup.io/partner/account/login'
URL_APP_TOKEN = "https://partner.gupshup.io/partner/app/{}/token"


def get_partner_access_token(provider):
    if 'email_partner' in provider.configuracion and 'password_partner' in provider.configuracion:
        headers = {"accept": "application/json"}
        payload = {
            'email': provider.configuracion['email_partner'],
            'password': provider.configuracion['password_partner']
        }
        response = requests.post(url=URL_PARTNER_TOKEN, headers=headers, data=payload)
        if response.status_code==200:
            return response.json()['token']
    return ''


def get_app_token(app_id, partner_token):
    if app_id and 'partner_token':
        headers = {"accept": "application/json", "Authorization": partner_token}
        response = requests.get(url=URL_APP_TOKEN.format(app_id), headers=headers)
        if response.status_code==200:
            return response.json()['token']['token']
    return ''


def get_line_status(line):
    token = get_partner_access_token(line.proveedor)
    headers = {"accept": "application/json"}
    if token and 'app_id' in line.configuracion:
        app_id = line.configuracion['app_id']
        app_token = get_app_token(app_id, token)
        headers.update({'Authorization': app_token})
        response = requests.get(url=URL_LINE_HEALTH.format(app_id), headers=headers)
        if response.status_code==200:
            return 'LIVE' if response.json()['healthy'] =='true' else '-'
    return '-'
