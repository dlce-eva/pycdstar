# pycdstar
Python client library for CDStar

[![Documentation Status](https://readthedocs.org/projects/pycdstar/badge/?version=latest)](http://pycdstar.readthedocs.org/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/clld/pycdstar.svg?branch=master)](https://travis-ci.org/clld/pycdstar)
[![codecov.io](http://codecov.io/github/clld/pycdstar/coverage.svg?branch=master)](http://codecov.io/github/clld/pycdstar?branch=master)


## Usage

```python
    from pycdstar.api import Cdstar

    # Initialize a client object, with connection info from a config file
    cdstar = Cdstar()

    # create a new object
    obj = cdstar.get_object()
    # with initially no associated metadata
    assert obj.metadata is None

    # assigning to the metadata property will create a metadata record
    obj.metadata = {"creator": "pycdstar"}

    # retrieve the now existing object
    obj = cdstar.get_object(obj.id)
    assert 'creator' in obj.metadata

    # again, initially the bitstreams property is an empty list
    assert not obj.bitstreams

    # we add a bitstream by uploading a local file
    bitstream = obj.add_bitstream(fname='README.txt')
    # and re-read the object
    obj.read()
    # a bitstreams read method returns an iterator to allow for streaming,
    # i.e. chunked downloads
    assert ''.join(list(bitstream.read()))
    assert len(obj.bitstreams) == 1

    # to make sure the newly created resources are properly indexed, we allow
    # for a short delay
    sleep(1)

    # now we search for a string we know to exist in the uploaded bitstream
    res = cdstar.search('ssh')
    assert len(res)
    # the first element in the search results list has the bitstream as
    # associated resource
    assert 'ssh' in ''.join(list(res[0].resource.read()))

    query = 'pycdstar'
    res = cdstar.search(query, index='metadata')
    assert len(res)
    res = cdstar.search(query, index='fulltext')
    assert not len(res)
    bitstream.delete()
    obj.delete()
```