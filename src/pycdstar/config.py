"""
We allow configuration of a CDSTAR client via config file.
"""
import logging
import pathlib
from configparser import RawConfigParser

from platformdirs import PlatformDirs
from clldutils.misc import NO_DEFAULT

APP_DIRS = PlatformDirs('pycdstar')


class Config(RawConfigParser):
    """Config file for a CDSTAR client."""
    def __init__(self, **kw):
        cfg = kw.pop('cfg', None)
        if cfg:
            cfg_path = pathlib.Path(cfg)
        else:  # pragma: no cover
            cfg_path = pathlib.Path(APP_DIRS.user_config_dir) / 'config.ini'
        cfg_path = cfg_path.resolve()

        RawConfigParser.__init__(self)

        if cfg_path.exists():
            assert cfg_path.is_file()
            self.read(cfg_path)
        else:
            self.add_section('service')
            for opt in 'url user password'.split():
                self.set('service', opt, kw.get(opt, '') or '')
            self.add_section('logging')
            self.set('logging', 'level', 'INFO')

            config_dir = cfg_path.parent
            if not config_dir.exists():
                try:
                    config_dir.mkdir()
                except OSError:  # pragma: no cover
                    # this happens when run on travis-ci, by a system user.
                    pass
            if config_dir.exists():
                with cfg_path.open('w') as fp:
                    self.write(fp)
        level = self.get('logging', 'level', default=None)
        if level:
            logging.basicConfig(level=getattr(logging, level))

    def get(self, section, option, default=NO_DEFAULT, **_):
        if default is not NO_DEFAULT:
            if not self.has_option(section, option):
                return default
        return RawConfigParser.get(self, section, option)
