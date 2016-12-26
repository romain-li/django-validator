import io

from django.core.files.base import File
from django.test import TestCase, RequestFactory

from django_validator.decorators import param, POST_OR_GET, HEADER, URI, FILE
from django_validator.exceptions import ValidationError


class DecoratorTest(TestCase):
    """
    Test cases for decorators.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def get(self, view, url='/text', **kwargs):
        request = self.factory.get(url, **kwargs)
        return view(request)

    def post(self, view, url='/text', **kwargs):
        request = self.factory.post(url, **kwargs)
        return view(request)

    def test_decorator(self):
        @param('a')
        def view(request, a):
            self.assertEqual(a, 'a')

        self.get(view, data={'a': 'a'})

    def test_multiple_in(self):
        @param('a', validators='in: a, b')
        def view(request, a):
            self.assertIn(a, ('a'))

        self.get(view, data={'a': 'a'})
        self.get(view, data={'a': 'a'})
        self.get(view, data={'a': 'a'})

    def test_default(self):
        """
        Test decorator with default param.
        """

        # Test param with default value
        @param('a', default='default')
        def view_with_default(request, a):
            self.assertEqual(a, 'default')

        self.get(view_with_default)

        # Test param without default value
        @param('a')
        def view_without_default(request, a):
            self.assertIsNone(a)

        self.get(view_without_default)

    def test_many(self):
        @param('a', type='int', default=[1], many=True, separator='|')
        def view(request, a):
            return a

        self.assertEquals(self.get(view, data={}), [1])
        self.assertEquals(self.get(view, data={'a': '1|2'}), [1, 2])
        with self.assertRaises(ValidationError):
            self.get(view, data={'a': '1|a'})

    def test_related_name(self):
        @param('a', related_name='b', type='int', default=[1], many=True, separator='|', validators='required')
        def view(request, b):
            return b

        self.assertEquals(self.get(view, data={}), [1])
        self.assertEquals(self.get(view, data={'a': '1|2'}), [1, 2])
        with self.assertRaises(ValidationError):
            self.get(view, data={'a': '1|a'})

    def test_verbose_name(self):
        @param('a', verbose_name='b', type='int', default=[1], many=True, separator='|')
        def view(request, a):
            return a

        self.assertEquals(self.get(view, data={}), [1])
        self.assertEquals(self.get(view, data={'a': '1|2'}), [1, 2])
        with self.assertRaisesRegexp(ValidationError, 'b'):
            self.get(view, data={'a': '1|a'})

    def test_file(self):
        """
        Test for file upload decorator.
        """

        @FILE('f', type='file')
        def view(request, f):
            self.assertIsInstance(f, File)

        test_file = io.StringIO()
        self.post(view, data={'f': test_file})

    def test_post_or_get(self):
        @POST_OR_GET('a', type='int', default=0)
        def view(request, a):
            return a

        self.assertEquals(self.get(view, data={'a': 1}), 1)
        self.assertEquals(self.post(view, data={'a': 1}), 1)
        self.assertEquals(self.get(view), 0)

    def test_header(self):
        @HEADER('a', type='int', default=0)
        def view(request, a):
            return a

        self.assertEquals(self.get(view, a='1'), 1)  # Pass header via **extra
        self.assertEquals(self.get(view), 0)

    def test_uri(self):
        @URI('a', type='int', default=0)
        def view(request, a):
            return a

        request = self.factory.get('/test')
        self.assertEquals(view(request, a=1), 1)
        self.assertEquals(view(request, a='1'), 1)
