from random import random

from eventlet import sleep

from application import celery, logger
from application.rests.mongo import find, find_one, insert_one, update_one
from application.rests.scholar import (get_authors, get_next_page,
                                       get_organization_page, parse_author)
from application.tasks.scrape_publications_of_author import \
    t_scrape_publications_of_author
from application.utils.decorators import celery_exception_handler


@celery.task(bind=True, name="authors_scraper", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_authors_scraper(self):
    organizations = find("organization")  # Get all organizations.

    len_organizations = len(organizations)

    logger.info(f'There are {len_organizations} organizations.')

    count = 0
    for org in organizations:
        logger.info(f'Starting for <{org["domain"]}>')

        tree, org_href = get_organization_page(org["domain"])

        counter = 10
        while True:
            authors = get_authors(tree)

            if authors is None:
                break

            for author in authors:
                author_dict = parse_author(author)

                author_in_mongo = find_one(
                    "author",
                    {"filter": {"id": {"$eq": author_dict["id"]}}}
                )

                if not author_in_mongo:
                    author_dict["organizations"] = [org["domain"]]
                    result = insert_one("author", author_dict)

                    if result is not None:
                        logger.info(f'<{author_dict["name"]}> is inserted!')
                else:
                    update_one(
                        "author",
                        {
                            "filter": {
                                "id": {"$eq": author_dict["id"]}
                            },
                            "update": {
                                "$addToSet": {
                                    "organizations": org["domain"]
                                }
                            }
                        }
                    )

                    logger.info(f'<{author_dict["name"]}> is updated!')

                t_scrape_publications_of_author.apply_async(
                    (author_dict["id"], author_dict["name"])
                )
                count += 1

            tree = get_next_page(tree, counter, org_href)

            counter += 10

            sleep(int(random() * 7))

    return {"status": "ok", "count": count,
            "num_organizations": len_organizations}
