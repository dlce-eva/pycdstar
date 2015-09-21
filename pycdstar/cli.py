#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cdstar

Usage:
  cdstar create <what> <properties>
  cdstar [options] retrieve <what> <id>
  cdstar delete <what> <id>
  cdstar -h | --help
  cdstar --version

Options:
  -h --help        Show this screen.
  --version        Show version.
  --service=<URL>  URL of the cdstar service
"""

from __future__ import unicode_literals, print_function
import sys

from docopt import docopt

from pycdstar.config import Config
from pycdstar.api import Cdstar


__version__ = "0.1.1"
__author__ = "Robert Forkel"
__license__ = "MIT"


def parsed_kw(s):
    return {k: v for k, v in [pair.split('=') for pair in s.split(';')]}


def checked_call(f, *args, **kw):
    try:
        return f(*args, **kw)
    except AssertionError:
        return Exception()


def main(argv=None):  # pragma: no cover
    """Main entry point for the cdstar CLI."""
    cfg = Config()
    args = docopt(__doc__, version=__version__, argv=argv)
    api = Cdstar(cfg, service_url=args['--service'])
    if args['retrieve']:
        return checked_call(getattr(api, args['<what>']), id=args['<id>'])
    if args['create']:
        return checked_call(api.create, args['<what>'], **parsed_kw(args['<properties>']))
    if args['delete']:
        return checked_call(
            api.delete, checked_call(getattr(api, args['<what>']), id=args['<id>']))


if __name__ == '__main__':  # pragma: no cover
    res = main()
    if isinstance(res, Exception):
        status = -1
    else:
        status = 0
        print(res)
    sys.exit(status)
