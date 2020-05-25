from flask import Blueprint, request, jsonify
from application.rests.elasticsearch import search

bp_elasticsearch = Blueprint("bp_elasticsearch", __name__,
                             url_prefix="/elasticsearch")


@bp_elasticsearch.route("/search/publication", methods=["GET"])
def search_publication():
    response = search("publication", request.json["text"])

    # hits = response.get("hits", {}).get("hits", [])
    # total = response.get("hits", {}).get("total", {})
    #
    # authors = dict()
    # for hit in hits:
    #     pub_authors = hit.get("_source", {}).get("authors", [])
    #

    return jsonify(response)
