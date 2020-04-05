# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import datetime
from string import ascii_lowercase, digits

from flask import current_app
from application import logger
from application.utils.contextor import ensure_app_context


@ensure_app_context
def get_config(name):
    return current_app.config.get(name, None)


@ensure_app_context
def set_config(name, value):
    current_app.config[name] = value


@ensure_app_context
def get_logger():
    return logger


def get_time_limit():
    now = datetime.datetime.now()
    time_limit = now - datetime.timedelta(
        days=get_config("DB_HISTORY_DAYS_LIMIT")
    )
    return time_limit


def extract_file_name_from_url(url):
    file_name = url.split("/")[-1].split(".")[0].lower().replace(" ", "")
    accepted_chars = ascii_lowercase + digits + "_"
    file_name = "".join([c for c in file_name if c in accepted_chars])
    return file_name
