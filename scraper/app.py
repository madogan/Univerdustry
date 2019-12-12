# Import system level libraries.
import os
import sys

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# File logger.
logger.add(sink=sys.stderr,
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "
                  "{message}", serialize=True,
           level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))

# Import necessary libraries.
from flask import Flask, jsonify, request
from scrapy.crawler import CrawlerProcess
from werkzeug.exceptions import BadRequest
from scrapy.utils.project import get_project_settings

# Create application instance.
app = Flask(__name__)

# Update json encoder
from custom_json_encoder import CustomJsonEncoder
app.json_encoder = CustomJsonEncoder

# Create and configure celery instance.
# from ops_celery import make_celery
# celery = make_celery(app)
#
#
# @celery.task(bind=True)
# def starter(self, organization_domain):
#     logger.debug(f'Starter for {organization_domain}')
#
#     process = CrawlerProcess(get_project_settings())
#
#     process.crawl(organization_domain)
#
#     logger.debug(f'Process started.')


@app.route("/")
def index():
    return "Scraper is running."


@app.route("/univerdustry/scraper/start", methods=["POST"])
def get_university():
    # Posted data must be json.
    if not request.is_json:
        return BadRequest

    # Get posted data as json.
    data = request.json

    # Get ``author_name`` from ``data``.
    organization_domain = data.get("organization_domain", None)

    # ``author_name`` must be provided.
    if organization_domain is None:
        return BadRequest

    try:
        from threading import Thread

        process = CrawlerProcess(get_project_settings())

        process.crawl(organization_domain)

        Thread(target=process.start, daemon=True).start()
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500

    return jsonify({"status": "ok"}), 202
