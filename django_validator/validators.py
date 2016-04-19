"""Module that provides the default validators and validator registry.

Inherit BaseValidator to implement the custom validators.
"""
import os
import re

from django.core.files.base import File
from django.utils.translation import ugettext_lazy as _

from . import status
from .exceptions import ValidationError


class ValidatorRegistry(object):
    """
    Registry for all validators.

    You can register and get validator classes from its class methods.
    """
    _registry = {}

    @classmethod
    def register(cls, name, _class):
        """Register Converter in ConverterRegistry.

        Args:
            name (str, iterable): Register key or name tuple.
            _class (BaseConverter): Validator class.
        """
        if hasattr(name, '__iter__'):
            for _name in name:
                cls._registry[_name] = _class
        else:
            cls._registry[name] = _class

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def get_validators(cls, validator_str):
        """Converter a validator string to a list of validator instances.

        Args:
            validator_str (str):

        Returns:
            List[BaseValidator]: A list of validator instances.

        Raises:
            TODO: Determine a special error.
        """
        validators = []
        if not validator_str:
            return validators

        rules = validator_str.split('|')
        for rule in rules:
            if ':' in rule:
                name, args = rule.split(':', 2)
                name = name.strip()
                args = map(lambda x: x.strip(), args.split(','))
            else:
                name = rule.strip()
                args = ()

            validator_class = cls.get(name)
            if validator_class:
                # Raise ValueError
                validators.append(validator_class(*args))
            else:
                raise Exception('Can not resolve validator class: %s.' % name)

        return validators


