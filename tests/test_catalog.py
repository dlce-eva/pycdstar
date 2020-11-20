import os
from time import sleep

import pytest

from unittest.mock import Mock


@pytest.fixture
def catalog_file(tmpdir):
    c = tmpdir.join('catalog.json')
    c.write_text('{}', 'utf8')
    return str(c)


@pytest.fixture
def catalog(catalog_file):
    from pycdstar.catalog import Catalog

    return Catalog(catalog_file)


def test_context_manager(catalog_file):
    from pycdstar.catalog import Catalog, filter_hidden

    mtime = os.stat(catalog_file).st_mtime
    with Catalog(catalog_file) as cat:
        sleep(0.1)
        cat.upload(os.path.dirname(__file__), Mock(), {}, filter_=lambda p: False)
        assert len(cat) == 0
        cat.upload(__file__, Mock(), {}, filter_=filter_hidden)
        cat.upload(os.path.dirname(__file__), Mock(), {})
        stat = cat.stat(os.path.dirname(__file__))
        assert [i for i in stat.values() if not i[0][2]] == []
        assert len(cat)

    with Catalog(catalog_file) as cat:
        cat.delete(Mock(), md5=list(cat.entries.keys())[0])
        cat.delete(Mock(), objid=list(cat.entries.values())[0]['objid'])
        cat.delete(Mock())
        assert len(cat) == 0
    assert os.stat(catalog_file).st_mtime > mtime

def test_misc(catalog):
    catalog.stat('.')
    catalog.stat(__file__, verbose=True)
    assert len(catalog) == 0
    assert catalog.size == 0
    assert catalog.size_h == '0.0B'
