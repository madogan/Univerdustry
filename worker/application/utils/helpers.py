# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import datetime
from string import ascii_lowercase, digits

from flask import (_app_ctx_stack, current_app, has_app_context)


def ensure_app_context(function):
    """Decorator function to make sure a function works in app context.

    Args:
        function: A function that will be wrapped with context.
    """
    def wrapper(*args, **kwargs):
        """Decorate function here.

        Args:
            *args: Arguments of the function.
            **kwargs: Keyword arguments of the function.

        Returns:
            :obj:`function`: Wrapped function.
        """
        is_pushed = push_app_context_if_has_not_app_context()
        return_value = function(*args, **kwargs)
        pop_app_context_if_pushed(is_pushed)

        return return_value

    # To avoid naming conflicts.
    wrapper.__name__ = function.__name__
    return wrapper


def push_app_context_if_has_not_app_context() -> [bool, None]:
    """Check app context and push an app context manually."""
    if not has_app_context():
        # If out of app context, push app context.
        from scholar_rest import app
        ctx = app.app_context()
        ctx.push()
        return True


def pop_app_context_if_pushed(is_pushed: bool) -> None:
    """Pop app context if pushed
    
    Arguments:
        is_pushed: If it is True, pop app context from stack.
    """
    if is_pushed is True:
        from scholar_rest import app
        ctx = app.app_context()
        if ctx == _app_ctx_stack.top:
            ctx.pop()


@ensure_app_context
def get_time_limit():
    now = datetime.datetime.now()
    time_limit = now - datetime.timedelta(
        days=current_app.config["DB_HISTORY_DAYS_LIMIT"]
    )
    return time_limit


def extract_file_name_from_url(url):
    file_name = url.split("/")[-1].split(".")[0].lower().replace(" ", "")
    accepted_chars = ascii_lowercase + digits + "_"
    file_name = "".join([c for c in file_name if c in accepted_chars])
    return file_name