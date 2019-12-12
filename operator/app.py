# Import system level libraries.
import os
import sys

# Store path of application root in a variable.
from werkzeug.exceptions import BadRequest

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Console logger.
logger.add(sink=sys.stderr, level="DEBUG")

# File logger.
logger.add(sink=os.path.join(ROOT_DIR, "logs", "log_{time}.log"),
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "
                  "{message}", serialize=True,
           rotation="100 MB",  # Every log file max size.
           # Remove logs older than 3 days.
           retention="3 days", level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))

# Import necessary libraries.
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from sqlalchemy_utils import database_exists, create_database

# Create application instance.
app = Flask(__name__)

# Configure application.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("PGRST_DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Update json encoder
from custom_json_encoder import CustomJsonEncoder

app.json_encoder = CustomJsonEncoder

# Create and init database instance.
db = SQLAlchemy(app)

# Create and configure celery instance.
from ops_celery import make_celery
celery = make_celery(app)

# Import database models classes.
from models import *

# Import task
from ops import get_author_and_publications


@app.before_first_request
def do_these_before_first_request():
    """Create database if not
    
    This function executes before first request.
    It will check and create database and tables.
    """

    # NOTE: This is best solution. Use this to create database
    #       for other projects.
    if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
        create_database(app.config["SQLALCHEMY_DATABASE_URI"])

    # Create tables if not exists.
    # NOTE: If a table is missing in database it won't create.
    #       It creates if all models are not created.
    db.create_all()


@app.route("/")
def index():
    return "Operator is running."


@app.route("/univerdustry/add/author", methods=["POST"])
def add_author():
    # Posted data must be json.
    if not request.is_json:
        return BadRequest

    # Get posted data as json.
    data = request.json

    # Get ``author_name`` from ``data``.
    author_name = data.get("author_name", None)

    # ``author_name`` must be provided.
    if author_name is None:
        return BadRequest

    logger.info(f'Queuing task for "{author_name}"')

    # Add task to queue.
    task = get_author_and_publications.apply_async(args=[author_name])

    return jsonify({"status": "ok", "message": "Added to queue."}), 202, \
           {"Location": url_for("check_task_status", task_id=task.id)}


@app.route("/univerdustry/task/<task_id>/status")
def check_task_status(task_id):
    task = get_author_and_publications.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
