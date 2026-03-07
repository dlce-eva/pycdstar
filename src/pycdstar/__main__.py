"""
The CLI of the pycdstar package.
"""
import logging
import sys
import argparse
import contextlib
from typing import Optional

from clldutils.loglib import Logging
from clldutils.clilib import get_parser_and_subparsers, register_subcommands, PathType

from pycdstar.config import Config
from pycdstar.api import Cdstar
import pycdstar.commands


def main(
        args: Optional[list[str]] = None,
        catch_all: bool = False,
        parsed_args: Optional[argparse.Namespace] = None,
        log: Optional[logging.Logger] = None
) -> int:
    """CLI"""
    parser, subparsers = get_parser_and_subparsers('cdstar')
    parser.add_argument(
        '-V', '--verbose', default=False, action='store_true',
        help='Display status messages verbosely.',
    )
    parser.add_argument(
        '--cfg', type=PathType(type='file', must_exist=False),
        help='Path to config file.',
    )
    parser.add_argument('--service', help='URL of the cdstar service.')
    parser.add_argument('--user', help='For the cdstar service.')
    parser.add_argument('--password', help='For the cdstar service.')
    parser.add_argument('--api', help=argparse.SUPPRESS, default=False)

    register_subcommands(subparsers, pycdstar.commands)

    args = parsed_args or parser.parse_args(args=args)
    if not hasattr(args, "main"):  # pragma: no cover
        parser.print_help()
        return 1

    cfg = Config(
        cfg=args.cfg,
        url=args.service,
        user=args.user,
        password=args.password)
    args.api = Cdstar(cfg=cfg)

    with contextlib.ExitStack() as stack:
        if not log:  # pragma: no cover
            stack.enter_context(Logging(args.log, level=args.log_level))
        else:
            args.log = log  # pragma: no cover
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except Exception as e:  # pragma: no cover
            if catch_all:
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
