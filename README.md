# django-validator

A django-rest-framework tools for validate and extract param from request.
And also support normal django view functions.

## Usage:

### Use default decorators and validators
```
@GET('check_phone_type', type='int', validators='required | in: 1,2,3')
@POST('phone', validators='required | regex: \d{11}')
@POST('token', validators='required')
def post(request, check_phone_type, phone, token):
    pass
```

### Custom validator
```
class PhoneNumberValidator(BaseValidator):
    def is_valid(self, value, params):
        return True

ValidatorRegistry.register('phone_number_validator', PhoneNumberValidator)
@POST('phone', validators='required | regex: \d{11} | phone_number_validator')

# or

@POST('phone', validators='required | regex: \d{11}', validator_classes=[PhoneNumberValidator()])
```

### TODO List

- [x] Base decorator
- [x] Default value
- [x] Type converter
- [x] Lookup param, and be compatible with older version of django-rest-framework
- [x] Many and separator param
- [x] Validators
- [x] Custom type converter
- [x] Custom validators
- [x] Custom validator messages
- [ ] Auto output API documents or function document
- [x] Tests
- [ ] Be compatible with django framework, not django-rest-framework.