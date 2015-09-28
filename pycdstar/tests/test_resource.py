# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase


from mock import MagicMock, Mock


class Tests(TestCase):
    def get_api(self, ret=None):
        class MockApi(Mock):
            _req = Mock(return_value=ret or MagicMock(status_code=200))
        return MockApi()

    def test_Resource(self):
        from pycdstar.resource import Resource

        self.assertRaises(NotImplementedError, Resource, self.get_api())
        rsc = Resource(self.get_api(), id='1')
        self.assertTrue(rsc.exists())
        self.assertRaises(NotImplementedError, rsc.update)
        rsc.delete()

        rsc = Resource(self.get_api(), id='1', obj='2')
        assert rsc.path

    def test_Object(self):
        from pycdstar.resource import Object

        api = self.get_api(ret={'uid': 'abc'})
        obj = Object(api)
        assert api._req.called
        self.assertEquals(obj.id, 'abc')
        self.assertIn('uid', obj.read())

        api = self.get_api()
        obj = Object(api)
        assert obj.metadata
        obj.metadata = {}

        api = self.get_api(ret=MagicMock(status_code=404))
        obj = Object(api)
        obj.metadata = {}
