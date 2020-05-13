from random import choice
from cleantext import clean
from scholarly import search_author
from application import celery, logger
from application.utils.helpers import preprocess_text
from application.utils.decorators import celery_exception_handler
from application.rests.mongo import find, find_one, insert_one, update_one
from application.tasks.scrape_publications_of_author import \
    t_scrape_publications_of_author
from application.rests.scholar import (get_authors, get_next_page,
                                       get_organization_page, parse_author)


def get_author(author_name):
    result = dict()

    try:
        author_info = next(search_author(author_name)).fill()
        result["id"] = author_info.id
        result["name"] = author_info.name
        result["affiliation"] = preprocess_text(author_info.affiliation)
        result["citedby"] = author_info.citedby
        result["citedby5y"] = author_info.citedby5y
        result["cites_per_year"] = author_info.cites_per_year
        result["coauthors"] = [c.id for c in author_info.coauthors]
        result["email"] = author_info.email
        result["hindex"] = author_info.hindex
        result["hindex5y"] = author_info.hindex5y
        result["i10index"] = author_info.i10index
        result["i10index5y"] = author_info.i10index5y
        result["publications"] = list(set([
            pub.id_citations.split(":")[1].strip() for pub in
            author_info.publications
        ]))
        result["interests"] = list(map(
            lambda t: clean(t, fix_unicode=True, to_ascii=False, lower=True,
                            no_line_breaks=False, no_urls=True, no_emails=True,
                            no_phone_numbers=True, no_numbers=True,
                            no_digits=True, no_currency_symbols=False,
                            no_punct=True, replace_with_url=" ",
                            replace_with_email=" ",
                            replace_with_phone_number=" ",
                            replace_with_number=" ",
                            replace_with_digit=" "),
            author_info.interests
        ))
    except Exception:
        return None

    return result


@celery.task(bind=True, name="get_author", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_get_author(self, author, org_domain):
    author_in_mongo = find_one(
        "author",
        {"filter": {"id": {"$eq": author["id"]}}}
    )

    if author_in_mongo:
        update_one(
            "author",
            {
                "filter": {
                    "id": {"$eq": author["id"]}
                },
                "update": {
                    "$addToSet": {
                        "organizations": org_domain
                    }
                }
            }
        )
    else:
        scraped_author = get_author(author["name"])

        if scraped_author is not None:
            author = scraped_author

        author["organizations"] = [org_domain]
        result = insert_one("author", author)

        if result is not None:
            logger.info(f'<{author["name"]}> is inserted!')

    t_scrape_publications_of_author.apply_async((author["id"], author["name"]))


@celery.task(bind=True, name="authors_scraper", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_authors_scraper(self):
    organizations = find("organization")  # Get all organizations.

    len_organizations = len(organizations)

    logger.info(f'There are {len_organizations} organizations.')

    proxies = ["http://192.116.142.153:8080", "http://192.241.149.83:80",
               "http://192.241.150.4:80"]

    for org in organizations[20:25]:
        logger.info(f'Starting for <{org["domain"]}>')

        proxy = choice(proxies)

        tree, org_href = get_organization_page(org["domain"], proxy)

        counter = 10
        while True:
            authors = get_authors(tree)

            if authors is None:
                break

            for author in authors[:3]:
                author = parse_author(author)

                logger.info(f'Starting for <{author["name"]}>')

                t_get_author.apply_async((author, org["domain"]))

            proxy = choice(proxies)
            tree = get_next_page(tree, counter, org_href, proxy)

            counter += 10

            break

    return {"status": "ok", "num_organizations": len_organizations}
