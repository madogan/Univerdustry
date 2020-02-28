# -*- coding: utf-8 -*-
"""Application Factory Module

This module consist of application creation functions designed according to
application factory pattern. It also contains blueprint registration
function and extensions initialization function.
"""

import os

from celery import Celery
from flask import Flask
from redis import Redis

from application.utils.helpers import ensure_app_context


def create_app(environment: str = "development") -> Flask:
    """Create application as fully configured and initialized.

    `Application Factory`_ pattern is used for application creation.

    Args:
        environment:
            This parameter determines application environment. Defaults
            to `development`. It can be only one of `development`, `testing`
            and `production`.

    Returns:
        :flask:`Flask`: Fully configured and initialized Flask Application.

    .. _Application Factory:
        https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/
        https://hackersandslackers.com/demystifying-flask-application-factory/
    """

    if environment not in ["development", "testing", "production"]:
        raise ValueError('Environment must be one of `development`, '
                         '`testing` and `production`.')

    # Create flask application with name of current module. This is for
    # convention according to docs.
    # More about ``__name__`` as argument of ``flask.Flask``:
    #   https://stackoverflow.com/questions/39393926/flaskapplication-
    #   versus-flask-name
    from flask import Flask
    app = Flask(__name__)

    # Get application environment from environmental variable if given.
    environment = os.getenv("FLASK_ENV") or environment

    # Configure application.
    from application.config import config
    app.config.from_object(config[environment])

    # Update json encoder for more general serializing.
    from application.utils.custom_json_encoder import CustomJsonEncoder
    app.config.update({"RESTFUL_JSON": {"cls": CustomJsonEncoder}})
    app.json_encoder = CustomJsonEncoder

    from flask import json

    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["json_serializer"] = json.dumps
    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["json_deserializer"] = json.loads

    # Set some functions runs before first request for initializing.
    set_before_first_request_functions(app)

    # Set some functions runs before every requests.
    set_before_requests_functions(app)

    # Initialize extensions which are declared above.
    initialize_extensions(app)

    # Register designed blueprints.
    register_blueprints(app)

    return app


def set_before_first_request_functions(_app: Flask) -> None:
    """Sets some functions to run before first request.

    Args:
        _app: Address of :flask:`Flask` application instance.
    """
    pass


def set_before_requests_functions(_app: Flask) -> None:
    """Sets some functions to run before every requests.

    Args:
        _app: Address of :flask:`Flask` application instance.
    """
    pass


def register_blueprints(_app: Flask) -> None:
    """Registers blueprints to :flask: application.

    Args:
        _app: Address of :flask:`Flask` application instance.
    """
    from application.bps.index import index_bp
    _app.register_blueprint(index_bp)

    from application.bps.tasks import tasks_bp
    _app.register_blueprint(tasks_bp)


def initialize_extensions(_app: Flask) -> None:
    """This function initialize to integrate flask extensions.

    Arguments:
        _app:  Flask application instance.
    """
    pass


def create_redis():
    return Redis.from_url(os.getenv("CELERY_BROKER_URL"))


def create_celery(app_name: str) -> Celery:
    """Create configured celery instance.

    Args:
        app_name: Flask application name.

    Returns:
        :celery:`Celery`: Configured celery instance.
    """
    # Create celery instance.
    celery = Celery(app_name,
                    backend=os.getenv("CELERY_BROKER_URL"),
                    broker=os.getenv("CELERY_BROKER_URL"),
                    include=[app_name])

    # # Configure celery with app config.
    # celery.conf.update(_app.config)

    # Configure celery.
    # noinspection PyTypeChecker
    celery.conf.update(
        task_serializer="json",
        accept_content=["application/json"],
        result_serializer="json",
        enable_utc=True,
        task_create_missing_queues=True,
        # celery_queues=(
        #     Queue("background", Exchange("background"),
        #           routing_key="background"),
        #     Queue("foreground", Exchange("foreground"),
        #           routing_key="foreground")
        # ),
        # task_default_queue="background"
    )

    # noinspection PyPep8Naming
    TaskBase = celery.Task

    # Update base :celery:`Task` class for application context ensuring.
    class ContextTask(TaskBase):
        abstract = True

        @ensure_app_context
        def __call__(self, *args, **kwargs):
            return TaskBase.__call__(self, *args, **kwargs)

    # noinspection PyPropertyAccess
    celery.Task = ContextTask

    return celery
