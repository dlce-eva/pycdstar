# coding: utf8
from __future__ import unicode_literals

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
