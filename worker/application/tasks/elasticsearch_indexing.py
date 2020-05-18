from langdetect import detect
from application import celery, es
from application.rests.mongo import find_one, update_one
from application.rests.vectorizer import get_vector
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="elasticsearch_indexing", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_elasticsearch_indexing(self, pub_id: str):
    resd = {"status": "ok"}

    publication = find_one("publication", {"filter": {"id": {"$eq": pub_id}}})

    authors = list()
    for author_id in publication.get("authors", list()):
        author = find_one("author", {"filter": {"id": {"$eq": author_id}}})
        authors.append({
            "name": author["name"],
            "affiliation": author.get("affiliation", None)
        })

    publication["authors"] = authors

    try:
        publication["lang"] = detect(
            publication.get("content", publication["title"])
        )
    except Exception:
        publication["lang"] = "en"

    publication.pop("created_at", None)
    publication.pop("raw_base64", None)
    publication.pop("title_md5", None)
    publication.pop("_id", None)

    pub_id = publication.pop("id")
    title = publication.get("title", None)
    content = publication.get("content", None)

    vector_field_tokens = list()

    if content is not None:
        vector_field_tokens += content.split()

    if title is not None and not title.startswith("unk_"):
        vector_field_tokens += title.split()

    vector_field = " ".join(vector_field_tokens)

    vectorizer_response = get_vector(vector_field, publication["lang"])

    publication["vector"] = vectorizer_response["vector"]

    update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"vector": {"$set": publication["vector"]}}
    })

    result = es.index(index="publication", body=publication, id=pub_id)

    resd["result"] = result

    return resd
