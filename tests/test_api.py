# coding: utf8
from __future__ import unicode_literals

import pytest
from httmock import all_requests, HTTMock

from pycdstar.config import Config
from pycdstar import resource


@pytest.fixture
def api(configfile):
    from pycdstar.api import Cdstar

    return Cdstar(cfg=Config(cfg=str(configfile)))


@all_requests
def response_content(url, request):
    if url.path == '/objects/' and request.method == 'POST':
        return {'status_code': 201, 'content': b'{"uid": "abc"}'}

    if url.path == '/search/' and request.method == 'POST':
        return {
            'status_code': 200,
            'content': b"""{
    "maxscore": 1,
    "hitcount": 1,
    "hits": [
        {"source": "s", "score": 1, "uid": "a", "type": "fulltext", "bitstreamid": 0}
    ]}"""}


def single_response(status_code=200, content=b"{}"):
    def _r(url, request):
        return {'status_code': status_code, 'content': content}
    return all_requests(_r)


def test_bad_json(api):
    with HTTMock(single_response(content=b'{2: 3}')):
        with pytest.raises(ValueError):
            api._req('/')


def test_bad_status(api):
    from pycdstar.exception import CdstarError

    with HTTMock(single_response(status_code=500)):
        with pytest.raises(CdstarError):
            api._req('/')


def test_get_object(api):
    with HTTMock(response_content):
        obj = api.get_object()
        assert isinstance(obj, resource.Object)
        assert obj.id == 'abc'


def test_search(api):
    with HTTMock(response_content):
        obj = api.search('q', index='metadata')
        assert isinstance(obj, resource.SearchResults)
        assert len(obj) == 1
