from django_validator.validators import IntegerValidator, NumericValidator


class ConverterRegistry(object):
    """
    Registry for all converters.
    """
    _registry = {}

    @classmethod
    def register(cls, name, _class):
        """
        Register Converter in ConverterRegistry.
        :param name: Register key or name tuple.
        :param _class: Converter class.
        """
        if isinstance(name, str):
            cls._registry[name] = _class
        else:
            for _name in name:
                cls._registry[_name] = _class

    @classmethod
    def get(cls, name):
        return cls._registry.get(name, StringConverter)


class ConverterMetaClass(type):
    """
    Metaclass for all Converters.
    """

    def __new__(cls, name, bases, attributes):
        _class = super(ConverterMetaClass, cls).__new__(cls, name, bases, attributes)
        attr_meta = attributes.pop('Meta', None)
        abstract = getattr(attr_meta, 'abstract', False)
        if not abstract:
            _class.register()

        return _class


class BaseConverter(object):
    """
    Abstract super class for all converters.
    """
    __metaclass__ = ConverterMetaClass

    @staticmethod
    def convert(key, string):
        raise NotImplementedError

    @classmethod
    def register(cls, name=None):
        if name is None:
            attr_meta = getattr(cls, 'Meta', None)
            name = getattr(attr_meta, 'name', cls.__name__)
        ConverterRegistry.register(name, cls)

    class Meta:
        abstract = True


class StringConverter(BaseConverter):
    @staticmethod
    def convert(key, string):
        return string

    class Meta:
        name = ('string', 'str')


class IntegerConverter(BaseConverter):
    integer_validator = IntegerValidator()

    @staticmethod
    def convert(key, string):
        if string is None:
            return None
        IntegerConverter.integer_validator(key, {key: string})
        return int(string)

    class Meta:
        name = ('integer', 'int')


class FloatConverter(BaseConverter):
    numeric_validator = NumericValidator()

    @staticmethod
    def convert(key, string):
        if string is None:
            return None
        FloatConverter.numeric_validator(key, {key: string})
        return float(string)

    class Meta:
        name = 'float'


class BooleanConverter(BaseConverter):
    """
    Convert the value to a boolean value.
    """

    # Set is the faster than tuple and list, but False is equals 0 in set structure.
    false_values = {None, False, 'false', 'False', 0, '0'}

    @staticmethod
    def convert(key, string):
        return string not in BooleanConverter.false_values

    class Meta:
        name = ('boolean', 'bool')
