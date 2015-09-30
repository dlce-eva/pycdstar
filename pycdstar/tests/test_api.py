# coding: utf8
from __future__ import unicode_literals

from httmock import all_requests, HTTMock

from pycdstar.config import Config
from pycdstar.tests.util import WithConfigFile
from pycdstar import resource


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


class Tests(WithConfigFile):
    def setUp(self):
        from pycdstar.api import Cdstar

        WithConfigFile.setUp(self)
        self.api = Cdstar(cfg=Config(cfg=self.config_file))

    def test_bad_json(self):
        with HTTMock(single_response(content=b'{2: 3}')):
            self.assertRaises(ValueError, self.api._req, '/')

    def test_bad_status(self):
        from pycdstar.exception import CdstarError

        with HTTMock(single_response(status_code=500)):
            self.assertRaises(CdstarError, self.api._req, '/')

    def test_get_object(self):
        with HTTMock(response_content):
            obj = self.api.get_object()
            self.assertIsInstance(obj, resource.Object)
            self.assertEquals(obj.id, 'abc')

    def test_search(self):
        with HTTMock(response_content):
            obj = self.api.search('q', index='metadata')
            self.assertIsInstance(obj, resource.SearchResults)
            self.assertEquals(len(obj), 1)
