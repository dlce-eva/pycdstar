"""
Create a new object uploading files from a directory as bitstreams.
"""
import re
import fnmatch
from typing import Optional

from clldutils.clilib import PathType
from clldutils.path import walk

from pycdstar.command_utils import set_metadata


def _split(s, separator=','):
    return [x.strip() for x in (s or '').split(separator) if x.strip()]


def register(parser):  # pylint: disable=C0116
    parser.add_argument('dir', type=PathType(type='dir'))
    parser.add_argument('--metadata', help='Path to metadata in JSON, or JSON literal.')
    parser.add_argument('--include', help='comma-separated list of filename patterns to include.')
    parser.add_argument('--exclude', help='comma-separated list of filename patterns to exclude.')


def run(args):  # pylint: disable=C0116
    def patterns(opt) -> Optional[str]:
        res = _split(opt)
        if res:
            return r'|'.join([fnmatch.translate(x) for x in res])
        return None  # pragma: no cover

    includes = patterns(args.include)
    excludes = patterns(args.exclude)

    obj = args.api.get_object()
    if args.verbose:
        print('object created at')
        print(args.api.url(obj))

    if set_metadata(args.metadata, obj):
        if args.verbose:
            print('adding metadata')
            print(args.api.url(obj.metadata))

    for p in walk(args.dir, mode='files'):
        if excludes and re.match(excludes, p.name):
            continue
        if includes and not re.match(includes, p.name):
            continue
        if not p.stat().st_size:
            continue
        bitstream = obj.add_bitstream(fname=str(p))
        if args.verbose:
            print('adding bitstream')
            print(args.api.url(bitstream))

    print(args.api.url(obj))
