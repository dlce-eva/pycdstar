# coding: utf8
from __future__ import unicode_literals
from collections import defaultdict

from pycdstar.resource import Object


class Response(dict):
    def __init__(self, d, status_code=200):
        self.status_code = status_code
        dict.__init__(self, d)


def args(d=None, default=None):
    return defaultdict(lambda: default, d or {})


def object(api_factory, **kw):
    kw.setdefault('uid', 'a')
    return Object(api_factory(ret=Response(kw)))


def test_metadata(api_factory):
    from pycdstar.commands import c_metadata

    res = c_metadata(api_factory(obj=object(api_factory)), args({'<URL>': 'a'}))
    assert 'uid' in res
    c_metadata(api_factory(obj=object(api_factory)), args({'<URL>': 'a', '<JSON>': '{}'}))


def test_delete(api_factory):
    from pycdstar.commands import c_delete

    assert c_delete(api_factory(obj=object(api_factory)), args({'<URL>': 'a'}), verbose=True)


def test_ls(api_factory):
    from pycdstar.commands import c_ls

    res = c_ls(api_factory(obj=object(api_factory, bitstream=[])), args({'<URL>': 'a', '-s': True}))
    assert len(list(res)) == 0
    res = c_ls(
        api_factory(obj=object(api_factory, bitstream=[defaultdict(lambda: 1)])),
        args({'<URL>': 'a'}, default=True))
    assert len(list(res)) == 1


def test_create(api_factory):
    from pycdstar.commands import c_create

    res = list(c_create(
        api_factory(),
        args({
            '<DIR>': '.',
            '--metadata': '{}',
            '--include': '*.py',
            '--exclude': '*.pyc'}),
        verbose=True))
    assert res
