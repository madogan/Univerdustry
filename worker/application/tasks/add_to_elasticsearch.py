from application import celery, es
from application.rests.mongo import find_one


@celery.task(bind=True, name="add_to_elasticsearch")
def task_add_to_elasticsearch(self, pub_id: str):
    resd = {"status": "ok"}

    publication = find_one(
        "publication",
        {"filter": {"id": {"$eq": pub_id}}}
    )

    if not publication:
        return resd

    authors = list()
    for author_id in publication["authors"]:
        author = find_one(
            "author",
            {"filter": {"id": {"$eq": author_id}}}
        )
        authors.append(author)

    publication["authors"] = authors
    publication["title"] = publication["bib"].get("title", "unknown_title")
    publication["year"] = publication["bib"].get("year", 9999)

    publication.pop("_filled")
    publication.pop("bib")
    publication.pop("created_at")
    publication.pop("raw_base64")
    publication.pop("source")
    publication.pop("_id")

    es.index("publication", publication, doc_type="publication")

    return resd
