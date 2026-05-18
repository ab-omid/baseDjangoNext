from rest_framework.exceptions import Throttled, AuthenticationFailed, NotAuthenticated
from rest_framework.views import exception_handler

from app.actions.action import Action


def app_exceptions_exception_handler(exc, context):
    """
    Custom exception handler for the app_exceptions application. This function intercepts exceptions raised during the
    processing of requests and returns customized responses based on the type of exception.

    Parameters:
    exc (Exception): The exception that occurred during request processing.
    context (dict): A dictionary containing information about the request and view.

    Returns:
    response (Response): A Django REST framework response object with customized error details.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # If the exception is a Throttled exception, customize the response.
    if isinstance(exc, Throttled):
        return Action().throttled(exc.detail.split()[-2]).json_response()
    if isinstance(exc, NotAuthenticated):
        return Action().unauthorized(["Invalid or expired token"]).json_response()
    if isinstance(exc, AuthenticationFailed):
        return Action().unauthorized(["Invalid Credentials"]).json_response()

    return response
