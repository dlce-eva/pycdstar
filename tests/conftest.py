from __future__ import unicode_literals
import os

import pytest


@pytest.fixture
def test_file():
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'test.json')


@pytest.fixture
def configfile(tmpdir):
    tmpdir.join('config.ini').write_text("""
[logging]
level = CRITICAL
[service]
url = http://localhost:9999/
user = user
password = pwd""", 'utf8')
    return str(tmpdir.join('config.ini'))


@pytest.fixture
def api_factory(mocker):
    def _api(ret=None, obj=None):
        class MockApi(mocker.Mock):
            _req = mocker.Mock(return_value=ret or mocker.MagicMock(status_code=200))
            get_object = mocker.Mock(return_value=obj or mocker.MagicMock())
        return MockApi()
    return _api
