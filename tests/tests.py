import unittest

from django.http import HttpRequest

from django_validator.decorators import GET, POST
from django_validator.validators import *


class FakeRequest(HttpRequest):
    def __init__(self, method='GET', get=None, post=None, header=None, drf_version=3):
        super(FakeRequest, self).__init__()
        if drf_version >= 3:
            self.query_params = self._param_to_string(get or {})
            self.data = self._param_to_string(post or {})
        else:
            self.GET = self._param_to_string(get or {})
            self.DATA = self._param_to_string(post or {})
        self.META = self._param_to_string(header or {})
        self.method = method

    @staticmethod
    def _param_to_string(params):
        """
        Convert all params to string, because in the request, all the params are string.
        """
        if params:
            params = params.copy()
            for key, value in params.items():
                params[key] = str(value)
        return params

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def test(cls, func, drf_version=3, **kwargs):
        """
        Create a fake request and perform the view function.
        """
        return func(cls.create(drf_version=drf_version, **kwargs))


class UsageTest(unittest.TestCase):
    def setUp(self):
        self.test = FakeRequest.test

    def test_usage1(self):
        @POST('name', validators='required', validator_classes=RegexValidator('name', message='custom message'))
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
        with self.assertRaisesRegexp(ValidationError, 'custom message'):
            self.test(view, post={'name': 'test', 'password': 'password'})

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
