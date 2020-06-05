from collections import defaultdict
from flask import Blueprint, request, jsonify
from application.rests.elasticsearch import search


bp_elasticsearch = Blueprint("bp_elasticsearch", __name__,
                             url_prefix="/elasticsearch")


@bp_elasticsearch.route("/search/publication", methods=["GET"])
def search_publication():
    pubs = search("publication", request.args["text"])

    authors = dict()
    author_count, pub_count = 0, 0
    author_pubs = defaultdict(list)
    author_scores = defaultdict(int)
    aurhor_pub_counts = defaultdict(int)
    for pub in pubs:
        pub_count += 1
        pub.pop("_index")
        pub_authors = pub["_source"].get("authors", list())
        for pub_author in pub_authors:
            author_id = pub_author.pop("id")
            authors[author_id] = pub_author
            aurhor_pub_counts[author_id] += 1
            author_scores[author_id] += pub["_score"]
            author_pubs[author_id].append({
                "id": pub["_id"], "title": pub["_source"]["title"]
            })

    author_scores = dict(sorted(
        author_scores.items(), key=lambda x: x[1],  reverse=True
    ))

    authors_sorted_list = list()
    for author_id, score in author_scores.items():
        authors_sorted_list.append({
            **authors[author_id], "score": score,
            "matched_pub_count": aurhor_pub_counts[author_id],
            "matched_pubs": author_pubs[author_id]
        })
        author_count += 1

    return jsonify({
        "authors": {"count": author_count, "items": authors_sorted_list},
        "pubs": {"count": pub_count, "items": pubs}
    })
