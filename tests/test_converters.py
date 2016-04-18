import ddt
from django.test import TestCase

from django_validator.converters import ConverterRegistry, BaseConverter, StringConverter, IntegerConverter, \
    BooleanConverter, FloatConverter


@ddt.ddt
class ConverterTests(TestCase):
    """
    Test cases for converters.
    """

    @ddt.data(
        ('string', 'str', True),
        ('string', None, True),
        ('string', 'int', False),
        ('int', 'integer', True),
        ('int', 'float', False),
        ('bool', 'boolean', True),
    )
    @ddt.unpack
    def test_registry(self, first, second, equals):
        if equals:
            self.assertEquals(ConverterRegistry.get(first), ConverterRegistry.get(second))
        else:
            self.assertNotEquals(ConverterRegistry.get(first), ConverterRegistry.get(second))

    def test_auto_register(self):
        """
        Test auto register for converters.
        """

        class TestConverter(BaseConverter):
            pass

        class TestConverterWithMeta(BaseConverter):
            class Meta:
                name = 'test'

        self.assertEquals(TestConverter, ConverterRegistry.get('TestConverter'))
        self.assertEquals(TestConverterWithMeta, ConverterRegistry.get('test'))

    @ddt.data(
        (StringConverter, 'test', 'test'),
        (StringConverter, None, None),
        (IntegerConverter, '10', 10),
        (IntegerConverter, None, None),
        (FloatConverter, None, None),
        (FloatConverter, '3.1415', 3.1415),
        (FloatConverter, '1.1e-1', 0.11),
        (BooleanConverter, None, False),
        (BooleanConverter, False, False),
        (BooleanConverter, 'false', False),
        (BooleanConverter, 'False', False),
        (BooleanConverter, 0, False),
        (BooleanConverter, 1, True),
        (BooleanConverter, 'true', True),
    )
    @ddt.unpack
    def test_converter(self, converter, value, excepted):
        self.assertEqual(converter.convert('test', value), excepted)
