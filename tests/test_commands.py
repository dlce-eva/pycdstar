import argparse
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


def test_metadata(api_factory, tmpdir, capsys):
    from pycdstar.commands import metadata

    metadata.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory)), url='a', json=None))
    out, _ = capsys.readouterr()
    assert 'uid' in out
    metadata.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory)), url='a', json='{}'))

    md = tmpdir.join('md.json')
    md.write_text('{"attr": "value"}', encoding='utf8')
    metadata.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory)), url='a', json=str(md)))


def test_delete(api_factory):
    from pycdstar.commands import delete

    delete.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory)), url='a', verbose=True))


def test_ls(api_factory, capsys):
    from pycdstar.commands import ls

    ls.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory, bitstream=[])), url='a', s=False, t=True, r=False))
    ls.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory, bitstream=[])), url='a', s=False, t=False, r=True))
    ls.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory, bitstream=[])), url='a', s=True, t=False, r=False))
    out, _ = capsys.readouterr()
    assert not out
    ls.run(argparse.Namespace(
        api=api_factory(obj=object(api_factory, bitstream=[defaultdict(lambda: 1)])),
        url='a', s=False, t=False, r=False, verbose=False))
    out, _ = capsys.readouterr()
    assert out


def test_create(api_factory):
    from pycdstar.commands import create

    create.run(argparse.Namespace(
        api=api_factory(),
        dir='.',
        metadata='{}',
        include='*.py',
        exclude='*.pyc',
        verbose=True))
