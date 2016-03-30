import ddt
from django.test import TestCase

from django_validator.validators import *


@ddt.ddt
class ValidatorTest(TestCase):
    """
    Test cases for validators.
    """

    @staticmethod
    def _validator(validator, value, other=None, verbose_key=None):
        return validator('test', {'test': value, 'other': other}, verbose_key)

    @ddt.data(
        ('required', RequiredValidator),
        ('required_with', RequiredWithValidator),
        ('required_without', RequiredWithoutValidator),
        ('required_if', RequiredIfValidator),
        ('max', MaxValidator),
        ('min', MinValidator),
        ('between', BetweenValidator),
        ('regex', RegexValidator),
        ('integer', IntegerValidator),
        ('numeric', NumericValidator),
        ('in', InValidator),
        ('not_in', NotInValidator),
    )
    @ddt.unpack
    def test_registry(self, name, excepted_validator):
        # Test the default validator registry
        validator = ValidatorRegistry.get(name)
        self.assertEqual(validator, excepted_validator)

    @ddt.data(
        # Required
        (RequiredValidator(), True, 'test'),
        (RequiredValidator(), False, None),
        (RequiredValidator(), False, ''),
        # Required with
        (RequiredWithValidator('other'), True, 'test'),
        (RequiredWithValidator('other'), True, 'test', 'test'),
        (RequiredWithValidator('other'), True, None),
        (RequiredWithValidator('other'), True, ''),
        (RequiredWithValidator('other'), False, None, 'test'),
        (RequiredWithValidator('other'), False, '', 'test'),
        # Required without
        (RequiredWithoutValidator('other'), True, 'test'),
        (RequiredWithoutValidator('other'), True, 'test', 'test'),
        (RequiredWithoutValidator('other'), True, None, 'test'),
        (RequiredWithoutValidator('other'), True, '', 'test'),
        (RequiredWithoutValidator('other'), False, None),
        (RequiredWithoutValidator('other'), False, ''),
        # Required if
        (RequiredIfValidator('other', 'test'), True, 'test'),
        (RequiredIfValidator('other', 'test'), True, 'test', 'test'),
        (RequiredIfValidator('other', 'test'), True, 'test', 'other'),
        (RequiredIfValidator('other', 'test'), True, None),
        (RequiredIfValidator('other', 'test'), True, None, 'other'),
        (RequiredIfValidator('other', 'test'), True, ''),
        (RequiredIfValidator('other', 'test'), True, '', 'other'),
        (RequiredIfValidator('other', 'test'), False, None, 'test'),
        (RequiredIfValidator('other', 'test'), False, '', 'test'),
        # Max
        (MaxValidator(10), True, None),
        (MaxValidator(10), True, -1),
        (MaxValidator(10), True, 10),
        (MaxValidator(10), True, 'test'),
        (MaxValidator(10), True, 't' * 10),
        (MaxValidator(10), False, 11),
        (MaxValidator(10), False, 't' * 11),
        # Min
        (MinValidator(10), True, None),
        (MinValidator(10), True, 10),
        (MinValidator(10), True, 20),
        (MinValidator(10), True, 't' * 10),
        (MinValidator(10), True, 't' * 20),
        (MinValidator(10), True, 't' * 20),
        (MinValidator(10), False, 5),
        (MinValidator(10), False, 'test'),
        # Between
        (BetweenValidator(5, 10), True, None),
        (BetweenValidator(5, 10), True, 5),
        (BetweenValidator(5, 10), True, 8),
        (BetweenValidator(5, 10), True, 10),
        (BetweenValidator(5, 10), True, 't' * 5),
        (BetweenValidator(5, 10), True, 't' * 8),
        (BetweenValidator(5, 10), True, 't' * 10),
        (BetweenValidator(5, 10), False, 0),
        (BetweenValidator(5, 10), False, 20),
        (BetweenValidator(5, 10), False, 'test'),
        (BetweenValidator(5, 10), False, 't' * 20),
        # Regex
        (RegexValidator('^\w+$'), True, None),
        (RegexValidator('^\w+$'), True, 'abc'),
        (RegexValidator('^\w+$'), False, ''),
        (RegexValidator('^\w+$'), False, '#abc'),
        # Integer
        (IntegerValidator(), True, None),
        (IntegerValidator(), True, '1'),
        (IntegerValidator(), True, '-1'),
        (IntegerValidator(), True, 1),
        (IntegerValidator(), True, -1),
        (IntegerValidator(), False, 'a'),
        (IntegerValidator(), False, '1-1'),
        # Numeric
        (NumericValidator(), True, None),
        (NumericValidator(), True, '1'),
        (NumericValidator(), True, '-1'),
        (NumericValidator(), True, 1),
        (NumericValidator(), True, -1),
        (NumericValidator(), True, '1.1'),
        (NumericValidator(), True, '1.01e10'),
        (NumericValidator(), True, '1e10'),
        (NumericValidator(), True, '0.1e-5'),
        (NumericValidator(), True, '.1e-5'),
        (NumericValidator(), False, '.'),
        (NumericValidator(), False, 'number'),
        (NumericValidator(), False, '4e4e4'),
        # In
        (InValidator('1', '2', '3'), True, None),
        (InValidator('1', '2', '3'), True, 1),
        (InValidator('1', '2', '3'), True, '1'),
        (InValidator('1', '2', '3'), True, 2),
        (InValidator('1', '2', '3'), True, 3),
        (InValidator('1', '2', '3'), False, 0),
        (InValidator('1', '2', '3'), False, '0'),
        # Not in
        (NotInValidator('1', '2', '3'), True, None),
        (NotInValidator('1', '2', '3'), True, 0),
        (NotInValidator('1', '2', '3'), True, '0'),
        (NotInValidator('1', '2', '3'), False, 1),
        (NotInValidator('1', '2', '3'), False, '1'),
        (NotInValidator('1', '2', '3'), False, 2),
        (NotInValidator('1', '2', '3'), False, 3),
    )
    @ddt.unpack
    def test_validator(self, validator, valid, value, other=None):
        if valid:
            self.assertTrue(self._validator(validator, value, other))
        else:
            self.assertRaises(ValidationError, self._validator, validator, value, other)

    def test_verbose_key(self):
        """ Test if the verbose key can throw from the validation error. """
        validator = RequiredValidator()
        self.assertRaisesRegexp(ValidationError, 'TEST_VERBOSE_KEY', self._validator, validator,
                                None, verbose_key='TEST_VERBOSE_KEY')
