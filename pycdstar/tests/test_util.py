# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase

from pycdstar.tests.util import test_file


class Tests(TestCase):
    def test_(self):
        from pycdstar.util import jsonload, jsondumps

        obj = jsonload(test_file('test.json'))
        self.assertEquals(obj['int'], 5)
        jsondumps(obj)
