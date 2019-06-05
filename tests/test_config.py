import os

import pytest

from pycdstar.config import Config


@pytest.fixture
def cfg_path(tmpdir):
    return str(tmpdir.join('.config', 'config.ini'))


def test_new_config(cfg_path):
    assert not os.path.exists(cfg_path)
    Config(cfg=cfg_path)
    assert os.path.exists(cfg_path)


def test_existing_config(configfile):
    cfg = Config(cfg=configfile)
    assert cfg.get('service', 'user') == 'user'
    assert cfg.get('a', 'b', default=9) == 9
