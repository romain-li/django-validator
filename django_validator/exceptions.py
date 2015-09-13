from rest_framework import status
import rest_framework.exceptions


class ValidationError(rest_framework.exceptions.ValidationError):
    code = ''

    def __init__(self, detail, code=None, status_code=status.HTTP_400_BAD_REQUEST):
        super(ValidationError, self).__init__(detail)
        self.status_code = status_code
        self.code = code
