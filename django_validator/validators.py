# TODO: Add django translate feature
import re

from django.utils.translation import ugettext_lazy as _
from django_validator.exceptions import ValidationError


class ValidatorRegistry(object):
    """
    Registry for all validators.
    """
    _registry = {}

    @classmethod
    def register(cls, name, _class):
        """
        Register Validator in ValidatorRegistry.
        :param name: Register key or name tuple.
        :param _class: Validator class.
        """
        if isinstance(name, str):
            cls._registry[name] = _class
        else:
            for _name in name:
                cls._registry[_name] = _class

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def get_validators(cls, validator_str):
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
    message = _('The {key} field is invalid.')
    # When this param set to True, validator will skip when value is None.
    nullable = True
    clean = lambda self, x: x

    def __call__(self, key, params):
        value = params.get(key)
        if value is None and self.nullable:
            return True
        cleaned = self.clean(value)
        message_params = {'show_value': cleaned, 'value': value, 'key': key}
        if not self.is_valid(cleaned, params):
            raise ValidationError(self.message.format(**message_params))
        return True

    def is_valid(self, value, params):
        raise NotImplementedError


class RequiredValidator(BaseValidator):
    message = _('The {key} field is required.')
    nullable = False

    def is_valid(self, value, params):
        if value is None:
            return False
        elif isinstance(value, str) and value.strip() == '':
            return False
        return True


class MinValidator(BaseValidator):
    """
    Mix min value and min length validators.
    """

    def __init__(self, min_value):
        self.min_value = int(min_value)

    def is_valid(self, value, params):
        if isinstance(value, str):
            self.message = _('The {{key}} must be at least {min} characters.').format(min=self.min_value)
            return len(value) >= self.min_value
        else:
            self.message = _('The {{key}} must be at least {min}.').format(min=self.min_value)
            return value >= self.min_value


class MaxValidator(BaseValidator):
    """
    Mix max value and max length validators.
    """

    def __init__(self, max_value):
        self.max_value = int(max_value)

    def is_valid(self, value, params):
        if isinstance(value, str):
            self.message = _('The {{key}} may not be greater than {max} characters.').format(max=self.max_value)
            return len(value) <= self.max_value
        else:
            self.message = _('The {{key}} may not be greater than {max}.').format(max=self.max_value)
            return value <= self.max_value


class BetweenValidator(BaseValidator):
    """
    Mix min and max validators.
    """

    def __init__(self, min_value, max_value):
        self.min_value = int(min_value)
        self.max_value = int(max_value)

    def is_valid(self, value, params):
        if isinstance(value, str):
            self.message = _('The {{key}} must be between {min} and {max} characters.').format(min=self.min_value,
                                                                                               max=self.max_value)
            return self.min_value <= len(value) <= self.max_value
        else:
            self.message = _('The {{key}} must be between {min} and {max}.').format(min=self.min_value,
                                                                                    max=self.max_value)
            return self.min_value <= value <= self.max_value


class BaseRegexValidator(BaseValidator):
    """
    Base class for regex validators.
    """
    regex = None

    @staticmethod
    def clean(value):
        if value is None:
            return ''
        return str(value)

    def is_valid(self, value, params):
        return self.regex.match(value)


class RegexValidator(BaseRegexValidator):
    """
    Custom regex validator.
    """
    message = _('The {key} format is invalid.')

    def __init__(self, regex):
        self.regex = re.compile(regex)


class IntegerValidator(BaseRegexValidator):
    """
    Inherit regex validator to confirm integers.
    """
    message = _('The {key} must be an integer.')
    regex = re.compile('^-?\d+\Z')


class NumericValidator(BaseRegexValidator):
    """
    Inherit regex validator to confirm numbers.
    """
    message = _('The {key} must be a number.')
    regex = re.compile('^-?\d*(\.\d+)?(e-?\d+)?\Z')


class InValidator(BaseValidator):
    """
    Check if the value is in the choices list.
    """
    message = _('The selected {key} is invalid.')

    def __init__(self, *choices):
        self.choices = choices

    @staticmethod
    def clean(value):
        if value is None:
            return ''
        return str(value)

    def is_valid(self, value, params):
        return value in self.choices


# Register all validators
ValidatorRegistry.register('required', RequiredValidator)
ValidatorRegistry.register('max', MaxValidator)
ValidatorRegistry.register('min', MinValidator)
ValidatorRegistry.register('between', BetweenValidator)
ValidatorRegistry.register('regex', RegexValidator)
ValidatorRegistry.register('integer', IntegerValidator)
ValidatorRegistry.register('numeric', NumericValidator)
ValidatorRegistry.register('in', InValidator)
