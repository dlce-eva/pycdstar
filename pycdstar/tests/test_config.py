# coding: utf8
from __future__ import unicode_literals
import os
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree

from pycdstar.tests.util import WithConfigFile


class ConfigTest(TestCase):
    def setUp(self):
        self.tmp = mkdtemp()
        self.cfg = os.path.join(self.tmp, '.config', 'config.ini')

    def tearDown(self):
        rmtree(self.tmp, ignore_errors=True)

    def test_new_config(self):
        from pycdstar.config import Config

        self.assertFalse(os.path.exists(self.cfg))
        Config(cfg=self.cfg)
        self.assertTrue(os.path.exists(self.cfg))


class Tests2(WithConfigFile):
    def test_existing_config(self):
        from pycdstar.config import Config

        cfg = Config(cfg=self.config_file)
        self.assertEqual(cfg.get('service', 'user'), 'user')
        self.assertEquals(cfg.get('a', 'b', default=9), 9)
