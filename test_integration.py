from time import sleep

from pycdstar.api import Cdstar


def main():
    # Initialize a client object, with connection info from a config file
    cdstar = Cdstar(debug=True)

    # create a new object
    obj = cdstar.get_object()
    # with initially no associated metadata
    assert obj.metadata is None

    # assigning to the metadata property will create a metadata record
    obj.metadata = {"creator": "pycdstar"}

    # retrieve the now existing object
    obj = cdstar.get_object(obj.id)
    assert 'creator' in obj.metadata.read()

    # again, initially the bitstreams property is an empty list
    assert not obj.bitstreams

    # we add a bitstream by uploading a local file
    bitstream = obj.add_bitstream(fname='README.md')
    # and re-read the object
    obj.read()
    # a bitstreams read method returns an iterator to allow for streaming,
    # i.e. chunked downloads
    assert ''.join(list(bitstream.read().decode('utf8')))
    assert len(obj.bitstreams) == 1

    # to make sure the newly created resources are properly indexed, we allow
    # for a short delay
    sleep(1)

    # now we search for a string we know to exist in the uploaded bitstream
    res = cdstar.search('client')
    assert len(res)
    # the first element in the search results list has the bitstream as
    # associated resource
    assert 'client' in ''.join(list(res[0].resource.read().decode('utf8')))

    query = 'pycdstar'
    res = cdstar.search(query, index='metadata')
    assert len(res)
    cdstar.search(query, index='fulltext')
    bitstream.delete()
    obj.delete()


if __name__ == '__main__':
    main()
