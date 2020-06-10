import numpy as np

from flask import Blueprint, request, jsonify
from application.rests.elasticsearch import search, get_docs, update_vector
from application.rests.vectorizer import get_vector
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
            elif author_count < 100:
                author_count += 1
                pub_author["score"] = pub["_score"]
                pub_author["pubs"] = [{
                    "id": pub["_id"], "title": pub["_source"]["title"]
                }]
                pub_author["pub_counts"] = 1
                authors[author_id] = pub_author

        title = pub["_source"].get("title", None) or pub["_source"].get(f'title_{pub["_source"]["lang"]}', "unknown")
        content = pub["_source"].get("content", None) or pub["_source"].get(f'content_{pub["_source"]["lang"]}', "unknown")

        title_keys = [k for k in pub["_source"].keys() if k.startswith("title_")]
        content_keys = [k for k in pub["_source"].keys() if k.startswith("content_")]

        removal_keys = title_keys + content_keys

        for key in removal_keys:
            del pub["_source"][key]

        pub["_source"]["title"] = title
        pub["_source"]["content"] = content

    return jsonify({
        "authors": {"count": author_count, "items": authors.values()[:100]},
        "pubs": {"count": pub_count, "items": pubs}
    })


@bp_elasticsearch.route("/relevance-feedback", methods=["PUT"])
def relevance_feedback():
    """Update document vectors with relevance feedback of user.
    Expects a dictionary named feedback which has relevance_count,
    irrelevance_count, pubs. Every pub has pub_id, relevance, position,
    matched_word_count
    """
    # Get client data.
    feedback = request.json.get("feedback")
    pubs = feedback["pubs"]
    query = feedback["query"]
    # rcount = feedback["rcount"]
    # nrcount = feedback["nrcount"]

    # Get vector and lang. of the query.
    result = get_vector(query)
    qvector = np.array(result["vector"])

    for pub_id, values in pubs.items():
        rcoef = values["matched_word_count"] / values["position"]
        update_vector("publication", pub_id, qvector, rcoef ** 2, values[
            "relevance"])

    return jsonify({"status": "ok"})
