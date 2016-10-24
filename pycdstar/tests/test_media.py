# coding: utf8
from __future__ import unicode_literals, print_function, division
import os
from unittest import TestCase
from tempfile import NamedTemporaryFile

from mock import Mock, patch
from six import PY2


class TestVideo(TestCase):
    def setUp(self):
        from pycdstar.media import Video

        with NamedTemporaryFile(delete=False, suffix='.avi') as fp:
            fp.write(b"""test""")
            self.file = Video(fp.name)

    def test_create_object(self):
        class subprocess(object):
            def check_call(self, args):
                with open(args[-1], 'w') as fp:
                    fp.write(b'test' if PY2 else 'test')
                return

            def check_output(self, args):
                return '{"streams":[{"duration":5.5}]}'

        with patch('pycdstar.media.subprocess', subprocess()):
            obj, md, bs = self.file.create_object(Mock())
            self.assertAlmostEqual(md['duration'], 5.5)

    def tearDown(self):
        if os.path.exists(self.file.path):
            os.remove(self.file.path)


class TestImage(TestCase):
    def setUp(self):
        from pycdstar.media import Image

        with NamedTemporaryFile(delete=False, suffix='.jpg') as fp:
            fp.write(b"""test""")
            self.file = Image(fp.name)

    def test_create_object(self):
        class subprocess(object):
            def check_call(self, args):
                with open(args[-1], 'w') as fp:
                    fp.write(b'test' if PY2 else 'test')
                return

            def check_output(self, args):
                return 'path JPEG 3x5 more'

        with patch('pycdstar.media.subprocess', subprocess()):
            self.file.create_object(Mock())

    def tearDown(self):
        if os.path.exists(self.file.path):
            os.remove(self.file.path)


class TestFile(TestCase):
    def setUp(self):
        from pycdstar.media import File

        with NamedTemporaryFile(delete=False, suffix='ä ö,ü.ß') as fp:
            fp.write(b"""test""")
            self.file = File(fp.name)

    def test_clean_name(self):
        self.assertTrue(self.file.clean_name.endswith('a_o_u.ss'))

    def test_size(self):
        self.assertEqual(self.file.size, 4)
        self.assertEqual(self.file.size_h, '4.0B')
        self.assertEqual(self.file.format_size(1000000000000000000000000000), '827.2YiB')

    def test_md5(self):
        self.assertEqual(self.file.md5, '098f6bcd4621d373cade4e832627b4f6')

    def test_create_object(self):
        self.file.temporary = True
        obj, md, bitstreams = self.file.create_object(Mock())
        self.assertIn('original', bitstreams)
        self.assertFalse(os.path.exists(self.file.path))

    def test_create_object_fail(self):
        """Make sure obj.delete() is called when adding a bitstream fails."""
        class Object(Mock):
            def add_bitstream(self, *args, **kw):
                raise ValueError

        obj = Object()
        with self.assertRaises(ValueError):
            self.file.create_object(Mock(get_object=lambda: obj))
        self.assertTrue(obj.delete.called)

    def tearDown(self):
        if os.path.exists(self.file.path):
            os.remove(self.file.path)
