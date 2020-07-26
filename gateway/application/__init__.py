# -*- coding: utf-8 -*-
"""Application Initializer Module

This module consist of application and application level attributes
like ``db`` as database object.

Attributes:
    ROOT_DIR (str): This variable store absolute path of
        root dir of application.
"""
# Version of the application.
# TODO: Research for SemVer for versioning.
__version__ = "0.1"

# This lib. provides safe threading. For more information: http://eventlet.net/
import eventlet

# System library.
import sys

# Monkey patching is for multi-threading with Flask requests.
if sys.version_info[1] > 6:  # If python version is greater then 3.6
    # This is done because there is some incompatibles with eventlet
    # with greater version of Python 3.6
    eventlet.monkey_patch(os=False)
else:
    eventlet.monkey_patch()

# Operating system library.
import os

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Remove default handler.
logger.remove()

# Console logger.
logger.add(
    sink=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO"),
    format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| {message}"
)

from elasticsearch import Elasticsearch
es = Elasticsearch(os.getenv("ELASTICSEARCH"))

from googletrans import Translator
translator = Translator()

# Create application instance.
from application.factory import create_app
app = create_app()

from application.utils.before_first_request_funcs import init_db
init_db()
