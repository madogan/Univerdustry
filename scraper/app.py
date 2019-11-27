# -*- coding: utf-8 -*-
"""Summary

Description.

TODO:
    *
"""

# Import system level libraries.
import os
import sys

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Console logger.
logger.add(sink=sys.stderr, level="DEBUG")

# File logger.
logger.add(sink=os.path.join(ROOT_DIR, "logs", "log_{time}.log"),
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| {message}", serialize=True,
           rotation="100 MB",  # Every log file max size.
           retention="3 days", level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))  # Remove logs older than 3 days.

# Import neccessary libraries.
from flask.helpers import url_for
from flask.wrappers import Response
from scrapy.crawler import CrawlerProcess
from flask import Flask, abort, json, jsonify, request
from scrapy.utils.project import get_project_settings

# Create application instance.
app = Flask(__name__)

# Update json encoder
from custom_json_encoder import CustomJsonEncoder
app.json_encoder = CustomJsonEncoder


# Spiders match table.
table = {"marmara.edu.tr": "marmara_university_authors_spider"}


@app.route("/")
def index():
    return "Scraper is running."


@app.route("/univerdustry/add/organization", methods=["POST"])
def get_university():
    # Posted data must be json.
    if not request.is_json:
        return jsonify({"status": "error", 
                        "message": "Bad request. Posted data must be json."
                                   "Check your headers."}), 400

    # Get posted data as json.
    data = request.json

    # Get ``author_name`` from ``data``.
    organization_domian = data.get("organization_domian", None)

    # ``author_name`` must be provided.
    if organization_domian is None or organization_domian not in table:
        return jsonify({"status": "error", 
                        "message": "Bad request. ``organization_domian`` field not "
                                   "found in posted data or not supported."}), 400

    logger.info(f'Scraping for "{organization_domian}"')

    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    process.crawl(table[organization_domian])
    process.start() # the script will block here until the crawling is finished

    return jsonify({"status": "ok", "message": "Started."}), 202
