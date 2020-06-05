from application import logger
from flask import Blueprint, request, jsonify
from application.rests.elasticsearch import search
from application.utils.auto_sorted_dict import AutoSortedDict

bp_elasticsearch = Blueprint("bp_elasticsearch", __name__,
                             url_prefix="/elasticsearch")


@bp_elasticsearch.route("/search/publication", methods=["GET"])
def search_publication():
    pubs = search("publication", request.args["text"])

    authors = AutoSortedDict(sort_field="score")
    author_count, pub_count = 0, 0
    for pub in pubs:
        pub_count += 1
        pub.pop("_index")
        pub_authors = pub["_source"].get("authors", list())
        for pub_author in pub_authors:
            author_id = pub_author.pop("id")

            if authors.get(author_id, None) is not None:
                current_author = authors[author_id]
                del authors[author_id]

                current_author["pub_counts"] += 1
                current_author["score"] += pub["_score"]
                current_author["pubs"].append({
                    "id": pub["_id"], "title": pub["_source"]["title"]
                })

                authors[author_id] = current_author
            else:
                author_count += 1
                pub_author["score"] = pub["_score"]
                pub_author["pubs"] = [{
                    "id": pub["_id"], "title": pub["_source"]["title"]
                }]
                pub_author["pub_counts"] = 1
                authors[author_id] = pub_author

    return jsonify({
        "authors": {"count": author_count, "items": authors.values()},
        "pubs": {"count": pub_count, "items": pubs}
    })
