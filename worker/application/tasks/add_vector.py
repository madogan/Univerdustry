from _md5 import md5

from elasticsearch import NotFoundError

from application import celery, logger, es
from application.rests.mongo import update_one, find_one
from application.rests.vectorizer import get_vector
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="add_vector", max_retries=3)
@celery_exception_handler(ConnectionError, NotFoundError)
def task_add_vector(self, pub_id: str):
    resd = {"status": "ok"}

    publication = find_one(
        "publication",
        {"filter": {"id": {"$eq": pub_id}}}
    )

    if not publication:
        return resd

    logger.debug(f'Publication: {publication}')

    title = publication.get("title", None) or ""
    content = publication.get("content", None) or ""

    if content:
        vectorization = get_vector(content)
    else:
        vectorization = get_vector(title)

    result = update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"$set": {"fasttext_vector": vectorization["vector"]}}
    })

    resd["db_result"] = result

    es.indices.put_mapping(
        index="publication",
        body={
            "properties": {
                "fasttext_vector": {
                    "type": "dense_vector", "dims": 300
                }
            }
        }
    )

    result = es.update(
        index="publication", doc_type="publication", id=publication["id"],
        body=f'{{"doc": {{ "fasttext_vector": {vectorization["vector"]} }} }}'
    )

    resd["es_result"] = result

    return resd
