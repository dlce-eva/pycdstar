# coding: utf8
from __future__ import unicode_literals
import json
import fnmatch
import os
import os.path
import re
from datetime import datetime

from pycdstar.util import jsonload


def split(s, separator=','):
    return [x.strip() for x in (s or '').split(separator) if x.strip()]


class Command(object):
    def __init__(self, func, desc):
        self.name = func.__name__
        self.desc = desc
        self.doc = func.__doc__.format('usage: cdstar %s' % self.name)
        self.func = func

    def __call__(self, *args, **kw):
        return self.func(*args, **kw)


def command(desc):
    def wrapper(func):
        return Command(func, desc)
    return wrapper


def set_metadata(spec, obj):
    if spec:
        if os.path.isfile(spec):
            metadata = jsonload(spec)
        else:
            metadata = json.loads(spec)
        obj.metadata = metadata
        return True
    return False


@command("Set or get metadata associated with an object.")
def metadata(api, args, verbose=False):
    """
{0} <URL> [<JSON>]

    <JSON>  Path to metadata in JSON, or JSON literal.
"""
    obj = api.get_object(args['<URL>'].split('/')[-1])
    if not set_metadata(args['<JSON>'], obj):
        print(json.dumps(obj.metadata.read(), indent=4))


@command("Delete an object.")
def delete(api, args, verbose=False):
    """
{0} <URL>
"""
    obj = api.get_object(args['<URL>'].split('/')[-1])
    obj.delete()
    if verbose:
        print('deleted object at')
        print(api.url(obj))


@command("List bitstreams of an object.")
def ls(api, args, verbose=False):
    """
{0} [options] <URL>

options:
    -t  sort by modification time, newest first
    -s  sort by filesize, biggest first
    -r  reverse order while sorting
"""
    obj = api.get_object(args['<URL>'].split('/')[-1])
    res = []
    for bitstream in obj.bitstreams:
        res.append((
            api.url(bitstream),
            bitstream._properties['content-type'],
            bitstream._properties['filesize'],
            datetime.fromtimestamp(bitstream._properties['last-modified'] / 1000.0)
        ))
    if args['-t']:
        res = sorted(res, key=lambda t: t[3], reverse=True)
    elif args['-s']:
        res = sorted(res, key=lambda t: t[2], reverse=True)
    if args['-r']:
        res = reversed(res)

    for r in res:
        if verbose:
            print('{0}\t{1}\t{2:>8}\t{3}'.format(*r))
        else:
            print(r[0])


@command("Create a new object uploading files from a directory as bitstreams.")
def create(api, args, verbose=False):
    """
{0} [options] <DIR>

options:
    --metadata=<JSON>    Path to metadata in JSON, or JSON literal.
    --include=<PATTERNS> comma-separated list of filename patterns to include.
    --exclude=<PATTERNS> comma-separated list of filename patterns to exclude.
    """
    def patterns(opt):
        res = split(opt)
        if res:
            return r'|'.join([fnmatch.translate(x) for x in res])

    includes = patterns(args['--include'])
    excludes = patterns(args['--exclude'])

    obj = api.get_object()
    if verbose:
        print('object created at')
        print(api.url(obj))

    if set_metadata(args['--metadata'], obj):
        if verbose:
            print('adding metadata')
            print(api.url(obj.metadata))

    for root, dirs, files in os.walk(args['<DIR>']):
        # exclude/include files
        files = [os.path.join(root, f) for f in files]
        if excludes:
            files = [f for f in files if not re.match(excludes, f)]
        if includes:
            files = [f for f in files if re.match(includes, f)]

        for fname in files:
            bitstream = obj.add_bitstream(fname=fname)
            if verbose:
                print('adding bitstream')
                print(api.url(bitstream))

    print(api.url(obj))
