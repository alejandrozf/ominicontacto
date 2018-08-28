# -*- coding: utf-8 -*-

from django.test.runner import DiscoverRunner
from django.conf import settings


class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """
    def __init__(self, *args, **kwargs):
        settings.OML_TESTING_MODE = True
        super(ManagedModelTestRunner, self).__init__(*args, **kwargs)
