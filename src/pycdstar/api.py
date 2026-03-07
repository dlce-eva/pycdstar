"""A client for the REST API of cdstar instances."""
import json
import logging
from typing import Union, Any, Literal, Optional, Protocol

import requests

from pycdstar import resource
from pycdstar.config import Config
from pycdstar.exception import CdstarError


log = logging.getLogger(__name__)


class HasPath(Protocol):  # pylint: disable=R0903,C0115
    path: str


class Cdstar:
    """The API client.

    >>> api = Cdstar(service_url='http://example.org', user='user', password='pwd')
    >>> obj = api.get_object()
    """
    def __init__(
            self,
            cfg: Optional[Config] = None,
            service_url: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None):
        """
        Initialize a new client object.

        :param cfg: A `pycdstar.config.Config` object or `None`.
        :param service_url: The base URL of the cdstar service.
        :param user: user name for HTTP basic auth.
        :param password: password for HTTP basic auth.
        :return:
        """
        self.cfg: Config = cfg or Config()
        self.service_url: str = service_url or self.cfg.get('service', 'url')
        user = user or self.cfg.get('service', 'user', default=None)
        password = password or self.cfg.get('service', 'password', default=None)
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)

    def url(self, obj: Union[HasPath, str]) -> str:
        """Compose a full URL representing the object."""
        res = self.service_url
        if res.endswith('/'):
            res = res[:-1]
        return res + getattr(obj, 'path', obj)

    def _req(
            self,
            path: str,
            method: Literal['get', 'head', 'post', 'delete'] = 'get',
            json: bool = True,
            assert_status: int = 200,
            **kw,
    ) -> Union[requests.Response, Any]:
        """Make a request to the API of a cdstar instance.

        :param path: HTTP path.
        :param method: HTTP method.
        :param json: Flag signalling whether the response should be treated as JSON.
        :param assert_status: Expected HTTP response status of a successful request.
        :param kw: Additional keyword parameters will be handed through to the \
        appropriate function of the requests library.
        :return: The return value of the function of the requests library or a decoded \
        JSON object/array.
        """
        method = getattr(self.session, method.lower())
        res = method(self.url(path), **kw)

        status_code = res.status_code
        if json:
            try:
                res = res.json()
            except ValueError:
                log.error(res.text[:1000])
                raise
        if assert_status:
            if not isinstance(assert_status, (list, tuple)):
                assert_status = [assert_status]
            if status_code not in assert_status:
                log.error('got HTTP %s, expected HTTP %s', status_code, assert_status)
                log.error(res.text[:1000] if hasattr(res, 'text') else res)
                raise CdstarError('Unexpected HTTP status code', res, status_code)
        return res

    def get_object(self, uid: Optional[str] = None) -> resource.Object:
        """
        Retrieve an existing or newly created object.

        :param uid: UID of an existing object or `None` to create a new object.
        :return: `pycdstar.resource.Object` instance.
        """
        return resource.Object(self, uid)

    def search(
            self,
            query: Union[dict, str],
            limit: int = 15,
            offset: int = 0,
            index: Optional[Literal['metadata', 'fulltext']] = None,
    ) -> resource.SearchResults:
        """
        Query the search service.

        :param query: The query.
        :param limit: The maximal number of results to return (at most 500).
        :param offset: Use to page through big search result sets.
        :param index: Name of the index to search in (metadata|fulltext) or `None`.
        :return:
        """
        params = {'limit': limit, 'offset': offset}
        if index:
            assert index in ['metadata', 'fulltext']
            params['indexselection'] = index
        if isinstance(query, str):
            query = {"query_string": {"query": query}}
        # elif isinstance(query, ElasticQuery):
        #    query = query.dict()
        assert isinstance(query, dict)
        return resource.SearchResults(self, self._req(
            '/search/',
            method='post',
            params=params,
            headers={'content-type': 'application/json'},
            data=json.dumps(query)))
