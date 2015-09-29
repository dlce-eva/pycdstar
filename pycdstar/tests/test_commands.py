# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase
from collections import defaultdict

from pycdstar.tests.util import get_api, Response
from pycdstar.resource import Object


def args(d=None):
    return defaultdict(lambda: None, d or {})


def object(**kw):
    kw.setdefault('uid', 'a')
    return Object(get_api(ret=Response(kw)))


class Tests(TestCase):
    def test_metadata(self):
        from pycdstar.commands import metadata

        res = metadata(get_api(obj=object()), args({'<URL>': 'a'}))
        self.assertIn('uid', res)

    def test_ls(self):
        from pycdstar.commands import ls

        res = ls(get_api(obj=object(bitstream=[])), args({'<URL>': 'a'}))
        assert len(list(res)) == 0

    def test_create(self):
        from pycdstar.commands import create

        res = list(create(get_api(), args({'<DIR>': '.'})))
