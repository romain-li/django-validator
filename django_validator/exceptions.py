import rest_framework.exceptions


class ValidationError(rest_framework.exceptions.ValidationError):
    code = ''

    def __init__(self, detail, code=None):
        super(ValidationError, self).__init__(detail)
        self.code = code
