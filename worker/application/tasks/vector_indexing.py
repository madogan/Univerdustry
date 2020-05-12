from elasticsearch import NotFoundError
from langdetect import detect

from application import celery, es, logger
from application.rests.mongo import update_one
from application.rests.vectorizer import get_vector
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="vector_indexing", max_retries=3)
@celery_exception_handler(ConnectionError, NotFoundError)
def t_vector_indexing(self, pub_id: str, content: str):
    resd = {"status": "ok"}

    try:
        lang = detect(content)
    except Exception as e:
        logger.error(f'Content lang. detection error: {str(e)}')
        lang = "en"

    fasttext_vector = get_vector(content, f'fasttext_{lang}')
    muse_vector = get_vector(content, f'muse')

    result = update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"$set": {
            "fasttext": fasttext_vector,
            "muse": muse_vector,
            "lang": lang
        }}
    })

    resd["db_result"] = result

    es.indices.put_mapping(
        index="publication",
        body={
            "properties": {
                "fasttext": {
                    "type": "dense_vector", "dims": 300
                },
                "muse": {
                    "type": "dense_vector", "dims": 300
                }
            }
        }
    )

    result = es.update(
        index="publication", id=pub_id,
        body=f'{{"doc": {{ "fasttext": {fasttext_vector}, "muse": {muse_vector}, "lang": {lang} }} }}'
    )

    resd["es_result"] = result

    return resd
