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
from flask import Flask, jsonify, request, abort, render_template

# Create application instance.
app = Flask(__name__)

# Update json encoder
from custom_json_encoder import CustomJsonEncoder

app.json_encoder = CustomJsonEncoder

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
DATABASE_REST_URL = os.getenv("DATABASE_REST_URL")

from elasticsearch import Elasticsearch

es = Elasticsearch(ELASTICSEARCH_URL)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route(f'/api/v{__version__}/scrape/<organization_domain>',
           methods=["GET"])
def scrape(organization_domain):
    url = os.getenv("SCRAPER_URL") + "/univerdustry/scraper/start"

    data = {"organization_domain": organization_domain}
    response = requests.post(url, json=data).json()

    if response["status"] == "ok":
        return jsonify(response), 202
    else:
        return jsonify({"status": "error", "message": response["message"]}), \
               500


@app.route(f'/api/v{__version__}/search', methods=["GET"])
def search():
    data = request.args

    if "q" not in data:
        abort(404)

    try:
        es_data = es.search(index="_all", body={
            "query": {
                "multi_match": {
                    "query": data["q"],
                    "fields": ["publication.content_text",
                               "publication.title", "author.affiliation",
                               "author.name", "author.interests",
                               "publication.ident", "author.ident"]
                }
            }
        })
        result = {"status": "ok",
                  "data": es_data.get("hits", {}).get("hits", [])}
    except Exception as e:
        result = {"status": "failure", "message": str(e)}

    return jsonify(result)


@app.route(f'/api/v{__version__}/author/<author_id>', methods=["GET"])
def get_author(author_id):
    # TODO: Input check.
    rq = requests.get(DATABASE_REST_URL
                      + f'/author?ident=eq.{author_id}').json()
    return jsonify(rq)


@app.route(f'/api/v{__version__}/publication/<publication_id>',
           methods=["GET"])
def get_publication(publication_id):
    # TODO: Input check.
    rq = requests.get(DATABASE_REST_URL
                      + f'/publication?ident=eq.{publication_id}').json()
    return jsonify(rq)
