"""
Functionality to wrap media files suitable for uploading to CDSTAR.
"""
import os
import json
import hashlib
import logging
import pathlib
import subprocess
from string import ascii_letters
from time import time, strftime
from typing import Any, TYPE_CHECKING, Optional, Union
from tempfile import NamedTemporaryFile
from mimetypes import guess_type

from unidecode import unidecode
from clldutils.path import ensure_cmd

import pycdstar
from pycdstar.resource import Bitstream, Object

if TYPE_CHECKING:
    from .api import Cdstar  # pragma: no cover


log = logging.getLogger(pycdstar.__name__)


def ensure_unicode(s):
    if not isinstance(s, str):  # pragma: no cover
        s = s.decode('utf8')
    return s


class File:
    """Any local file."""
    def __init__(
            self,
            path: Union[str, pathlib.Path],
            temporary: bool = False,
            name: Optional[str] = None,
            type: str = 'original',
            mimetype: Optional[str] = None):
        path = pathlib.Path(path)
        assert path.exists() and path.is_file()
        self.path: pathlib.Path = path
        self.temporary: bool = temporary
        self.bitstream_name: str = name or self.clean_name
        self.bitstream_type: str = type
        self._md5 = None
        self.mimetype: str = mimetype or guess_type(self.path.name, strict=False)[0]

    @property
    def ext(self) -> str:
        """Filename extansion."""
        return self.path.suffix.lower()

    @property
    def clean_name(self) -> str:
        """A name suitable for the bitstream instance on CDSTAR."""
        valid_characters = ascii_letters + '._0123456789'
        name = ensure_unicode(self.path.name)
        res = ''.join([c if c in valid_characters else '_' for c in unidecode(name)])
        assert Bitstream.NAME_PATTERN.match(res)
        return res

    @property
    def md5(self) -> str:
        """md5 checksum for the file."""
        if self._md5 is None:
            self._md5 = hashlib.md5()
            with self.path.open(mode="rb") as fp:
                self._md5.update(fp.read())
            self._md5 = self._md5.hexdigest()
        return self._md5

    @property
    def size(self) -> int:
        """The filesize in bytes."""
        return self.path.stat().st_size

    @staticmethod
    def format_size(num) -> str:
        """A filesize as human-readable number."""
        suffix = 'B'
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    @property
    def size_h(self) -> str:
        """The filesize as human-readable number."""
        return self.format_size(self.size)

    def add_bitstreams(self) -> list['File']:
        """
        Derived files to be uploaded as bitstreams for the same object.

        Can be used to add - e.g. - simplified versions of image files, or other formats of audio
        files.
        """
        return []

    def add_metadata(self) -> dict[str, Any]:
        """A dict of metadata to add to the object created for the file."""
        return {}

    def create_object(
            self,
            api: 'Cdstar',
            metadata=None,
    ) -> tuple[Object, dict[str, Any], dict[str, str]]:
        """
        Create an object using the CDSTAR API, with the file content as bitstream.

        :param api:
        :return:
        """
        metadata = {k: v for k, v in (metadata or {}).items()}
        metadata.setdefault('creator', f'{pycdstar.__name__} {pycdstar.__version__}')
        metadata.setdefault('path', f'{self.path}')
        metadata.update(self.add_metadata())
        bitstream_specs = [self] + self.add_bitstreams()
        obj = api.get_object()
        res = {}
        try:
            obj.metadata = metadata
            for file_ in bitstream_specs:
                res[file_.bitstream_type] = file_.add_as_bitstream(obj)
        except:  # noqa: E722
            obj.delete()  # If bitstream creation failed, we delete the new object right away.
            raise
        return obj, metadata, res

    def add_as_bitstream(self, obj: Object) -> str:
        """Add File as bitstream to the specified object."""
        start = time()
        log.info(
            '%s uploading bitstream %s for object %s (%s)...',
            strftime('%H:%M:%S'), self.bitstream_name, obj.id, self.size_h)
        obj.add_bitstream(
            fname=str(self.path), name=self.bitstream_name, mimetype=self.mimetype)
        log.info('... done in %.2f secs', time() - start)
        if self.temporary and self.path.exists():
            self.path.unlink()
        return self.bitstream_name


