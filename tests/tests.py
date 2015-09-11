import unittest
from django.http import HttpRequest
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django_validator.converters import ConverterRegistry, BaseConverter
from django_validator.decorators import param, GET, POST
from django_validator.validators import ValidatorRegistry, RequiredValidator, MaxValidator, InValidator, MinValidator, \
    BetweenValidator, RegexValidator, IntegerValidator, NumericValidator, BaseValidator


class FakeRequest(HttpRequest):
    def __init__(self, method='GET', get=None, post=None):
        super(FakeRequest, self).__init__()
        self.query_params = self._param_to_string(get or {})
        self.data = self._param_to_string(post or {})
        self.method = method

    @staticmethod
    def _param_to_string(params):
        """
        Convert all params to string, because in the request, all the params are string.
        """
        if params:
            params = params.copy()
            for key, value in params.iteritems():
                params[key] = str(value)
        return params

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def test(cls, func, **kwargs):
        """
        Create a fake request and perform the view function.
        """
        return func(cls.create(**kwargs))


class ConverterTest(unittest.TestCase):
    """
    Test cases for converters.
    """

    def setUp(self):
        self.test = FakeRequest.test

    def test_registry(self):
        # Test string converter and default converter
        string_converter = ConverterRegistry.get('string')
        self.assertIsNotNone(string_converter)
        self.assertEquals(string_converter, ConverterRegistry.get('str'))
        self.assertEquals(string_converter, ConverterRegistry.get(None))

        self.assertNotEquals(string_converter, ConverterRegistry.get('int'))
        self.assertNotEquals(string_converter, ConverterRegistry.get('integer'))
        self.assertNotEquals(string_converter, ConverterRegistry.get('float'))
        self.assertNotEquals(string_converter, ConverterRegistry.get('bool'))
        self.assertNotEquals(string_converter, ConverterRegistry.get('boolean'))

        # Test auto register for converters
        class TestConverter(BaseConverter):
            @staticmethod
            def convert(key, value):
                return value

        self.assertEquals(TestConverter, ConverterRegistry.get('TestConverter'))

    def test_integer_converter(self):
        @GET('offset', type='int')
        @GET('limit', type='integer')
        def view(request, offset, limit):
            return offset, limit

        self.assertEqual(self.test(view, get={}), (None, None))
        self.assertEqual(self.test(view, get={'offset': 10, 'limit': 10}), (10, 10))

    def test_float_converter(self):
        @GET('timestamp', type='float')
        def view(request, timestamp):
            return timestamp

        self.assertEqual(self.test(view, get={}), None)
        self.assertEqual(self.test(view, get={'timestamp': '1.1e-1'}), 0.11)

    def test_boolean_converter(self):
        @GET('test', type='bool')
        def view(request, test):
            return test

        self.assertEqual(self.test(view, get={}), False)
        self.assertEqual(self.test(view, get={'test': False}), False)
        self.assertEqual(self.test(view, get={'test': 'false'}), False)
        self.assertEqual(self.test(view, get={'test': 'False'}), False)
        self.assertEqual(self.test(view, get={'test': 1}), True)
        self.assertEqual(self.test(view, get={'test': 100}), True)
        self.assertEqual(self.test(view, get={'test': 'true'}), True)


class DecoratorTest(unittest.TestCase):
    """
    Test cases for decorators.
    """

    def setUp(self):
        self.test = FakeRequest.test

    def test_decorator(self):
        @param('a')
        def view(request, a):
            self.assertEqual(a, 'a')

        self.test(view, get={'a': 'a'})

        class ModelView(generics.RetrieveAPIView):
            @param('a')
            def filter_queryset(self, queryset, a):
                return a

        model_view = ModelView()
        model_view.request = FakeRequest.create(get={'a': 'a'})
        self.assertEquals(model_view.filter_queryset(None), 'a')

    def test_default(self):
        # Test param with default value
        @param('a', default='default')
        def view_with_default(request, a):
            self.assertEqual(a, 'default')

        self.test(view_with_default, get={})

        # Test param without default value
        @param('a')
        def view_without_default(request, a):
            self.assertIsNone(a)

        self.test(view_without_default, get={})

    def test_many(self):
        @param('a', type='int', default=[1], many=True, separator='|')
        def view(request, a):
            return a

        self.assertEquals(self.test(view, get={}), [1])
        self.assertEquals(self.test(view, get={'a': '1|2'}), [1, 2])
        with self.assertRaises(ValidationError):
            self.test(view, get={'a': '1|a'})


