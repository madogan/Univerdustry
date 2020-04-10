from application import celery, logger
from application.rests.mongo import update_one, find_one
from application.rests.vectorizer import get_vector


@celery.task(bind=True, name="add_vector")
def task_add_vector(self, pub_id: str):
    resd = {"status": "ok"}

    publication = find_one(
        "publication",
        {"filter": {"id": {"$eq": pub_id}}}
    )

    if not publication:
        return resd

    logger.debug(f'Publication: {publication}')

    vectorization = get_vector(publication["content"])

    result = update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"$set": {"vector": vectorization["vector"]}}
    })

    resd["result"] = result

    return resd
