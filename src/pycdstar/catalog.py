"""
A CDSTAR catalog is a local registry of the objects uploaded to a CDSTAR instance.
"""
from collections import OrderedDict, defaultdict
import json
from mimetypes import guess_type
import pathlib
import dataclasses
from typing import Union, Any, Optional, Callable

from clldutils.path import walk

from pycdstar.api import Cdstar
from pycdstar.media import File, Video, Image


@dataclasses.dataclass
class Stats:
    size: int = 0
    files: int = 0
    distinct: int = 0

    def __str__(self):
        return f'{File.format_size(self.size)} in {self.files} files ({self.distinct} distinct)'


def filter_hidden(p: pathlib.Path) -> bool:
    """Predefined filter for hidden files."""
    return not p.stem.startswith('.')


def iter_files(path: Union[str, pathlib.Path]):
    """Yield files from path."""
    path = pathlib.Path(path)
    assert path.exists()
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from walk(path, mode='files')


class Catalog:
    """
    A catalog storing CDSTAR bitstream metadata.

    To be used as updateable context when uploading objects.
    """
    def __init__(self, path: Union[str, pathlib.Path]):
        self.path: pathlib.Path = pathlib.Path(path)
        # Entries in the catalog are keyed by md5 sum of the corresponding file.
        self.entries: dict[str, Any] = {}
        if self.path.exists():
            with self.path.open(encoding='utf8') as fp:
                self.entries = json.load(fp)

    def __enter__(self):
        return self

    def __len__(self):
        return len(self.entries)

    @property
    def size(self) -> int:
        """
        Accumulated filesizes of the bitstreams recorded in the catalog.
        """
        return sum(d['size'] for d in self.entries.values())

    @property
    def size_h(self) -> str:
        """Human-readable size of the catalog."""
        return File.format_size(self.size)

    def stat(self, path, verbose=False):
        """Prints a report about the upload status of files in a directory."""
        stats: dict[str, list[tuple[pathlib.Path, int, bool]]] = defaultdict(list)
        for fname in iter_files(path):
            self.update_stat(fname, stats)
        instats = Stats()
        outstats = Stats()
        for _, files in stats.items():
            for i, (p, size, in_catalog) in enumerate(files):
                if i == 0:
                    if in_catalog:
                        instats.distinct += 1
                    else:
                        outstats.distinct += 1
                        if verbose:
                            print(p)

                if in_catalog:
                    instats.size += size
                    instats.files += 1
                else:
                    outstats.size += size
                    outstats.files += 1

        print(f'uploaded: {instats}')
        print(f'todo: {outstats}')
        return stats

    def update_stat(
            self,
            path: pathlib.Path,
            stats: dict[str, list[tuple[pathlib.Path, int, bool]]]) -> None:
        """Add stats for the file identified by path."""
        file_ = File(path)
        md5 = file_.md5
        stats[md5].append((file_.path, file_.size, md5 in self.entries))

    def upload(
            self,
            path: Union[str, pathlib.Path],
            api: Cdstar,
            metadata: dict,
            filter_: Optional[Callable[[Union[str, pathlib.Path]], bool]] = None,
    ) -> int:
        """Upload files from path."""
        start = len(self)
        for fname in iter_files(path):
            self.upload_one(fname, api, metadata, filter_=filter_)
        return len(self) - start

    def upload_one(
            self,
            path: Union[str, pathlib.Path],
            api: Cdstar,
            metadata: dict,
            filter_: Optional[Callable[[str], bool]] = None):
        """Conditionally upload a file."""
        if filter_ and not filter_(path):
            return

        if path.suffix == '.MOD':
            cls = Video  # pragma: no cover
        else:
            mimetype = (guess_type(path.name)[0] or '').split('/')[0]
            cls = {'video': Video, 'image': Image}.get(mimetype, File)
        file_ = cls(path)
        if file_.md5 not in self.entries:
            obj, md, bitstreams = file_.create_object(api, metadata)
            res = {'objid': f'{obj.id}', 'size': file_.size}
            res.update(md)
            res.update(bitstreams)
            self.entries[file_.md5] = res

    def delete(self, api: Cdstar, objid: Optional[str] = None, md5: Optional[str] = None) -> int:
        """Delete an object from the catalog."""
        objs = set()
        if md5:
            objs.add((md5, self.entries[md5]['objid']))
        if objid:
            for md5_, d in self.entries.items():
                if d['objid'] == objid:
                    objs.add((md5_, objid))
                    break
        if objid is None and md5 is None:
            objs = set((md5, d['objid']) for md5, d in self.entries.items())
        c = 0
        for md5_, objid_ in objs:
            try:
                obj = api.get_object(objid_)
                obj.delete()
                del self.entries[md5_]
                c += 1
            except:  # noqa: E722; # pragma: no cover  # pylint: disable=bare-except
                pass
        return c

    def __exit__(self, *args):
        self.write()

    def write(self):
        """Write the catalog to disk."""
        ordered = OrderedDict()
        for md5 in sorted(self.entries.keys()):
            ordered[md5] = OrderedDict(sorted(self.entries[md5].items()))

        with self.path.open(mode='w', encoding='utf8') as fp:
            return json.dump(ordered, fp, indent=4)
