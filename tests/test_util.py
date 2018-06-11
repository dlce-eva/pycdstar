import os

from pycdstar.util import jsonload, jsondumps, pkg_path


def test_(test_file):
    obj = jsonload(test_file)
    assert obj['int'] == 5
    jsondumps(obj)


def test_pkg_path():
    assert os.path.exists(pkg_path('__main__.py'))
