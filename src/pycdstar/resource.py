"""
OO wrappers for CDSTAR resources.
"""
import re
import string
from mimetypes import guess_type
import json
import dataclasses
from typing import TYPE_CHECKING, Optional, Any, Union

if TYPE_CHECKING:
    from pycdstar.api import Cdstar, MethodType  # pragma: no cover


class Resource:
    """A generic CDSTAR resource."""
    def __init__(self, api: 'Cdstar', id: Optional[str] = None, obj=None, **kw):
        """Instantiating a resource with id = None will call its `create` method."""
        self.id = id
        self.obj = obj
        self._api = api
        self._properties = {}

        if id is None:
            self.create(**kw)

    def exists(self) -> bool:
        """Check, if the resource exists in the CDSTAR instance."""
        return self.read(assert_status=[200, 404], json=False).status_code != 404

    def create(self, **_):
        """Resources are managed via REST CRUD methods."""
        raise NotImplementedError

    def read(self, **kw):
        """Resources are managed via REST CRUD methods."""
        return self._api._req(self.path, **kw)  # pylint: disable=W0212

    def update(self, **_):
        """Resources are managed via REST CRUD methods."""
        raise NotImplementedError

    def delete(self):
        """Resources are managed via REST CRUD methods."""
        assert self.id
        return self._api._req(  # pylint: disable=W0212
            self.path, method='delete', assert_status=204, json=False)

    @property
    def service_name(self) -> str:
        """The path component identifying the service serving the resource."""
        return f'{self.__class__.__name__.lower()}s'

    @property
    def path(self) -> str:
        """Full URL path to the resource instance."""
        path = f'/{self.service_name}/'
        if self.obj:
            path += f"{getattr(self.obj, 'id', self.obj)}"
        if self.id:
            if not path.endswith('/'):
                path += '/'
            path += f'{self.id}'
        return path


class Object(Resource):
    """CDSTAR objects are bags of metadata plus associated bitstreams."""
    def create(self, **_):
        res = self._api._req(self.path, method='post', assert_status=201)  # pylint: disable=W0212
        self.id = res['uid']

    def read(self, **_) -> dict:
        self._properties = Resource.read(self)
        return self._properties

    @property
    def metadata(self) -> Optional['Metadata']:
        """The metadata of an object lives in an associated resource."""
        md = Metadata(self._api, id=self.id)
        if md.exists():
            return md
        return None  # pragma: no cover

    @metadata.setter
    def metadata(self, value):
        """Setting the metadata means updating the metadata resource."""
        md = Metadata(self._api, id=self.id)
        if md.exists():
            md.update(metadata=value)
        else:
            md.create(metadata=value)

    @property
    def bitstreams(self) -> list['Bitstream']:
        """The bitstreams associated with the object."""
        if not self._properties:
            self.read()
        return [
            Bitstream(self._api, id=spec['bitstreamid'], obj=self, properties=spec)
            for spec in self._properties['bitstream']]

    def add_bitstream(self, **kw):
        """Create a new bitstream associated with the object."""
        return Bitstream(self._api, obj=self, **kw)

    @property
    def acl(self) -> 'ACL':
        """The Access Control List of the object."""
        return ACL(self._api, id=self.id)


class Metadata(Resource):
    @property
    def service_name(self):
        return 'metadata'

    def _cu(self, method: 'MethodType', **kw):
        return self._api._req(  # pylint: disable=W0212
            self.path,
            method=method,
            assert_status=201,
            data=json.dumps(kw['metadata']),
            headers={'content-type': 'application/json'})

    def create(self, **kw):
        return self._cu('post', **kw)

    def update(self, **kw):
        return self._cu('put', **kw)


class ACL(Resource):
    @property
    def service_name(self):
        return 'accesscontrol'

    def update(self, **kw):
        acl = self.read()
        for permission in ['manage', 'read', 'write']:
            if permission in kw:
                acl[permission] = kw[permission]
        return self._api._req(  # pylint: disable=W0212
            self.path,
            method='put',
            assert_status=200,
            data=json.dumps(acl),
            headers={'content-type': 'application/json'})


class Bitstream(Resource):
    """Bitstreams are binary blobs (aka files) associated with an object."""
    NAME_PATTERN = re.compile(r'[%s0-9_.]+$' % string.ascii_letters)  # pylint: disable=C0209

    def __init__(
            self,
            api: 'Cdstar',
            id: Optional[str] = None,  # pylint: disable=W0622
            obj: Object = None,
            **kw):
        """
        Retrieve an existing or create a new Bitstream.

        A Bitstream is created by uploading a local file, specified by its local path
        passed as `fname` keyword argument.

        :param api: An initialized Cdstar API client.
        :param id: UID of an existing bitstream or `None` to create a new bitstream.
        :param obj: The object the bistream is associated with.
        :param kw: A keyword parameter `mimetype` can be passed to explicitely specify \
        a content-type for the bitstream; a keyword parameter `name` can be passed to \
        specify an explicit Bitstream ID; note that Bitstream IDs are limited to \
        alphanumeric characters, underscore and dot.
        """
        assert obj
        Resource.__init__(self, api, id=id, obj=obj, **kw)
        if 'properties' in kw:
            self._properties = kw['properties']

    def _cu(self, method, **kw):
        content_type = kw.get('mimetype', guess_type(kw['fname'])[0])
        if not content_type:
            content_type = 'application/octet-stream'  # pragma: no cover
        with open(kw['fname'], 'rb') as f:
            _kw = dict(  # pylint: disable=R1735
                method=method,
                data=f,
                assert_status=201,
                headers={'content-type': content_type})
            return self._api._req(self.path, **_kw)  # pylint: disable=W0212

    def create(self, **kw):
        if 'name' in kw:
            assert self.NAME_PATTERN.match(kw['name'])
            self.id = kw['name']
        res = self._cu('post', **kw)
        self.id = res['bitstreamid']

    def update(self, **kw):
        return self._cu('put', **kw)

    def read(self, **_):
        return Resource.read(self, json=False, stream=True).content


@dataclasses.dataclass
class Result:
    """OO wrapper for a JSON search result."""
    source: str
    score: float
    resource: Union[Object, Bitstream]
    _api: 'Cdstar'

    @classmethod
    def from_hit(cls, api, hit: dict[str, Any]):
        """Initialize from JSON hit spec."""
        resource = Object(api, hit['uid'])
        if hit['type'] == 'fulltext':  # type is metadata or fulltext.
            resource = Bitstream(api, id=hit['bitstreamid'], obj=resource)
        return cls(_api=api, source=hit['source'], score=hit['score'], resource=resource)


class SearchResults(list):
    """OO wrapper for JSON search results."""
    def __init__(self, api, res):
        self._api = api
        self.maxscore: float = res['maxscore']
        self.hitcount: int = res['hitcount']
        list.__init__(self, [Result.from_hit(api, hit) for hit in res['hits']])
