import os
import unittest

from stango import Manager
from stango.files import Files
from stango.tests import StangoTestCase, make_suite
from stango.tests.util import view_value, view_template

dummy_view = view_value('')

class GenerateTestCase(StangoTestCase):
    def setup(self):
        self.tmp = self.tempdir()
        self.manager = Manager()
        self.manager.index_file = 'index.html'

    def test_generate_simple(self):
        self.manager.files += [
            ('', view_value('foobar')),
            ('barfile.txt', view_value('barfoo')),
        ]
        self.manager.generate(self.tmp)

        self.eq(sorted(os.listdir(self.tmp)), ['barfile.txt', 'index.html'])
        with open(os.path.join(self.tmp, 'index.html')) as fobj:
            self.eq(fobj.read(), 'foobar')
        with open(os.path.join(self.tmp, 'barfile.txt')) as fobj:
            self.eq(fobj.read(), 'barfoo')

    def test_generate_dest_is_non_dir(self):
        self.manager.files = Files(
            ('', dummy_view),
        )

        dest_path = os.path.join(self.tmp, 'dest.txt')
        with open(dest_path, 'w') as fobj:
            fobj.write('foo')

        exc = self.assert_raises(ValueError, self.manager.generate, dest_path)
        self.eq(str(exc), "'%s' is not a directory" % dest_path)

        # Check the file wasn't modified
        self.eq(os.listdir(self.tmp), ['dest.txt'])
        with open(os.path.join(self.tmp, 'dest.txt'), 'r') as fobj:
            self.eq(fobj.read(), 'foo')

    def test_generate_different_index_file(self):
        self.manager.index_file = 'foofile.txt'
        self.manager.files += [
            ('', view_value('foobar')),
            ('barfile.txt', view_value('barfoo')),
        ]
        self.manager.generate(self.tmp)

        self.eq(sorted(os.listdir(self.tmp)), ['barfile.txt', 'foofile.txt'])
        with open(os.path.join(self.tmp, 'foofile.txt')) as fobj:
            self.eq(fobj.read(), 'foobar')
        with open(os.path.join(self.tmp, 'barfile.txt')) as fobj:
            self.eq(fobj.read(), 'barfoo')

    def test_view_returns_a_bytes_object(self):
        self.manager.files = Files(
            ('', view_value(b'\xde\xad\xbe\xef')),
        )
        self.manager.generate(self.tmp)

        self.eq(os.listdir(self.tmp), ['index.html'])
        with open(os.path.join(self.tmp, 'index.html'), 'rb') as fobj:
            self.eq(fobj.read(), b'\xde\xad\xbe\xef')

    def test_view_returns_a_bytearray_object(self):
        self.manager.files = Files(
            ('', view_value(bytearray(b'\xba\xdc\x0f\xfe'))),
        )
        self.manager.generate(self.tmp)

        self.eq(os.listdir(self.tmp), ['index.html'])
        with open(os.path.join(self.tmp, 'index.html'), 'rb') as fobj:
            self.eq(fobj.read(), b'\xba\xdc\x0f\xfe')

    def test_view_renders_a_template(self):
        self.manager.template_dirs.insert(0, self.template_path)
        self.manager.files = Files(
            ('', view_template('value.txt'), {'value': 'foobar'})
        )
        self.manager.generate(self.tmp)

        self.eq(os.listdir(self.tmp), ['index.html'])
        with open(os.path.join(self.tmp, 'index.html')) as fobj:
            self.eq(fobj.read(), 'value is: foobar')

    def test_no_index_file(self):
        self.manager.index_file = None
        self.manager.files = Files(
            ('', dummy_view),
            ('jee/', dummy_view),
        )
        exc = self.assert_raises(ValueError, self.manager.generate, self.tmp)
        self.eq(str(exc), "Incomplete files and no index_file: '', 'jee/'")

    def test_view_returns_None(self):
        self.manager.files = Files(
            ('', view_value(None)),
        )
        exc = self.assert_raises(ValueError, self.manager.generate, self.tmp)
        self.eq(str(exc), "The result of view 'value_returner' for path '' is not a str, bytes or bytearray instance")

    def test_view_returns_an_integer(self):
        self.manager.files = Files(
            ('foo.txt', view_value(1)),
        )
        exc = self.assert_raises(ValueError, self.manager.generate, self.tmp)
        self.eq(str(exc), "The result of view 'value_returner' for path 'foo.txt' is not a str, bytes or bytearray instance")

    def test_post_render_hook(self):
        def post_render_hook(context, data):
            return data + b' hurr durr'

        self.manager.add_hook('post_render_hook', post_render_hook)
        self.manager.files = Files(
            ('', view_value('foobar')),
        )
        self.manager.generate(self.tmp)

        self.eq(os.listdir(self.tmp), ['index.html'])
        with open(os.path.join(self.tmp, 'index.html'), 'rb') as fobj:
            self.eq(fobj.read(), b'foobar hurr durr')

    def test_post_render_hook_returns_None(self):
        self.manager.add_hook('post_render_hook', lambda x, y: None)
        self.manager.files = Files(
            ('', view_value('foobar')),
        )
        exc = self.assert_raises(ValueError, self.manager.generate, self.tmp)
        self.eq(str(exc), 'The result of post_render_hook is not a bytes or bytearray instance for index.html')


def suite():
    return make_suite(GenerateTestCase)