class Audio(File):
    """
    Audio file handling requires the `lame` command to convert files to mp3.
    """
    def _convert(self):
        with NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            subprocess.check_call([
                ensure_cmd('lame'), '--preset', 'insane', str(self.path), fp.name])
        return fp.name

    def add_bitstreams(self) -> list[File]:
        if self.mimetype == 'audio/mpeg':
            # we only need an alias with correct name!
            path = self.path
            temporary = False
        else:
            path = self._convert()
            temporary = True
        return [File(path, name='web.mp3', type='web', temporary=temporary)]


class Image(File):
    """
    Image file handling requires ImageMagick's `convert` and `identify` commands to
    create different resolutions of a file and determine its dimensions.
    """
    resolutions = {
        'thumbnail': '-thumbnail 103x103^ -gravity center -extent 103x103'.split(),
        'web': '-resize 357x357'.split(),
    }

    def _convert(self, opts):
        with NamedTemporaryFile(delete=False, suffix='.jpg') as fp:
            subprocess.check_call([ensure_cmd('convert'), str(self.path)] + opts + [fp.name])
        return fp.name

    def _identify(self):
        res = ensure_unicode(subprocess.check_output([ensure_cmd('identify'), str(self.path)]))
        assert res.startswith(str(self.path))
        dim = res.replace(str(self.path), '').strip().split()[1]
        return dict(zip(['height', 'width'], map(int, dim.split('x'))))

    def add_bitstreams(self) -> list[File]:
        return [
            File(self._convert(opts), temporary=True, name=type_ + '.jpg', type=type_)
            for type_, opts in self.resolutions.items()]

    def add_metadata(self) -> dict[str, Any]:
        return self._identify()


class Video(File):
    """
    Video file handling requires the `ffmpeg` command to convert files to mp4 and the
    `ffprobe` command to determine the duration of a video.
    """
    def __init__(self, *args, **kw):
        File.__init__(self, *args, **kw)
        self._props = None

    def _ffprobe(self):
        ffprobe = ensure_cmd('ffprobe')
        cmd = f'{ffprobe} -loglevel quiet -print_format json -show_streams'
        return json.loads(ensure_unicode(subprocess.check_output(cmd.split() + [str(self.path)])))

    @property
    def duration(self) -> float:
        if self._props is None:
            self._props = self._ffprobe()
        return float(self._props['streams'][0]['duration'])

    def _ffmpeg(self, iopts, opts, suffix):
        with NamedTemporaryFile(delete=False, suffix=suffix) as fp:
            p = pathlib.Path(fp.name)
            if p.exists():
                p.unlink()
            subprocess.check_call(
                [ensure_cmd('ffmpeg')] + iopts + ['-i', str(self.path)] + opts + [str(p)])
        return fp.name

    def add_bitstreams(self):
        thumbnail_offset = f'-{min([int(self.duration / 2), 20])}'
        res = [File(
            self._ffmpeg(
                ['-itsoffset', thumbnail_offset],
                ['-vcodec', 'mjpeg', '-vframes', '1', '-an', '-f', 'rawvideo'],
                '.jpg'),
            temporary=True,
            name='thumbnail.jpg',
            type='thumbnail')]

        if self.ext in ['.mov', '.qt', '.mod', '.avi']:
            res.append(File(
                self._ffmpeg([], '-c:v libx264'.split(), '.mp4'),
                name=os.path.splitext(self.clean_name)[0] + '.mp4',
                type='mp4'))

        return res

    def add_metadata(self) -> dict:
        return {'duration': self.duration}
