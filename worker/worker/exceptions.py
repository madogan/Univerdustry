# -*- coding: utf-8 -*-
"""Exceptions and catcher script.

This module contains exception classes and generic catcher decorator.
"""

from flask import Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response as WerkzeugResponse
from sqlalchemy.exc import DBAPIError, DatabaseError, IntegrityError

from worker import db, logger
from worker.utils.helpers import json_response


class DefaultException(Exception):
    """Default exception class."""

    def __init__(self, message_index=None):
        self.message_index = message_index or "default_error"

    @property
    def _str(self):
        return self.message_index

    def __str__(self):
        return self._str


class OperationFailure(DefaultException):
    def __init__(self, operation_name, operation_status, message_index):
        super(OperationFailure, self).__init__(message_index=message_index)
        self.operation_name = operation_name
        self.operation_status = operation_status
        self.status_code = 404


class NoRecord(DefaultException):
    def __init__(self, message_index=None):
        super(NoRecord, self).__init__(message_index=message_index)
        self.message_index = message_index or "no_record"
        self.status_code = 404


class MaxDeviceLimit(DefaultException):
    def __init__(self, message_index=None):
        super(MaxDeviceLimit, self).__init__(message_index=message_index)
        self.message_index = message_index or "max_device_limit"
        self.status_code = 403


class RequiredError(DefaultException):
    def __init__(self, message_index=None):
        super(RequiredError, self).__init__(message_index=message_index)
        self.message_index = message_index or "required_field_error"
        self.status_code = 400


class UnexpectedFieldError(DefaultException):
    def __init__(self, message_index=None):
        super(UnexpectedFieldError, self).__init__(message_index=message_index)
        self.message_index = message_index or "unexpected_field_error"
        self.status_code = 400


class LicenseServerError(DefaultException):
    def __init__(self, message_index=None):
        super(LicenseServerError, self).__init__(message_index=message_index)
        self.message_index = message_index or "license_server_error"
        self.status_code = 404


class UserNotFoundError(DefaultException):
    def __init__(self, message_index=None):
        super(UserNotFoundError, self).__init__(message_index=message_index)
        self.message_index = message_index or "user_not_found_error"
        self.status_code = 404


class LicenseKeyMismatchError(DefaultException):
    def __init__(self, message_index=None):
        super(LicenseKeyMismatchError, self) \
            .__init__(message_index=message_index)
        self.message_index = message_index or "license_key_mismatch_error"
        self.status_code = 404


class UnexpectedError(DefaultException):
    def __init__(self, message_index=None):
        super(UnexpectedError, self).__init__(message_index=message_index)
        self.message_index = message_index or "unexpected_error"
        self.status_code = 500


class InvalidRoleException(DefaultException):
    def __init__(self, message_index=None):
        super(InvalidRoleException, self).__init__(message_index=message_index)
        self.message_index = message_index or "invalid_role"
        self.status_code = 401


class RestoreFailed(DefaultException):
    def __init__(self, message_index=None, error=None):
        super(RestoreFailed, self).__init__(message_index=message_index)
        self.message_index = message_index or "restore_failure"
        if error:
            self.message_index += f"_{error}"


class NotFound(DefaultException):
    def __init__(self, message_index=None, resource_name=None):
        super(NotFound, self).__init__(message_index=message_index)
        self.status_code = 404
        self.message_index = message_index or "not_found"
        if resource_name:
            self.message_index = f"{resource_name}_" + self.message_index


def catcher(**dec_kwargs):
    """Decorator function for catching exceptions.

    This decorator function gets a function and put it into a try-catch
    and handles responses.

    Args:
        **dec_kwargs: Decorator Keyword arguments of decorator function.
            - is_jsonified (bool): If it is True, returns response
                                   by using :flask:`jsonify` function.
    """

    def decorator(function):
        """Inner decorator function.

        Args:
            function: The function will be decorated.

        Returns:
            Decorated function.
        """

        def wrapper(*args, **kwargs):
            """Function wrapper.

            Args:
                *args: Arguments of wrapped function.
                **kwargs: Keyword arguments of wrapped function.
            """

            error = None
            response = None
            is_jsonified = dec_kwargs.get("is_jsonified", False)

            try:
                # Run function.
                response = function(*args, **kwargs)

                # Determine response type.
                if response is None:
                    response_type = "none"
                elif isinstance(response, tuple) and len(response) >= 2:
                    response_type = "tuple"
                elif isinstance(response, dict):
                    response_type = "dict"
                elif isinstance(response, (FlaskResponse, WerkzeugResponse)):
                    response_type = "object"
                else:
                    response_type = "data"
            except HTTPException as e:
                error = e
                response_type = "error_http"
                logger.error(f'HTTP Error: {str(e)}')
            except IntegrityError as e:
                error = str(e)
                response_type = "error"
                db.session.rollback()
                logger.exception(f'Integrity Error: {str(e)}')
            except (DatabaseError, DBAPIError) as e:
                logger.debug(f'e.__class__: {e.__class__}')
                error = str(e)
                response_type = "error"
                db.session.rollback()
                logger.exception(f'Database Error: {str(e)}')
            except DefaultException as e:
                error = e
                response_type = "default_error"
                logger.exception(f'Default Error: {str(e)}')
            except Exception as e:
                logger.debug(f'e.__class__: {e.__class__}')

                error = str(e)
                response_type = "error"
                logger.exception(f'Unexpected Error: {str(e)}')

            if dec_kwargs.get("timeline", False) is True:
                from worker.database.models import Timeline

                operation_status = "ok"
                if response_type == "error":
                    operation_status = "failure"

                operation_name = dec_kwargs.get("operation_name", None)
                timeline_data = dec_kwargs.get("timeline_data", None)
                message_index = operation_name + "_" + operation_status

                Timeline.add(operation_name=operation_name,
                             operation_status=operation_status,
                             message_index=message_index,
                             format_data=timeline_data)

            if response_type == "none":
                null_data = dec_kwargs.get("null_data", None)

                if null_data is None:
                    return json_response(is_jsonified=is_jsonified)
                else:
                    return json_response(data=null_data,
                                         is_jsonified=is_jsonified)

            if response_type == "data":
                return json_response(data=response, is_jsonified=is_jsonified)

            if response_type == "object":
                return response

            if response_type == "tuple":
                response_body, status_code = response[0], response[1]

                if not isinstance(response_body, dict) and not response_body:
                    response_body = dict(response_body)

                return json_response(**response_body,
                                     status_code=status_code,
                                     is_jsonified=is_jsonified)

            if response_type == "dict":
                return json_response(**response, is_jsonified=is_jsonified)

            if response_type == "error":
                if "UniqueViolation" in error:
                    message_index = "error_duplicate"
                elif "ForeignKeyViolation" in error:
                    message_index = "error_foreign_key_violation"
                else:
                    message_index = "error_database"

                return json_response(status="error",
                                     message_index=message_index,
                                     status_code=500,
                                     is_jsonified=is_jsonified)

            if response_type == "default_error":
                return json_response(status="error",
                                     message_index=error.message_index,
                                     status_code=error.status_code,
                                     is_jsonified=is_jsonified)

            if response_type == "error_http":
                return json_response(status="error",
                                     message_index=error.description,
                                     status_code=error.code)

        # NOTE: Flask needs unique function names for request
        # handler functions. When we wrap a function it names become wrapper
        # that is above function. So we change wrapper function name
        # by given function name in order to solve this problem.
        wrapper.__name__ = function.__name__
        return wrapper

    return decorator
