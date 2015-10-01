# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase

from mock import MagicMock, patch


class Tests(TestCase):
    def test_main(self):
        from pycdstar.cli import main

        self.assertRaises(SystemExit, main, ['--help'])
        main(['help'])
        main(['help', ['ls']])
        main(['unknown'])

        with patch.multiple('pycdstar.cli', Config=MagicMock(), Cdstar=MagicMock()):
            main(['ls', ['URL']])
            main(['--verbose', 'delete', ['URL']])
