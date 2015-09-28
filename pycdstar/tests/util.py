# coding: utf8
from __future__ import unicode_literals

from pycdstar.util import pkg_path


def test_file(*comps):
    return pkg_path('tests', 'fixtures', *comps)
