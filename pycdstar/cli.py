# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, print_function
import sys

from docopt import docopt

import pycdstar
from pycdstar.config import Config
from pycdstar.api import Cdstar
from pycdstar import commands


COMMANDS = [getattr(commands, name) for name in dir(commands)]
COMMANDS = {obj.name: obj for obj in COMMANDS if isinstance(obj, commands.Command)}
MAX_CMD_NAME = max([len(name) for name in COMMANDS.keys()])

DOC = """
usage: cdstar [options] <command> [<args>...]

options:
  -h --help         Show this screen.
  --version         Show version.
  -V --verbose      Display status messages verbosely.
  --cfg=<CFG>       Path to config file.
  --service=<URL>   URL of the cdstar service.
  --user=<USER>
  --password=<PWD>

The available commands are:
%s

See 'cdstar help <command>' for more information on a specific command.
""" % '\n'.join(
    '    %s  %s' % (cmd.name.ljust(MAX_CMD_NAME), cmd.desc) for cmd in COMMANDS.values())


def main(argv=None):  # pragma: no cover
    """Main entry point for the cdstar CLI."""
    args = docopt(DOC, version=pycdstar.__version__, argv=argv, options_first=True)
    subargs = [args['<command>']] + args['<args>']

    if args['<command>'] in ['help', None]:
        cmd = None
        if len(subargs) > 1:
            cmd = COMMANDS.get(subargs[1])
        if cmd:
            print(cmd.desc)
            print(cmd.doc)
        else:
            print(DOC)
        sys.exit(0)

    cmd = COMMANDS.get(args['<command>'])
    if not cmd:
        print('unknown command')
        print(DOC)
        sys.exit(0)

    cfg = Config(**dict(
        cfg=args.pop('--cfg', None),
        url=args.pop('--service', None),
        user=args.pop('--user', None),
        password=args.pop('--password', None)))

    try:
        res = cmd(
            Cdstar(cfg=cfg), docopt(cmd.doc, argv=subargs), verbose=args.get('--verbose'))
        sys.exit(res or 0)
    except:
        sys.exit(256)
