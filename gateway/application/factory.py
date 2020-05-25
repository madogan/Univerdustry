# -*- coding: utf-8 -*-
"""Application Factory Module

This module consist of application creation functions designed according to
application factory pattern. It also contains blueprint registration
function and extensions initialization function.
"""

import os

from flask import Flask


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

    # This is to solve conflicts between `Vue.JS` and `Jinja` rendering of
    # html files.
    app.jinja_env.variable_start_string = "(|"
    app.jinja_env.variable_end_string = "|)"

    # Add special converter for comma separated arguments.
    from application.utils.url_converters import (ListConverter,
                                                  IntListConverter)
    app.url_map.converters["list"] = ListConverter
    app.url_map.converters["int_list"] = IntListConverter

    # Get application environment from environmental variable if given.
    environment = os.getenv("FLASK_ENV") or environment

    # Configure application.
    from application.config import config
    app.config.from_object(config[environment])

    # Update json encoder for more general serializing.
    from application.utils.custom_json_encoder import CustomJsonEncoder
    app.config.update({"RESTFUL_JSON": {"cls": CustomJsonEncoder}})
    app.json_encoder = CustomJsonEncoder

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
    from application.bps.index import bp_index
    _app.register_blueprint(bp_index)

    from application.bps.organization import bp_organization
    _app.register_blueprint(bp_organization)

    from application.bps.elasticsearch import bp_elasticsearch
    _app.register_blueprint(bp_elasticsearch)

    from application.bps.worker import bp_worker
    _app.register_blueprint(bp_worker)


def initialize_extensions(_app: Flask) -> None:
    """This function initialize to integrate flask extensions.

    Arguments:
        _app:  Flask application instance.
    """
    pass