class ValidatorTest(unittest.TestCase):
    """
    Test cases for validators.
    """

    @staticmethod
    def _validator(validator, value):
        return validator('test', {'test': value})

    def test_registry(self):
        # Test the default validator registry
        validators = ValidatorRegistry.get_validators('required | max: 5 | in : 1, 3')
        self.assertEquals(len(validators), 3)
        self.assertIsInstance(validators[0], RequiredValidator)
        self.assertIsInstance(validators[1], MaxValidator)
        self.assertIsInstance(validators[2], InValidator)

    def test_required_validator(self):
        validator = RequiredValidator()
        self.assertTrue(self._validator(validator, 'test'))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, None)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '')

    def test_max_validator(self):
        validator = MaxValidator(10)
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, -1))
        self.assertTrue(self._validator(validator, 10))
        self.assertTrue(self._validator(validator, 'test'))
        self.assertTrue(self._validator(validator, 't' * 10))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 11)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 't' * 11)

    def test_min_validator(self):
        validator = MinValidator(10)
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, 10))
        self.assertTrue(self._validator(validator, 20))
        self.assertTrue(self._validator(validator, 't' * 10))
        self.assertTrue(self._validator(validator, 't' * 20))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 5)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 'test')

    def test_between_validator(self):
        validator = BetweenValidator(5, 10)
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, 5))
        self.assertTrue(self._validator(validator, 8))
        self.assertTrue(self._validator(validator, 10))
        self.assertTrue(self._validator(validator, 't' * 5))
        self.assertTrue(self._validator(validator, 't' * 8))
        self.assertTrue(self._validator(validator, 't' * 10))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 0)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 20)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 'test')
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 't' * 20)

    def test_regex_validator(self):
        validator = RegexValidator('^\w+$')
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, 'abc'))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '')
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '#abc')

    def test_integer_validator(self):
        validator = IntegerValidator()
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, '1'))
        self.assertTrue(self._validator(validator, '-1'))
        self.assertTrue(self._validator(validator, 1))
        self.assertTrue(self._validator(validator, -1))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 'a')
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '1-1')

    def test_numeric_validator(self):
        validator = NumericValidator()
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, '1'))
        self.assertTrue(self._validator(validator, '-1'))
        self.assertTrue(self._validator(validator, 1))
        self.assertTrue(self._validator(validator, -1))
        self.assertTrue(self._validator(validator, '1.1'))
        self.assertTrue(self._validator(validator, '1.01e10'))
        self.assertTrue(self._validator(validator, '1e10'))
        self.assertTrue(self._validator(validator, '0.1e-5'))
        self.assertTrue(self._validator(validator, '.1e-5'))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '.')
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 'number')
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '4e4e4')

    def test_in_validator(self):
        validator = InValidator('1', '2', '3')
        self.assertTrue(self._validator(validator, None))
        self.assertTrue(self._validator(validator, 1))
        self.assertTrue(self._validator(validator, 2))
        self.assertTrue(self._validator(validator, 3))
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, 0)
        self.assertRaisesRegexp(ValidationError, 'test', self._validator, validator, '0')


class UsageTest(unittest.TestCase):
    def setUp(self):
        self.test = FakeRequest.test

    def test_usage1(self):
        @POST('name', validators='required')
        @POST('password', validators='required', validator_classes=[RegexValidator('^(password|pwd)$')])
        def view(request, name, password):
            self.assertEqual(name, 'name')
            self.assertEqual(password, 'password')

        self.test(view, post={'name': 'name', 'password': 'password'})
        with self.assertRaisesRegexp(ValidationError, 'name'):
            self.test(view, post={'password': 'password'})
        with self.assertRaisesRegexp(ValidationError, 'password'):
            self.test(view, post={'name': 'name'})
        with self.assertRaisesRegexp(ValidationError, 'password'):
            self.test(view, post={'name': 'name', 'password': 'password1'})

    def test_usage2(self):
        @GET('keyword', validators=None)
        @GET('offset', default=0, type='int', validators=None)
        @GET('limit', default=10, type='int', validators=None)
        def view(request, keyword, offset, limit):
            return keyword, offset, limit

        self.assertEqual(self.test(view, get={'keyword': 'q', 'offset': 10, 'limit': 10}), ('q', 10, 10))
        self.assertEqual(self.test(view, get={}), (None, 0, 10))

    def test_phone_validate(self):
        """
        Demo of SMS Validate View
        """

        class PhoneNumberValidator(BaseValidator):
            def is_valid(self, value, params):
                check_phone_type = params.get('check_phone_type')
                exist = value[0] != '0'
                if check_phone_type == 1 and exist:
                    self.message = 'already register or bind'
                    return False
                elif check_phone_type == 2 and not exist:
                    self.message = 'not register'
                    return False
                elif check_phone_type == 3 and exist:
                    self.message = 'already bind'
                    return False
                else:
                    return True

        ValidatorRegistry.register('phone_number_validator', PhoneNumberValidator)

        @GET('check_phone_type', type='int', validators='required | in: 1,2,3')
        @POST('phone', validators='required | regex: \d{11} | phone_number_validator')
        @POST('token', validators='required')
        def post(request, check_phone_type, phone, token):
            self.assertIsNotNone(check_phone_type)
            self.assertIsNotNone(phone)
            self.assertIsNotNone(token)

        self.test(post, get={'check_phone_type': 1}, post={'phone': '03888888888', 'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'phone'):
            self.test(post, get={'check_phone_type': 1}, post={'phone': '1', 'token': '1'})
        # Test for required
        with self.assertRaisesRegexp(ValidationError, 'check_phone_type.*required'):
            self.test(post, post={'phone': '13888888888', 'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'phone.*required'):
            self.test(post, get={'check_phone_type': 1}, post={'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'token.*required'):
            self.test(post, get={'check_phone_type': 1}, post={'phone': '13888888888'})
        # Test for other default validators
        with self.assertRaisesRegexp(ValidationError, 'phone'):
            self.test(post, get={'check_phone_type': 1}, post={'phone': '8888', 'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'check_phone_type'):
            self.test(post, get={'check_phone_type': 0}, post={'phone': '03888888888', 'token': '1'})
        # Test for custom validator
        with self.assertRaisesRegexp(ValidationError, 'already register or bind'):
            self.test(post, get={'check_phone_type': 1}, post={'phone': '13888888888', 'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'not register'):
            self.test(post, get={'check_phone_type': 2}, post={'phone': '03888888888', 'token': '1'})
        with self.assertRaisesRegexp(ValidationError, 'already bind'):
            self.test(post, get={'check_phone_type': 3}, post={'phone': '13888888888', 'token': '1'})


if __name__ == '__main__':
    unittest.main()
