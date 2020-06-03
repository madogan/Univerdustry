from application import celery, loggerfrom application.rests.mongo import findfrom application.utils.decorators import celery_exception_handlerfrom application.tasks.scrape_publications_of_author import \    t_scrape_publications_of_author@celery.task(bind=True, name="publications_scraper", max_retries=3)@celery_exception_handler(ConnectionError)def task_publications_scraper(self):    resd = {"status": "ok"}    authors = find("author")    len_authors = len(authors)    resd["num_authors"] = len_authors    if not authors:        return resd    logger.info(f'# Authors: {len_authors}')    for author in authors:        author_pubs = author.get("publications", [])        author_pubs_in_mongo = find("publication", {            "filter": {"id": {"$not": {"$in": author_pubs}}},            "projection": ["id"]        })        author_pubs_in_mongo = [i["id"] for i in author_pubs_in_mongo]        not_scraped_pubs = [            p for p in author_pubs if p not in author_pubs_in_mongo        ]        len_not_scraped_pubs = len(not_scraped_pubs)        logger.info(f'# New Pubs for {author["name"]}')        if len_not_scraped_pubs > 0:            t_scrape_publications_of_author.apply_async((author["id"],                                                         author["name"]))    return resd