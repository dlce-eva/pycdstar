# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase
from collections import defaultdict

from pycdstar.tests.util import get_api, Response
from pycdstar.resource import Object


def args(d=None, default=None):
    return defaultdict(lambda: default, d or {})


def object(**kw):
    kw.setdefault('uid', 'a')
    return Object(get_api(ret=Response(kw)))


class Tests(TestCase):
    def test_metadata(self):
        from pycdstar.commands import metadata

        res = metadata(get_api(obj=object()), args({'<URL>': 'a'}))
        self.assertIn('uid', res)
        metadata(get_api(obj=object()), args({'<URL>': 'a', '<JSON>': '{}'}))

    def test_delete(self):
        from pycdstar.commands import delete

        assert delete(get_api(obj=object()), args({'<URL>': 'a'}), verbose=True)

    def test_ls(self):
        from pycdstar.commands import ls

        res = ls(get_api(obj=object(bitstream=[])), args({'<URL>': 'a', '-s': True}))
        assert len(list(res)) == 0
        res = ls(
            get_api(obj=object(bitstream=[defaultdict(lambda: 1)])),
            args({'<URL>': 'a'}, default=True))
        assert len(list(res)) == 1

    def test_create(self):
        from pycdstar.commands import create

        res = list(create(
            get_api(),
            args({
                '<DIR>': '.',
                '--metadata': '{}',
                '--include': '*.py',
                '--exclude': '*.pyc'}),
            verbose=True))
        assert res
