# django-validator ![Travis-CI](https://travis-ci.org/romain-li/django-validator.svg)

A django-rest-framework tools for validate and extract param from request.
And also support normal django view functions.

## Install:

```bash
pip install django_validator
```

## Usage:

### Use default decorators and validators
```python
@GET('check_phone_type', type='int', validators='required | in: 1,2,3')
@POST('phone', validators='required | regex: \d{11}')
@POST('token', validators='required')
def post(request, check_phone_type, phone, token):
    pass
```

### Custom validator
```python
class PhoneNumberValidator(BaseValidator):
    def is_valid(self, value, params):
        return True

ValidatorRegistry.register('phone_number_validator', PhoneNumberValidator)
@POST('phone', validators='required | regex: \d{11} | phone_number_validator')

# or

@POST('phone', validators='required | regex: \d{11}', validator_classes=[PhoneNumberValidator()])
```


## Decorators
- GET
- POST
- POST_OR_GET
- HEADER
- URI

## Params for decorator
- name: The key of param in the request.
- related_name: The key of param to pass throw the function. Default is equals to name.
- verbose_name: The key for display in the validation error message. Default is equals to name.
- default: Default value for the param. Default is `None`.
- type: Auto check and convert the param type. Default is string.
- many: Convert the param to a list if set to `True`.
- separator: If set many to `True`, use this value to split the param.
- validators: String format validator, like `required | max: 1`.

## Default types
- str, string
- int, integer
- float
- bool, boolean

## Default validators
- required
- required_with
- required_without
- required_if
- max
- min
- between
- regex
- integer
- numeric
- in
- not_in

## Run tests
scripts/test.sh

## TODO List
- [ ] Be compatible with django framework, not django-rest-framework.
