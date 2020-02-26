# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import os
import socket
import zipfile
import datetime

from flask_login import current_user
from paramiko import AuthenticationException, SSHClient
from worker.utils.translation_table import translator
from flask import (_app_ctx_stack, current_app, has_app_context, jsonify,
                   request)


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
        from worker import app
        ctx = app.app_context()
        ctx.push()
        return True


def pop_app_context_if_pushed(is_pushed: bool) -> None:
    """Pop app context if pushed
    
    Arguments:
        is_pushed: If it is True, pop app context from stack.
    """
    if is_pushed is True:
        from worker import app
        ctx = app.app_context()
        if ctx == _app_ctx_stack.top:
            ctx.pop()


def retrieve_file_paths(dir_path: str) -> list:
    """Return all file paths of the particular directory.

    Args:
        dir_path: Path of directory.

    Returns:
        :obj:`list`: List of file paths in the directory.
    """
    file_paths = list()

    # Read all directory, subdirectories and file lists.
    for root, directories, files in os.walk(dir_path):
        for filename in files:
            # Create the full filepath by using os module.
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)

    return file_paths


def zipfy(dir_path: str) -> None:
    """Zip a directory.

    Args:
        dir_path: Path of directory.
    """
    if os.path.isdir(dir_path):
        file_paths = retrieve_file_paths(dir_path)

        zip_file = zipfile.ZipFile(dir_path + '.zip', 'w',
                                   zipfile.ZIP_DEFLATED)

        with zip_file:
            for file in file_paths:
                zip_file.write(file, arcname=file.split(os.sep)[-1])
    else:
        timestamp = datetime_to_str(datetime.datetime.now(), file_fmt=True)
        with zipfile.ZipFile(dir_path + f"_{timestamp}.zip", 'w') as zip_file:
            zip_file.write(dir_path)


def is_port_open(ip: str, port: int, timeout: int = 5) -> bool:
    """Check an address is open or not.

    Args:
        ip: Ip address.
        port: Port of address.
        timeout: Connection wait time.

    Returns:
        :obj:`bool`: True if given ip and port is open, otherwise False.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)

    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        result = True
    except socket.error:
        result = False
    finally:
        s.close()

    return result


def is_ssh_port(ip: str, port: int) -> bool:
    """Check port of an ip is ssh port.

    Args:
        ip: Ip address.
        port: Port of address.

    Returns:
        :obj:`bool`: True if port is ssh port, otherwise False.
    """
    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.connect(hostname=ip, port=port, username="x", password="x")
        _, _, _ = client.exec_command('ls -l')
        client.close()
    except AuthenticationException:
        return True
    except Exception as e:
        if 'not found in known_hosts' in str(e):
            return True
        return False
    return True


@ensure_app_context
def datetime_to_str(dt: datetime.datetime, file_fmt: bool = False) -> str:
    """Convert :datetime:`datetime` object to string according
       to system datetime format.

    Args:
        dt: Input datetime object.
        file_fmt: True,

    Returns:

    """
    if not file_fmt:
        fm = current_app.config["DATETIME_FORMAT"]
    else:
        fm = "_%Y%m%d_%H%M%S"

    return dt.strftime(fm)


def get_client_ip() -> str:
    """Get requested Ip.

    It looks header if request is come from nginx or
    use :flask:`request`.`remote_addr` method.

    Returns:
        :obj:`str`: Ip address as string.
    """
    return request.environ.get("HTTP_X_REAL_IP", request.remote_addr)


def get_host_ip_via_socket():
    try:
        host = socket.gethostbyname(socket.gethostname())
    except Exception:
        host = None

    return host


@ensure_app_context
def get_host_ip() -> str:
    """Get requested Ip.

    Get current host ip address.

    Returns:
        :obj:`str`: Ip address as string.
    """
    try:
        host = request.host
    except Exception:
        host = None

    if host is None:
        host = current_app.config.get("host", None)

    if not host:
        host = get_host_ip_via_socket()

    return host





def set_host_ip():
    try:
        host = request.host
    except Exception:
        host = None

    current_app.config["host"] = host


def del_keys(o: dict, keys: list) -> None:
    """Get a dictionary and delete if given keys are exist.

    Args:
        o: A dictionary
        keys: Keys to delete.
    """
    for key in keys:
        if key in o.keys():
            del o[key]


@ensure_app_context
def get_time_limit():
    now = datetime.datetime.now()
    time_limit = now - datetime.timedelta(
        days=current_app.config["DB_HISTORY_DAYS_LIMIT"]
    )
    return time_limit


def is_connection_available() -> bool:
    """Check connectivity of the current system.

    It actually pings to google.

    Returns:
        :obj:`bool`: True if ping is succeed, otherwise False.
    """
    return is_port_open("google.com", 80)


@ensure_app_context
def json_response(**kwargs) -> tuple:
    """Build a dictionary and append status code using keyword arguments.

    Also it is jsonify using :flask:`jsonify` method is requested.
    """
    status = kwargs.pop("status", "ok")

    message_index = kwargs.pop("message_index", None)

    lang = kwargs.pop("lang", None)
    lang = getattr(current_user, "language", lang)

    is_jsonified = kwargs.pop("is_jsonified", False)

    status_code = kwargs.pop("status_code", 200)

    result = {"status": status}

    if message_index is not None:
        result["message"] = get_message(message_index, lang)

    result = {**result, **kwargs}

    if is_jsonified:
        result = jsonify(result)

    return result, status_code


@ensure_app_context
def get_message(key: str, lang: str = None, format_data: dict = None) -> str:
    """Get key and language and return language based message.

    Args:
        key: Index of message.
        lang: Requested language.
        format_data: Some date to format message string.

    Returns:
        :obj:`str`: Message according to given language or default language.
    """
    # If language is none, use system language.
    if lang is None:
        lang = current_app.config["DEFAULT_LANGUAGE"]

    # Get message dict according to message index.
    message_dict = translator.get(key, None)

    # If messages are not defined, return key in `Unk()` to express the key,
    # is unknown.
    if not message_dict:
        return f'Unk({key})'

    # Get message according to language.
    message = message_dict[lang]

    # If there is formatting data, format string.
    if format_data:
        message = message.format(**format_data)

    # Return result.
    return message