class BaseValidator(object):
    """
    Super class for all validators.

    You can overwrite these params and functions:

    code: error_code in the raised error.
    message: error_message in the raised error.
    nullable: when this param set to True, validator will skip when value is None.
    clean: class will call this function to clean value before validate it.
    is_valid: you must overwrite this function to implement your logic.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'base_validator'
    message = _('The {key} is invalid.')
    nullable = True

    def clean(self, value):
        return value

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, key, params, verbose_key=None):
        value = params.get(key)
        if value is None and self.nullable:
            return True
        if verbose_key is None:
            verbose_key = key

        cleaned = self.clean(value)
        message_params = {'show_value': cleaned, 'value': value, 'key': verbose_key}
        if not self.is_valid(cleaned, params):
            raise ValidationError(self.message.format(**message_params), self.code, self.status_code)
        return True

    def is_valid(self, value, params):
        raise NotImplementedError

    def set_message(self, message):
        """
        Set custom message with function.

        For example:
        @GET('xxx', validator_classes=xxxValidator().set_message('xxx'))
        """
        self.message = message
        return self


class RequiredValidator(BaseValidator):
    """
    Validate the value is required.
    """
    code = 'required_validator'
    message = _('The {key} is required.')
    nullable = False

    def is_valid(self, value, params):
        return RequiredValidator.required_valid(value)

    @staticmethod
    def required_valid(value):
        if value is None:
            return False
        elif isinstance(value, basestring) and value.strip() == '':
            return False
        return True


class RequiredWithValidator(BaseValidator):
    """
    Validate the value when other value is set.
    """
    code = 'required_with_validator'
    nullable = False

    def __init__(self, other, message=None):
        super(RequiredWithValidator, self).__init__(message)
        self.other = other
        self.message = _('The {{key}} is required with {other}'.format(other=other))

    def is_valid(self, value, params):
        if params.get(self.other) is not None:
            return RequiredValidator.required_valid(value)
        else:
            return True


class RequiredWithoutValidator(BaseValidator):
    """
    Validate the value when other value is not set.
    """
    code = 'required_without_validator'
    nullable = False

    def __init__(self, other, message=None):
        super(RequiredWithoutValidator, self).__init__(message)
        self.other = other
        self.message = _('The {{key}} is required without {other}'.format(other=other))

    def is_valid(self, value, params):
        if params.get(self.other) is None:
            return RequiredValidator.required_valid(value)
        else:
            return True


class RequiredIfValidator(BaseValidator):
    """
    Validate the value if other value is equals to your expectation.
    """
    code = 'required_if_validator'
    nullable = False

    def __init__(self, other, other_value, message=None):
        super(RequiredIfValidator, self).__init__(message)
        self.other = other
        self.other_value = other_value
        self.message = _(
            'The {{key}} is required when {other} is {other_value}'.format(other=other, other_value=other_value)
        )

    def is_valid(self, value, params):
        other_value = params.get(self.other)
        if other_value is not None and str(other_value) == self.other_value:
            return RequiredValidator.required_valid(value)
        else:
            return True


class MinValidator(BaseValidator):
    """
    Mix min value and min length validators.
    """
    code = 'min_validator'

    def __init__(self, min_value):
        super(MinValidator, self).__init__()
        self.min_value = int(min_value)

    def is_valid(self, value, params):
        if isinstance(value, basestring):
            self.message = _('The {{key}} must be at least {min} characters.').format(min=self.min_value)
            return len(value) >= self.min_value
        elif isinstance(value, File):
            self.message = _('The {{key}} must be at least {min} bytes.'.format(min=self.min_value))
            return value.size >= self.min_value
        else:
            self.message = _('The {{key}} must be at least {min}.').format(min=self.min_value)
            return value >= self.min_value


class MaxValidator(BaseValidator):
    """
    Mix max value and max length validators.
    """
    code = 'max_validator'

    def __init__(self, max_value):
        super(MaxValidator, self).__init__()
        self.max_value = int(max_value)

    def is_valid(self, value, params):
        if isinstance(value, basestring):
            self.message = _('The {{key}} may not be greater than {max} characters.').format(max=self.max_value)
            return len(value) <= self.max_value
        elif isinstance(value, File):
            self.message = _('The {{key}} must not be at greater {max} bytes.'.format(max=self.max_value))
            return value.size <= self.max_value
        else:
            self.message = _('The {{key}} may not be greater than {max}.').format(max=self.max_value)
            return value <= self.max_value


class BetweenValidator(BaseValidator):
    """
    Mix min and max validators.
    """
    code = 'between_validator'

    def __init__(self, min_value, max_value):
        super(BetweenValidator, self).__init__()
        self.min_value = int(min_value)
        self.max_value = int(max_value)

    def is_valid(self, value, params):
        if isinstance(value, basestring):
            self.message = _('The {{key}} must be between {min} and {max} characters.').format(
                min=self.min_value,
                max=self.max_value
            )
            return self.min_value <= len(value) <= self.max_value
        elif isinstance(value, File):
            self.message = _('The {{key}} must be between {min} and {max} bytes.').format(
                min=self.min_value,
                max=self.max_value
            )
            return self.min_value <= value.size <= self.max_value
        else:
            self.message = _('The {{key}} must be between {min} and {max}.').format(
                min=self.min_value,
                max=self.max_value
            )
            return self.min_value <= value <= self.max_value


class BaseRegexValidator(BaseValidator):
    """
    Base class for regex validators.
    """
    code = 'regex_validator'
    message = _('The {key} format is invalid.')
    regex = None

    def clean(self, value):
        if value is None:
            return ''
        return str(value)

    def is_valid(self, value, params):
        return self.regex.match(value)


class RegexValidator(BaseRegexValidator):
    """
    Custom regex validator.
    """

    def __init__(self, regex, message=None):
        super(RegexValidator, self).__init__(message)
        self.regex = re.compile(regex)


class IntegerValidator(BaseRegexValidator):
    """
    Inherit regex validator to confirm integers.
    """
    code = 'integer_validator'
    message = _('The {key} must be an integer.')
    regex = re.compile('^-?\d+\Z')

    def __init__(self, message=None):
        super(IntegerValidator, self).__init__(message)


class NumericValidator(BaseRegexValidator):
    """
    Inherit regex validator to confirm numbers.
    """
    code = 'numeric_validator'
    message = _('The {key} must be a number.')
    regex = re.compile('^-?\d*(\.\d+)?(e-?\d+)?\Z')

    def __init__(self, message=None):
        super(NumericValidator, self).__init__(message)


class InValidator(BaseValidator):
    """
    Check if the value is in the choices list.
    """
    code = 'in_validator'
    message = _('The selected {key} is invalid.')

    def __init__(self, *choices):
        super(InValidator, self).__init__()
        self.choices = {choice.lower() for choice in choices}

    def clean(self, value):
        if value is None:
            return ''
        return str(value).lower()

    def is_valid(self, value, params):
        return value in self.choices


class NotInValidator(InValidator):
    """
    Check if the value is not in the choices list.
    """
    code = 'not_in_validator'

    def is_valid(self, value, params):
        return value not in self.choices


class ExtInValidator(BaseValidator):
    """
    Check if the file extension type is in the choices list.
    """
    code = 'ext_in_validator'
    message = _('The extension type of {key} is invalid.')

    def __init__(self, *choices):
        super(ExtInValidator, self).__init__()
        choices = [choice.lower() for choice in choices]
        self.choices = {choice if choice.startswith('.') else '.' + choice for choice in choices}

    def clean(self, value):
        _, ext = os.path.splitext(value.name)
        return ext.lower()

    def is_valid(self, value, params):
        return value in self.choices


class ExtNotInValidator(ExtInValidator):
    """
    Check if the file extension type is not in the choices list.
    """
    code = 'ext_not_in_validator'

    def is_valid(self, value, params):
        return value not in self.choices


# Register all validators
ValidatorRegistry.register('required', RequiredValidator)
ValidatorRegistry.register('required_with', RequiredWithValidator)
ValidatorRegistry.register('required_without', RequiredWithoutValidator)
ValidatorRegistry.register('required_if', RequiredIfValidator)
ValidatorRegistry.register('max', MaxValidator)
ValidatorRegistry.register('min', MinValidator)
ValidatorRegistry.register('between', BetweenValidator)
ValidatorRegistry.register('regex', RegexValidator)
ValidatorRegistry.register('integer', IntegerValidator)
ValidatorRegistry.register('numeric', NumericValidator)
ValidatorRegistry.register('in', InValidator)
ValidatorRegistry.register('not_in', NotInValidator)
ValidatorRegistry.register('ext_in', ExtInValidator)
ValidatorRegistry.register('ext_not_in', ExtNotInValidator)
