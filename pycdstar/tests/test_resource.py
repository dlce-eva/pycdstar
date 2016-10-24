# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase

from mock import MagicMock

from pycdstar.tests.util import test_file, get_api


class Tests(TestCase):
    def test_Resource(self):
        from pycdstar.resource import Resource

        self.assertRaises(NotImplementedError, Resource, get_api())
        rsc = Resource(get_api(), id='1')
        self.assertTrue(rsc.exists())
        self.assertRaises(NotImplementedError, rsc.update)
        rsc.delete()

        rsc = Resource(get_api(), id='1', obj='2')
        assert rsc.path

    def test_Object(self):
        from pycdstar.resource import Object, Bitstream, ACL

        api = get_api(ret={'uid': 'abc'})
        obj = Object(api)
        assert api._req.called
        self.assertEquals(obj.id, 'abc')
        self.assertIn('uid', obj.read())

        api = get_api()
        obj = Object(api)
        assert obj.metadata
        obj.metadata = {}

        api = get_api(ret=MagicMock(status_code=404))
        obj = Object(api)
        obj.metadata = {}

        api = get_api(ret={
            'uid': 1, 'bitstreamid': 0, 'bitstream': [{'bitstreamid': 0}]})
        obj = Object(api)
        self.assertEquals(len(obj.bitstreams), 1)
        bs = obj.add_bitstream(fname=test_file('test.json'), name='test.json')
        self.assertIsInstance(bs, Bitstream)

        api = get_api(ret={'uid': 1, 'read': [], 'write': [], 'manage': []})
        obj = Object(api)
        acl = obj.acl
        self.assertIsInstance(acl, ACL)
        acl.update(read=['me'])
