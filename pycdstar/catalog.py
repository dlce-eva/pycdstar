# coding: utf8
from __future__ import unicode_literals, print_function, division
import os
from collections import OrderedDict, defaultdict
import json
from mimetypes import guess_type

from six import PY3

from pycdstar.util import jsonload
from pycdstar.media import File, Video, Image


def filter_hidden(p):
    return not os.path.basename(p).startswith('.')


class Catalog(object):
    def __init__(self, path):
        self.path = path
        self.entries = jsonload(self.path) if os.path.exists(self.path) else {}

    def __enter__(self):
        return self

    def __len__(self):
        return len(self.entries)

    @property
    def size(self):
        return sum(d['size'] for d in self.entries.values())

    @property
    def size_h(self):
        return File.format_size(self.size)

    def stat(self, path, verbose=False):
        stats = defaultdict(list)
        assert os.path.exists(path)
        if os.path.isfile(path):
            self.update_stat(path, stats)
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for fname in filenames:
                    self.update_stat(os.path.join(dirpath, fname), stats)
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

        print('uploaded: {0} in {1} files ({2} distinct)'.format(
            File.format_size(insize), infiles, indistinct))
        print('todo: {0} in {1} files ({2} distinct)'.format(
            File.format_size(outsize), outfiles, outdistinct))
        return stats

    def update_stat(self, path, stats):
        file_ = File(path)
        md5 = file_.md5
        stats[md5].append((file_.path, file_.size, md5 in self.entries))

    def upload(self, path, api, metadata, filter_=None):
        start = len(self)
        if os.path.isfile(path):
            self.upload_one(path, api, metadata, filter_=filter_)
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for fname in filenames:
                    self.upload_one(os.path.join(dirpath, fname), api, metadata, filter_=filter_)
        return len(self) - start

    def upload_one(self, path, api, metadata, filter_=None):
        if filter_ and not filter_(path):
            return

        if path.endswith('.MOD'):
            cls = Video  # pragma: no cover
        else:
            mimetype = (guess_type(path)[0] or '').split('/')[0]
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
            except:  # pragma: no cover
                pass
        return c

    def __exit__(self, *args):
        self.write()

    def write(self):
        ordered = OrderedDict()
        for md5 in sorted(self.entries.keys()):
            ordered[md5] = OrderedDict([i for i in sorted(self.entries[md5].items())])

        _kw = dict(mode='w')
        if PY3:  # pragma: no cover
            _kw['encoding'] = 'utf8'
        with open(self.path, **_kw) as fp:
            return json.dump(ordered, fp, indent=4)
