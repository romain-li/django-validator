from rest_framework import status
import rest_framework.exceptions


class ValidationError(rest_framework.exceptions.APIException):
    code = ''

    def __init__(self, detail, code=None, status_code=status.HTTP_400_BAD_REQUEST):
        super(ValidationError, self).__init__(detail)
        self.code = code
        self.status_code = status_code
