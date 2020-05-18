import datetime

from _md5 import md5
from time import sleep
from random import random
from scholarly import search_author
from application import celery, logger
from application.utils.helpers import preprocess_text
from application.utils.decorators import celery_exception_handler
from application.rests.mongo import find_one, insert_one, update_one
from application.tasks.find_pdf_primarily import t_find_pdf_primarily


@celery.task(bind=True, name="scrape_publications_of_author", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_scrape_publications_of_author(self, author_id, author_name):
    resd = {"status": "ok"}

    author_info = next(search_author(author_name)).fill()

    updates = list()

    counter = 1
    for publication in author_info.publications:
        pub_id = publication.id_citations.split(":")[1].strip()

        title = publication.bib.get("title", f'unk_{counter}')
        if not title.startswith("unk_"):
            title = preprocess_text(title)

        if title.strip() == "":
            continue

        pub_in_mongo = find_one(
            "publication", {"filter": {"id": {"$eq": pub_id}}}
        )

        if not pub_in_mongo:
            publication = publication.fill().__dict__

            publication["id"] = pub_id
            publication["title_md5"] = md5(title.encode("utf-8")).hexdigest()

            publication["created_at"] = datetime.datetime.now().isoformat()
            publication["authors"] = [author_id]

            publication.pop("id_citations", None)
            publication.pop("_filled", None)
            publication.pop("source", None)

            publication = {**publication, **publication.pop("bib", dict()),
                           "title": title}

            insert_result = insert_one("publication", publication)
            logger.info(f'<{publication["title"]}> | {insert_result}')

        if pub_in_mongo:
            if pub_in_mongo.get("title", None) is None:
                publication = publication.fill().__dict__

                publication["title_md5"] = md5(
                    title.encode("utf-8")).hexdigest()

                publication["created_at"] = datetime.datetime.now().isoformat()
                publication["authors"] = [author_id] + pub_in_mongo.get("authors", list())

                publication.pop("id_citations", None)
                publication.pop("_filled", None)
                publication.pop("source", None)

                publication = {**publication, **publication.pop("bib", dict()),
                               "title": title}

                update_result = update_one("publication", {
                    "filter": {"id": {"$eq": pub_id}},
                    "update": {"$set": publication}
                })
                logger.info(f'<{publication["title"]}> | {update_result}')
            else:
                updates.append(pub_id)

                publication = pub_in_mongo

                publication["authors"] = list(set(
                    publication.get("authors", list()) + [author_id]
                ))

                logger.info(f'Pub is updated!')

        update_one("author", {
            "filter": {"id": {"$eq": author_id}},
            "update": {"$addToSet": {"publications": pub_id}}
        })

        t_find_pdf_primarily.apply_async(
            (pub_id, title, publication["authors"],
             publication.get("eprint", None))
        )

        counter += 1

        sleep(int(random() * 2))

    update_one(
        "publication", {
            "filter": {"id": {"$in": updates}},
            "update": {"$addToSet": {"authors": author_id}}
        }
    )

    resd["num_publications"] = counter

    return resd
