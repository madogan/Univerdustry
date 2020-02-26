# -*- coding: utf-8 -*-
"""This module consists configuration of application.

This module consist of application creation function as application factory,
blueprint registration function and extensions initialization function.
Also it consist of application level attributes like ``db`` as database 
object.

Attributes:
    config (dict): It gives config according to key of environment.
"""
import os

from worker.utils.custom_json_encoder import CustomJsonEncoder


class BaseConfig(object):
    """Base configuration class for application."""

    DEBUG = False
    DATETIME_FORMAT = "%d-%m-%Y"
    RESTFUL_JSON = {'cls': CustomJsonEncoder}
    SECRET_KEY = os.urandom(16).hex()  # It results 32 length hex string.

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 512,
        "pool_timeout": 1,
        "max_overflow": 12
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development specified configuration class."""

    DEBUG = True

    # This for avoiding token invalidation. Because every time application
    # built, secret key will change. When secret key changed token will be
    # invalid.
    SECRET_KEY = "VCcbkFCUwOrtxBdrVCcbkFCUwOrtxBdr"
    CONSOLE_LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    """Test specified configuration class."""

    DEBUG = True

    # Enable the TESTING flag to disable the error catching during request
    # handling so that you get better error reports when performing test
    # requests against the application.
    TESTING = True

    # Because of the error: ``Popped wrong app context.``
    # See Also:
    # https://stackoverflow.com/questions/26647032/py-test-to-test-flask
    # -register-assertionerror-popped-wrong-request-context
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production specified configuration class."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
