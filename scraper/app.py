# -*- coding: utf-8 -*-
""""""

# Import system level libraries.
import os
import sys

# Store path of application root in a variable.
from threading import Thread

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# File logger.
logger.add(sink=sys.stderr,
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| {message}", serialize=True,
           level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))

# Import necessary libraries.
from scrapy.crawler import CrawlerProcess
from flask import Flask, jsonify, request, url_for
from scrapy.utils.project import get_project_settings

# Create application instance.
app = Flask(__name__)

# Update json encoder
from custom_json_encoder import CustomJsonEncoder
app.json_encoder = CustomJsonEncoder

# Create and configure celery instance.
from ops_celery import make_celery
celery = make_celery(app)


@celery.task(bind=True)
def starter(self, organization_domain):
    logger.debug(f'Starter for {organization_domain}')
    process = CrawlerProcess(get_project_settings())

    process.crawl(table[organization_domain])
    process.start()  # the script will block here until the crawling is finished
    logger.debug(f'Process started.')


# Spiders match table.
table = {"marmara.edu.tr": "marmara_university_authors_spider"}


@app.route("/")
def index():
    return "Scraper is running."


@app.route("/univerdustry/scraper/start", methods=["GET"])
def get_university():
    # Posted data must be json.
    if not request.is_json:
        return jsonify({"status": "error",
                        "message": "Bad request. Posted data must be json. Check your headers."}), 400

    # Get posted data as json.
    data = request.json

    # Get ``author_name`` from ``data``.
    organization_domain = data.get("organization_domain", None)

    # ``author_name`` must be provided.
    if organization_domain is None or organization_domain not in table:
        return jsonify({"status": "error", 
                        "message": "Bad request. ``organization_domain`` field not "
                                   "found in posted data or not supported."}), 400

    # Add task to queue.
    task = starter.apply_async(args=[organization_domain])

    return jsonify({"status": "ok", "message": "Added to queue.", "task_id": task.id}), 202
