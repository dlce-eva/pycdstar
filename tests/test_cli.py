import pytest


def test_main(mocker):
    from pycdstar.__main__ import main

    with pytest.raises(SystemExit):
        main(['--help'])

    mocker.patch.multiple(
        'pycdstar.__main__', Config=mocker.MagicMock(), Cdstar=mocker.MagicMock())
    main(['ls', 'URL'])
    main(['--verbose', 'delete', 'URL'])
