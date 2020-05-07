from _md5 import md5

from langdetect import detect

from application import celery, es
from application.rests.mongo import find_one
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="elasticsearch_indexing", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_elasticsearch_indexing(self, pub_id: str):
    resd = {"status": "ok"}

    publication = find_one("publication", {"filter": {"id": {"$eq": pub_id}}})

    authors = list()
    for author_id in publication.get("authors", list()):
        author = find_one("author", {"filter": {"id": {"$eq": author_id}}})
        authors.append(author["name"])

    publication["authors"] = authors

    try:
        publication["lang"] = detect(
            publication.get("content", publication["title"])
        )
    except Exception:
        publication["lang"] = "en"

    publication.pop("created_at")
    publication.pop("raw_base64")
    publication.pop("name")
    publication.pop("_id")

    es.index(index="publication", body=publication, id=publication.pop("id"))

    return resd
