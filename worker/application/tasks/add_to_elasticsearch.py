from _md5 import md5

from langdetect import detect

from application import celery, es
from application.rests.mongo import find_one
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="add_to_elasticsearch", max_retries=3)
@celery_exception_handler(ConnectionError)
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
        authors.append(author["name"])

    publication["authors"] = authors

    try:
        publication["lang"] = detect(publication.get("content",
                                                     publication["title"]))
    except Exception:
        publication["lang"] = "en"

    publication.pop("created_at")
    publication.pop("raw_base64")
    publication.pop("name")
    publication.pop("_id")

    es.index("publication", publication, id=publication.pop("id"),
             doc_type="publication")

    return resd
