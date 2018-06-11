# coding: utf8
from __future__ import unicode_literals
import os

import pytest

from pycdstar.resource import Resource, Object, Bitstream, ACL



def test_Resource(api_factory):
    with pytest.raises(NotImplementedError):
        Resource(api_factory())
    rsc = Resource(api_factory(), id='1')
    assert rsc.exists()
    with pytest.raises(NotImplementedError):
        rsc.update()
    rsc.delete()

    rsc = Resource(api_factory(), id='1', obj='2')
    assert rsc.path


def test_Object(api_factory, mocker, test_file):
    api = api_factory(ret={'uid': 'abc'})
    obj = Object(api)
    assert api._req.called
    assert obj.id == 'abc'
    assert 'uid' in obj.read()

    api = api_factory()
    obj = Object(api)
    assert obj.metadata
    obj.metadata = {}

    api = api_factory(ret=mocker.MagicMock(status_code=404))
    obj = Object(api)
    obj.metadata = {}

    api = api_factory(ret={
        'uid': 1, 'bitstreamid': 0, 'bitstream': [{'bitstreamid': 0}]})
    obj = Object(api)
    assert len(obj.bitstreams) == 1
    bs = obj.add_bitstream(fname=test_file, name='test.json')
    assert isinstance(bs, Bitstream)
    bs.update(fname=test_file)
    with pytest.raises(AttributeError):
        bs.read()  # FIXME: find way to actually test this!

    api = api_factory(ret={'uid': 1, 'read': [], 'write': [], 'manage': []})
    obj = Object(api)
    acl = obj.acl
    assert isinstance(acl, ACL)
    acl.update(read=['me'])
