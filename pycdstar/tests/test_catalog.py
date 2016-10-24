# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase
import os
from tempfile import NamedTemporaryFile
from time import sleep

from mock import Mock


class TestCatalog(TestCase):
    def setUp(self):
        with NamedTemporaryFile(delete=False, suffix='.json') as fp:
            fp.write(b"{}")
            self.path = fp.name

    def make_catalog(self):
        from pycdstar.catalog import Catalog

        return Catalog(self.path)

    def test_context_manager(self):
        from pycdstar.catalog import Catalog, filter_hidden

        mtime = os.stat(self.path).st_mtime
        with Catalog(self.path) as cat:
            sleep(0.1)
            cat.upload(os.path.dirname(__file__), Mock(), {}, filter_=lambda p: False)
            self.assertEqual(len(cat), 0)
            cat.upload(__file__, Mock(), {}, filter_=filter_hidden)
            cat.upload(os.path.dirname(__file__), Mock(), {})
            stat = cat.stat(os.path.dirname(__file__))
            self.assertEqual([i for i in stat.values() if not i[0][2]], [])
            self.assertGreater(len(cat), 0)

        with Catalog(self.path) as cat:
            cat.delete(Mock(), md5=list(cat.entries.keys())[0])
            cat.delete(Mock(), objid=list(cat.entries.values())[0]['objid'])
            cat.delete(Mock())
            self.assertEqual(len(cat), 0)
        self.assertGreater(os.stat(self.path).st_mtime, mtime)

    def test_misc(self):
        cat = self.make_catalog()
        cat.stat('.')
        cat.stat(__file__, verbose=True)
        self.assertEqual(len(cat), 0)
        self.assertEqual(cat.size, 0)
        self.assertEqual(cat.size_h, '0.0B')

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
