import requests as rq

from application import celery, es, logger
from application.utils.helpers import get_config
from application.utils.text import preprocess_text
from application.utils.mappings import publication_mappings
from application.rests.vectorizer import get_vector, translate
from application.rests.mongo import find, find_one, update_one
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="elasticsearch_indexing", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_elasticsearch_indexing(self, pub_id: str):
    resd = {"status": "ok"}

    pub = find_one("publication", {
        "filter": {"id": {"$eq": pub_id}, "vector": {"$exists": True}}
    })

    pub["authors"] = find("author", {
        "filter": {"id": {"$in": pub.get("authors", [])}},
        "projection": ["id", "name", "affiliation", "citedby", "interests",
                       "organizations"]
    })

    pub.pop("created_at", None)
    pub.pop("raw_base64", None)
    pub.pop("title_md5", None)
    pub.pop("_id", None)

    pub_id = pub.pop("id")

    vector_field_tokens = list()

    if pub.get("content", None):
        vector_field_tokens += pub["content"].split()
    if not pub["title"].startswith("unk_"):
        vector_field_tokens += pub["title"].split()

    vector_field = " ".join(vector_field_tokens)
    vectorizer_response = get_vector(preprocess_text(vector_field))

    pub["lang"] = vectorizer_response["lang"]
    pub["vector"] = vectorizer_response["vector"]

    langs = get_config("LANGUAGES")

    for lang in langs:
        if lang != pub["lang"]:
            pub[f'title_{lang}'] = preprocess_text(
                translate(pub["title"], lang) or ""
            )
            if str(pub.get("content", None)).strip().lower() not in ["none", ""]:
                pub[f'content_{lang}'] = preprocess_text(
                    translate(pub["content"], lang) or ""
                )
        else:
            pub[f'title_{lang}'] = preprocess_text(pub["title"])
            pub[f'content_{lang}'] = preprocess_text(pub.get("content",
                                                             "") or "")

    if "title" in pub: del pub["title"]
    if "content" in pub: del pub["content"]

    update_one("publication", {
        "filter": {"id": {"$eq": pub_id}},
        "update": {"$set": {"vector": pub["vector"],
                            "lang": pub["lang"]}}
    })

    for lang in langs:
        publication_mappings["properties"][f'title_{lang}'] = {"type": "text"}
        publication_mappings["properties"][f'content_{lang}'] = {"type": "text"}

    resp = rq.put(
        get_config("ELASTICSEARCH") + "/publication",
        json={"mappings": publication_mappings}
    )

    if resp.status_code == 400:
        resp = rq.put(
            get_config("ELASTICSEARCH") + "/publication/_mappings",
            json=publication_mappings
        )

    logger.info(f'Mapping Response: {resp.json()}')

    # resp = es.indices.create(
    #     index="publication",
    #     body={"mappings": publication_mappings},
    #     ignore=400
    # )

    result = es.index(index="publication", body=pub, id=pub_id)
    resd["result"] = result
    return resd
