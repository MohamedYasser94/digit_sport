from typing import Any, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

def core_exception_handler(exc: Exception, context: dict[str, Any]) -> Optional[Response]:
    """Error handler for the API."""
    response = exception_handler(exc, context)
    handlers = {'ValidationError': _handle_generic_error}

    exception_class = exc.__class__.__name__

    if exception_class in handlers:

        return handlers[exception_class](exc, context, response)

    return response


def _handle_generic_error(exc: Exception, context: dict[str, Any], response: Optional[Response]) -> Optional[Response]:
    if response:
        response.data = {'errors': response.data}

        return response
    return None


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Bad request error')


class InternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('Internal server error')


class TokenDecodeError(Exception):
    pass




class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the people.
    """
    def __init__(self, code, message):
        super().__init__(code)
        self.code = code
        if message:
        	self.message = message