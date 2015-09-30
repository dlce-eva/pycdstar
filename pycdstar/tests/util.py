# coding: utf8
from __future__ import unicode_literals
import os
from unittest import TestCase
from tempfile import NamedTemporaryFile

from mock import Mock, MagicMock

from pycdstar.util import pkg_path


def test_file(*comps):
    return pkg_path('tests', 'fixtures', *comps)


def get_api(ret=None, obj=None):
    class MockApi(Mock):
        _req = Mock(return_value=ret or MagicMock(status_code=200))
        get_object = Mock(return_value=obj or MagicMock())
    return MockApi()


class Response(dict):
    def __init__(self, d, status_code=200):
        self.status_code = status_code
        dict.__init__(self, d)


class WithConfigFile(TestCase):
    def setUp(self):
        with NamedTemporaryFile(delete=False) as fp:
            self.config_file = fp.name
            fp.write(b"""
[logging]
level = CRITICAL

[service]
url = http://localhost:9999/
user = user
password = pwd
""")

    def tearDown(self):
        os.remove(self.config_file)
