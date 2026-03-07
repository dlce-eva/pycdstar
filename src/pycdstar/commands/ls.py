"""
List bitstreams of an object.
"""
import datetime


def register(parser):  # pylint: disable=C0116
    parser.add_argument('url')
    parser.add_argument(
        '-t', default=False, action='store_true',
        help='sort by modification time, newest first')
    parser.add_argument(
        '-s', default=False, action='store_true',
        help='sort by filesize, biggest first')
    parser.add_argument(
        '-r', default=False, action='store_true',
        help='reverse order while sorting')


def run(args):  # pylint: disable=C0116
    obj = args.api.get_object(args.url.split('/')[-1])
    res = []
    for bitstream in obj.bitstreams:
        props = bitstream._properties  # pylint: disable=W0212
        res.append((
            args.api.url(bitstream),
            props['content-type'],
            props['filesize'],
            datetime.datetime.fromtimestamp(props['last-modified'] / 1000.0)
        ))
    if args.t:
        res = sorted(res, key=lambda t: t[3], reverse=True)
    elif args.s:
        res = sorted(res, key=lambda t: t[2], reverse=True)
    if args.r:
        res = reversed(res)

    for url, type_, size, modified in res:
        print(f'{url}\t{type_}\t{size:>8}\t{modified}' if args.verbose else url)
