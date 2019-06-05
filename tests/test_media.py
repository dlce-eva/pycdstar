import pytest
from pycdstar.media import Audio, Video, Image, File


@pytest.fixture
def subprocess(mocker):
    class _subprocess(object):
        def check_call(self, args):
            with open(args[-1], 'wb') as fp:
                fp.write(b'test')
            return

        def check_output(self, args):
            return '{"streams":[{"duration":5.5}]}'
    mocker.patch('pycdstar.media.subprocess', _subprocess())


@pytest.fixture
def media_file(request, tmpdir, subprocess):
    fname = tmpdir.join('test.{0}'.format(
        request.param[0] if hasattr(request, 'param') else 'ä ö,ü.ß'))
    fname.write_text('test', 'utf8')
    return (request.param[1] if hasattr(request, 'param') else File)('%s' % fname)


@pytest.mark.parametrize('media_file', [['.wav', Audio], ['.mp3', Audio]], indirect=True)
def test_create_audio(mocker, media_file):
    media_file.create_object(mocker.Mock())


@pytest.mark.parametrize('media_file', [['.mov', Video]], indirect=True)
def test_create_video(mocker, media_file):
    obj, md, bs = media_file.create_object(mocker.Mock())
    assert md['duration'] == pytest.approx(5.5)


@pytest.mark.parametrize('media_file', [['.jpg', Image]], indirect=True)
def test_create_image(mocker, media_file):
    class subprocess(object):
        def check_call(self, args):
            with open(args[-1], 'wb') as fp:
                fp.write(b'test')
            return

        def check_output(self, args):
            return '{0} JPEG 3x5 more'.format(args[-1])

    mocker.patch('pycdstar.media.subprocess', subprocess())
    media_file.create_object(mocker.Mock())


def test_clean_name(media_file):
    assert media_file.clean_name.endswith('a_o_u.ss')


def test_size(media_file):
    assert media_file.size == 4
    assert media_file.size_h == '4.0B'
    assert media_file.format_size(1000000000000000000000000000) == '827.2YiB'


def test_md5(media_file):
    assert media_file.md5 == '098f6bcd4621d373cade4e832627b4f6'


def test_create_object(media_file, mocker):
    media_file.temporary = True
    obj, md, bitstreams = media_file.create_object(mocker.Mock())
    assert 'original' in bitstreams
    assert not media_file.path.exists()


def test_create_object_fail(media_file, mocker):
    """Make sure obj.delete() is called when adding a bitstream fails."""
    class Object(mocker.Mock):
        def add_bitstream(self, *args, **kw):
            raise ValueError

    obj = Object()
    with pytest.raises(ValueError):
        media_file.create_object(mocker.Mock(get_object=lambda: obj))
    assert obj.delete.called
