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

## types
- str, string
- int, integer
- float
- bool, boolean

## validators
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
