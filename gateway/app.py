# -*- coding: utf-8 -*-
"""This app gets all requests and orchestrate them"""

__version__ = "0.1"

# Import system level libraries.
import os
import sys

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Console logger.
logger.add(sink=sys.stderr,
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "
                  "{message}", serialize=True,
           level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))

# Import necessary libraries.
import requests
from flask import Flask, jsonify


# Create application instance.
app = Flask(__name__)

# Update json encoder
from custom_json_encoder import CustomJsonEncoder

app.json_encoder = CustomJsonEncoder

from elasticsearch import Elasticsearch
es = Elasticsearch(os.getenv("ELASTICSEARCH_URL"))


@app.route("/")
@app.route("/index")
def index(path):
    return "Gateway is working..."


@app.route(f'/api/v{__version__}/scrape/<organization_domain>', methods=["GET"])
def scrape(organization_domain):
    url = os.getenv("SCRAPER_URL") + "/univerdustry/scraper/start"

    data = {"organization_domain": organization_domain}
    response = requests.post(url, json=data).json()

    if response["status"] == "ok":
        return jsonify(response), 202
    else:
        return jsonify({"status": "error", "message": response["message"]}), \
               500

#
# @app.route(f'/api/v{__version__}/search', methods=["GET"])
# def search():
#     data = request.args.json()
#
#     if "query" not in data:
#         abort(404)
#
#     result = es.search(index="marmara_edu_tr",
#                        body={"query": {"match": {"full_text": data["query"]}}})
#
#     return jsonify(result)
#
#
# @app.route(f'/api/v{__version__}/author/<author_id>', methods=["GET"])
# def get_author(author_id):
#     # TODO: Input check.
#     return jsonify(requests.get(DATABASE_REST_URL + f'/author?ident=eq.{author_id}'))
#
#
# @app.route(f'/api/v{__version__}/publication/<publication_id>', methods=["GET"])
# def get_publication(publication_id):
#     # TODO: Input check.
#     return jsonify(requests.get(DATABASE_REST_URL + f'/publication?ident=eq.{publication_id}'))
#
#
#
