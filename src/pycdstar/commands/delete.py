"""
Delete an object
"""


def register(parser):  # pylint: disable=C0116
    parser.add_argument('url')


def run(args):  # pylint: disable=C0116
    obj = args.api.get_object(args.url.split('/')[-1])
    obj.delete()
    if args.verbose:
        print(f'deleted object at {args.api.url(obj)}')
