"""
Set or get metadata associated with an object
"""
import json

from pycdstar.command_utils import set_metadata


def register(parser):  # pylint: disable=C0116
    parser.add_argument('url')
    parser.add_argument('json', nargs='?', default=None)


def run(args):  # pylint: disable=C0116
    obj = args.api.get_object(args.url.split('/')[-1])
    if not set_metadata(args.json, obj):
        print(json.dumps(obj.metadata.read(), indent=4))
