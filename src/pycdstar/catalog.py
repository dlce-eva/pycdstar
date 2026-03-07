"""
A CDSTAR catalog is a local registry of the objects uploaded to a CDSTAR instance.
"""
from collections import OrderedDict, defaultdict
import json
from mimetypes import guess_type
import pathlib
from typing import Union, Any

from clldutils.path import walk

from pycdstar.api import Cdstar
from pycdstar.media import File, Video, Image


def filter_hidden(p):
    return not p.stem.startswith('.')


def iter_files(path):
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
        return File.format_size(self.size)

    def stat(self, path, verbose=False):
        """Prints a report about the upload status of files in a directory."""
        stats: dict[str, list[tuple[pathlib.Path, int, bool]]] = defaultdict(list)
        for fname in iter_files(path):
            self.update_stat(fname, stats)
        insize, infiles, indistinct = 0, 0, 0
        outsize, outfiles, outdistinct = 0, 0, 0
        for md5, files in stats.items():
            for i, (path, size, in_catalog) in enumerate(files):
                if i == 0:
                    if in_catalog:
                        indistinct += 1
                    else:
                        outdistinct += 1
                        if verbose:
                            print(path)

                if in_catalog:
                    insize += size
                    infiles += 1
                else:
                    outsize += size
                    outfiles += 1

        print(f'uploaded: {File.format_size(insize)} in {infiles} files ({indistinct} distinct)')
        print(f'todo: {File.format_size(outsize)} in {outfiles} files ({outdistinct} distinct)')
        return stats

    def update_stat(
            self,
            path: pathlib.Path,
            stats: dict[str, list[tuple[pathlib.Path, int, bool]]]) -> None:
        """Add stats for the file identified by path."""
        file_ = File(path)
        md5 = file_.md5
        stats[md5].append((file_.path, file_.size, md5 in self.entries))

    def upload(self, path, api: Cdstar, metadata, filter_=None):
        start = len(self)
        for fname in iter_files(path):
            self.upload_one(fname, api, metadata, filter_=filter_)
        return len(self) - start

    def upload_one(self, path, api, metadata, filter_=None):
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
            res = {'objid': '%s' % obj.id, 'size': file_.size}
            res.update(md)
            res.update(bitstreams)
            self.entries[file_.md5] = res

    def delete(self, api, objid=None, md5=None):
        objs = set()
        if md5:
            objs.add((md5, self.entries[md5]['objid']))
        if objid:
            for md5, d in self.entries.items():
                if d['objid'] == objid:
                    objs.add((md5, objid))
                    break
        if objid is None and md5 is None:
            objs = set((md5, d['objid']) for md5, d in self.entries.items())
        c = 0
        for md5, objid in objs:
            try:
                obj = api.get_object(objid)
                obj.delete()
                del self.entries[md5]
                c += 1
            except:  # noqa: E722; # pragma: no cover
                pass
        return c

    def __exit__(self, *args):
        self.write()

    def write(self):
        ordered = OrderedDict()
        for md5 in sorted(self.entries.keys()):
            ordered[md5] = OrderedDict(sorted(self.entries[md5].items()))

        with self.path.open(mode='w', encoding='utf8') as fp:
            return json.dump(ordered, fp, indent=4)
