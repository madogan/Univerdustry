import datetime
from _md5 import md5
from random import random
from time import sleep

from scholarly import search_author

from application import celery, logger
from application.rests.mongo import find_one, insert_one, update_one
from application.tasks.find_pdf_primarily import t_find_pdf_primarily
from application.utils.decorators import celery_exception_handler
from application.utils.helpers import preprocess_text


@celery.task(bind=True, name="scrape_publications_of_author", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_scrape_publications_of_author(self, author_id, author_name):
    resd = {"status": "ok"}

    author_info = next(search_author(author_name)).fill()

    counter = 1
    for publication in author_info.publications:
        publication = publication.fill().__dict__

        publication["id"] = publication["id_citations"].split(":")[1].strip()

        title = publication["bib"].get("title", f'unk_{counter}')
        title = preprocess_text(title)

        publication["title_md5"] = md5(title.encode("utf-8")).hexdigest()

        publication.pop("id_citations")
        publication.pop("_filled")
        publication.pop("source")

        publication = {**publication, **publication.pop("bib")}

        pub_in_mongo = find_one(
            "publication", {"filter": {"id": {"$eq": publication["id"]}}}
        )

        if pub_in_mongo:
            update_one(
                "publication", {
                    "filter": {"id": {"$eq": publication["id"]}},
                    "update": {"$addToSet": {"authors": author_id}}
                }
            )

            publication = pub_in_mongo

            publication["authors"] = list(set(
                publication["authors"] + [author_id]
            ))

            logger.info(f'Pub is updated!')
        else:
            publication["created_at"] = datetime.datetime.now().isoformat()
            publication["authors"] = [author_id]

            insert_result = insert_one("publication", publication)

            if insert_result is not None:
                logger.info(f'<{publication["title"]}> is inserted!')

            logger.info(f'Pub is inserted!')

        update_one("author", {
            "filter": {"id": {"$eq": author_id}},
            "update": {"$addToSet": {"publications": publication["id"]}}
        })

        t_find_pdf_primarily.apply_async(
            (publication["id"], title, publication["authors"],
             publication.get("eprint", None))
        )

        counter += 1

        sleep(int(random() * 5))

    resd["num_publications"] = counter

    return resd
