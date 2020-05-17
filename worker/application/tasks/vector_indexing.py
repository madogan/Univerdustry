import json

from langdetect import detect
from elasticsearch import NotFoundError
from application import celery, es, logger
from application.rests.mongo import update_one
from application.rests.vectorizer import get_vector
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="vector_indexing", max_retries=3)
@celery_exception_handler(ConnectionError, NotFoundError)
def t_vector_indexing(self, pub_id: str, content: str = None,
                      title: str = None):
    resd = {"status": "ok"}

    vector_field_tokens = list()

    if content is not None:
        vector_field_tokens += content.split()

    if title is not None and not title.startswith("unk_"):
        vector_field_tokens += title.split()

    vector_field = " ".join(vector_field_tokens)

    try:
        lang = detect(vector_field)
    except Exception as e:
        logger.error(f'Content lang. detection error: {str(e)}')
        lang = "en"

    vectorizer_response = get_vector(vector_field, lang)

    doc = {"vector": vectorizer_response["vector"], "lang": lang}

    result = update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"$set": doc}
    })

    resd["db_result"] = result

    es.indices.put_mapping(
        index="publication",
        body={
            "properties": {
                "vector": {
                    "type": "dense_vector", "dims": 300
                },
                "lang": {
                    "type": "text"
                }
            }
        }
    )

    result = es.update(
        index="publication", id=pub_id,
        body=json.dumps({"doc": doc})
    )

    resd["es_result"] = result

    return resd
