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

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from worker.utils.custom_json_encoder import CustomJsonEncoder


class BaseConfig(object):
    """Base configuration class for application."""

    DEBUG = False
    LANGUAGES = ["tr", "en"]
    DEFAULT_LANGUAGE = "tr"
    SYSTEM_USER_NAME = "AllConfig"
    JWT_ALGORITHM = "HS256"

    DATETIME_FORMAT = "%d-%m-%Y"

    # Sqlalchemy forces us to use primary key. We need to avoid multiple
    # rows for some tables. So, we use a string primary key for all single
    # row tables, to avoid auto increment and multiple rows.
    SINGLE_ROW_TABLES_PRIMARY_KEY = -1

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 256,
        "pool_timeout": 3,
        "max_overflow": 12
    }

    RESTFUL_JSON = {'cls': CustomJsonEncoder}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL").format("allconfig")

    SECRET_KEY = os.urandom(16).hex()  # It results 32 length hex string.
    AES_IV = os.urandom(16)

    # Enable CSRF tokens in the Forms.
    WTF_CSRF_ENABLED = True
    FILES_PATH = os.path.join("application", "static", "files")
    STATIC_DB_FILES_PATH = os.path.join("application", "static", "db")

    SCHEDULER_API_ENABLED = True

    SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 8}}
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    SOCKET_APP_URL = os.getenv("SOCKET_APP_URL")
    FLOWER_APP_URL = os.getenv("FLOWER_APP_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_BROKER")

    DB_HISTORY_DAYS_LIMIT = 30

    HOST = None


class DevelopmentConfig(BaseConfig):
    """Development specified configuration class."""

    DEBUG = True

    # We are fixing this because sometimes when we recreate application
    # Device users may not be reachable.
    AES_IV = b'VCcbkFCUwOrtxBdr'

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

    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False

    # Because of the error: ``Popped wrong app context.``
    # See Also:
    # https://stackoverflow.com/questions/26647032/py-test-to-test-flask
    # -register-assertionerror-popped-wrong-request-context
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # Test on different database.
    SQLALCHEMY_DATABASE_URI = "postgres://allconfig:allconfig@localhost:5432" \
                              "/allconfig_test"

    STATIC_DB_FILES_PATH = os.path.join("..", "..", "application", "static",
                                        "db", "role_table.json")


class ProductionConfig(BaseConfig):
    """Production specified configuration class."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
