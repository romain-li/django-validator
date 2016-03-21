from django.core.exceptions import ValidationError as DjangoValidationError

from . import status


class ValidationError(DjangoValidationError):
    """
    Validation Error
    """
    code = ''

    def __init__(self, detail, code=None, status_code=status.HTTP_400_BAD_REQUEST):
        super(ValidationError, self).__init__(detail)
        self.code = code
        self.status_code = status_code
