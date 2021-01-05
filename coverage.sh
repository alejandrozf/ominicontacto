#!/usr/bin/env bash

coverage run manage.py test --settings=ominicontacto.settings.tests
coverage html --title="Coverage for Omnileads"
